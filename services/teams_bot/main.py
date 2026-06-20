from __future__ import annotations

import logging
from http import HTTPStatus

import httpx
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity

from shared.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

adapter_settings = BotFrameworkAdapterSettings(
    app_id=settings.microsoft_app_id,
    app_password=settings.microsoft_app_password,
)
adapter = BotFrameworkAdapter(adapter_settings)


async def on_error(context: TurnContext, error: Exception) -> None:
    logger.error("Unhandled error in bot turn: %s", error, exc_info=True)
    await context.send_activity("Sorry, something went wrong. Please try again.")


adapter.on_turn_error = on_error


async def _call_orchestrator(conversation_id: str, user_id: str, message: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.orchestrator_url}/chat",
            json={"conversation_id": conversation_id, "user_id": user_id, "message": message},
        )
        resp.raise_for_status()
        return resp.json()["reply"]


async def handle_message(turn_context: TurnContext) -> None:
    activity = turn_context.activity
    user_text = (activity.text or "").strip()
    if not user_text:
        return

    conversation_id = activity.conversation.id
    user_id = activity.from_property.id if activity.from_property else "unknown"

    reply_text = await _call_orchestrator(conversation_id, user_id, user_text)
    await turn_context.send_activity(reply_text)


async def messages(request: web.Request) -> web.Response:
    if "application/json" not in request.content_type:
        return web.Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    body = await request.json()
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    try:
        if activity.type == "message":
            await adapter.process_activity(activity, auth_header, handle_message)
        else:
            await adapter.process_activity(activity, auth_header, _noop)
    except Exception as exc:
        logger.error("Error processing activity: %s", exc, exc_info=True)
        return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return web.Response(status=HTTPStatus.OK)


async def _noop(_ctx: TurnContext) -> None:
    pass


async def _health(_request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


app = web.Application()
app.router.add_post("/api/messages", messages)
app.router.add_get("/health", _health)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=3978)
