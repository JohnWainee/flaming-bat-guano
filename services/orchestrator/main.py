from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from services.orchestrator import state_store
from services.orchestrator.conversation.state_machine import process_message
from services.orchestrator.vector.client import vector_client
from shared.models import ChatRequest, ChatResponse, ConversationState, EmailRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await vector_client.ensure_collections()
    logger.info("Qdrant collections ready")
    yield


app = FastAPI(title="ServiceNow Assistant API", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    state = await state_store.load_state(request.conversation_id)
    if state is not None and state.user_id != request.user_id:
        state = None
    if state is None:
        state = ConversationState(
            conversation_id=request.conversation_id,
            user_id=request.user_id,
        )

    state, response = await process_message(state, request)
    await state_store.save_state(state)
    return response


@app.post("/email", response_model=ChatResponse)
async def email_intake(request: EmailRequest) -> ChatResponse:
    """Process an inbound email and create a ticket headlessly."""
    chat_request = ChatRequest(
        conversation_id=f"email:{request.message_id}",
        user_id=request.from_address,
        message=f"Subject: {request.subject}\n\n{request.body}",
    )
    state = ConversationState(
        conversation_id=chat_request.conversation_id,
        user_id=chat_request.user_id,
    )
    state, response = await process_message(state, chat_request)

    # Drive the conversation to completion automatically for email (no back-and-forth)
    max_turns = 10
    turns = 0
    while state.stage.value not in ("submitted", "greeting") and turns < max_turns:
        if state.stage.value == "confirm":
            auto_confirm = ChatRequest(
                conversation_id=state.conversation_id,
                user_id=state.user_id,
                message="yes",
            )
            state, response = await process_message(state, auto_confirm)
        elif state.missing_fields:
            break  # Cannot auto-fill missing fields from email
        else:
            break
        turns += 1

    return response


@app.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str) -> dict:
    await state_store.delete_state(conversation_id)
    return {"deleted": conversation_id}
