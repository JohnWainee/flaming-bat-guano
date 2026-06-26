from __future__ import annotations

import json
import logging
from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, Attachment

from shared.config import settings
from shared.models import TicketType
from services.teams_bot.cards.confirmation_card import build_confirmation_card, build_submitted_card

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


async def _call_orchestrator(conversation_id: str, user_id: str, message: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.orchestrator_url}/chat",
            json={"conversation_id": conversation_id, "user_id": user_id, "message": message},
        )
        resp.raise_for_status()
        return resp.json()


def _adaptive_card_attachment(card_body: Dict[str, Any]) -> Attachment:
    return Attachment(
        content_type="application/vnd.microsoft.card.adaptive",
        content=card_body,
    )


async def handle_message(turn_context: TurnContext) -> None:
    activity = turn_context.activity

    # Adaptive Card action submissions arrive as activity.value (dict), not activity.text
    user_text: Optional[str] = None
    if activity.value and isinstance(activity.value, dict):
        card_action = activity.value.get("action")
        if card_action == "confirm":
            user_text = "yes"
        elif card_action == "edit":
            user_text = "I want to make a change"
        else:
            user_text = json.dumps(activity.value)
    else:
        user_text = (activity.text or "").strip()

    if not user_text:
        return

    conversation_id = activity.conversation.id
    user_id = activity.from_property.id if activity.from_property else "unknown"

    response = await _call_orchestrator(conversation_id, user_id, user_text)
    reply_text = response.get("reply", "")
    stage = response.get("stage", "")
    ticket_number = response.get("ticket_number")

    if stage == "submitted" and ticket_number:
        snow_url = None  # orchestrator doesn't surface it here; would need to extend model
        card = build_submitted_card(ticket_number=ticket_number, snow_url=snow_url)
        reply = turn_context.activity.create_reply()
        reply.text = reply_text
        reply.attachments = [_adaptive_card_attachment(card)]
        await turn_context.send_activity(reply)

    elif stage == "confirm" and response.get("ticket_type") and response.get("collected_fields"):
        try:
            card = build_confirmation_card(
                ticket_type=TicketType(response["ticket_type"]),
                fields=response["collected_fields"],
                conversation_id=conversation_id,
                user_id=user_id,
            )
            reply = turn_context.activity.create_reply()
            reply.text = reply_text
            reply.attachments = [_adaptive_card_attachment(card)]
            await turn_context.send_activity(reply)
        except Exception as exc:
            logger.warning("Adaptive Card build failed, falling back to text: %s", exc)
            await turn_context.send_activity(reply_text)

    else:
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
