from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from shared.models import (
    ChatRequest,
    ChatResponse,
    ConversationStage,
    ConversationState,
    Message,
    TicketType,
)

from services.orchestrator.conversation.field_schemas import (
    REQUIRED_FIELDS,
    normalize_field,
)
from services.orchestrator.llm.prompts import (
    CLASSIFY_PROMPT,
    SYSTEM_PROMPT,
    field_question,
    format_confirmation,
)

logger = logging.getLogger(__name__)

_CLASSIFY_CONFIDENCE_THRESHOLD = 0.6


def _llm():
    from services.orchestrator.llm import client as llm
    return llm


def _snow():
    from services.orchestrator.snow.client import snow_client
    return snow_client


def _vector():
    from services.orchestrator.vector.client import vector_client
    return vector_client


async def _classify_type(text: str) -> tuple[Optional[TicketType], float]:
    llm = _llm()
    response = await llm.chat_complete(
        messages=[
            {"role": "system", "content": CLASSIFY_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.0,
        max_tokens=128,
    )
    try:
        data = json.loads(response.content or "{}")
        raw_type = data.get("ticket_type", "").lower()
        confidence = float(data.get("confidence", 0.0))
        ticket_type = TicketType(raw_type) if raw_type in TicketType._value2member_map_ else None
        return ticket_type, confidence
    except (json.JSONDecodeError, ValueError):
        return None, 0.0


async def _extract_fields(user_text: str, ticket_type: TicketType, missing: List[str]) -> Dict[str, Any]:
    llm = _llm()
    field_list = ", ".join(missing)
    prompt = (
        f"Extract the following fields from the user message if present: {field_list}.\n"
        f"Ticket type: {ticket_type.value}\n"
        f"User message: {user_text}\n\n"
        "Return JSON only with keys matching the field names above. "
        "Omit any field not clearly present in the message. "
        'Example: {"short_description": "My laptop won\'t turn on"}'
    )
    response = await llm.chat_complete(
        messages=[
            {"role": "system", "content": "You are a precise data extraction assistant. Return valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=512,
    )
    try:
        return json.loads(response.content or "{}")
    except json.JSONDecodeError:
        return {}


async def _generate_reply(state: ConversationState, next_field: Optional[str]) -> str:
    llm = _llm()
    context = (
        f"Ticket type: {state.ticket_type.value if state.ticket_type else 'unknown'}\n"
        f"Collected fields: {list(state.collected_fields.keys())}\n"
        f"Next field needed: {next_field or 'none'}"
    )
    history = [{"role": m.role, "content": m.content} for m in state.messages[-6:]]
    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context}] + history
    if next_field:
        messages.append({
            "role": "user",
            "content": f"Ask the user for: {field_question(next_field, state.ticket_type)}",
        })
        response = await llm.chat_complete(messages, temperature=0.3, max_tokens=256)
        return response.content or field_question(next_field, state.ticket_type)
    return "I have all the information I need."


async def process_message(state: ConversationState, request: ChatRequest) -> tuple[ConversationState, ChatResponse]:
    user_text = request.message.strip()
    state.messages.append(Message(role="user", content=user_text))

    reply = ""
    ticket_number = None

    if state.stage == ConversationStage.GREETING:
        state.stage = ConversationStage.CLASSIFY_TYPE
        ticket_type, confidence = await _classify_type(user_text)

        if ticket_type and confidence >= _CLASSIFY_CONFIDENCE_THRESHOLD:
            state.ticket_type = ticket_type
            state.missing_fields = list(REQUIRED_FIELDS[ticket_type])
            state.stage = ConversationStage.COLLECT_FIELDS
            extracted = await _extract_fields(user_text, ticket_type, state.missing_fields)
            _apply_extracted(state, extracted)
        else:
            reply = (
                "I can help you create a ServiceNow ticket. What type do you need?\n"
                "- **Incident** — something is broken or not working\n"
                "- **Request** — access, software, hardware, or a service\n"
                "- **Change** — planned modification to IT systems\n"
                "- **Problem** — root cause investigation of recurring issues"
            )

    elif state.stage == ConversationStage.CLASSIFY_TYPE:
        ticket_type, confidence = await _classify_type(user_text)
        if ticket_type:
            state.ticket_type = ticket_type
            state.missing_fields = list(REQUIRED_FIELDS[ticket_type])
            state.stage = ConversationStage.COLLECT_FIELDS
            extracted = await _extract_fields(user_text, ticket_type, state.missing_fields)
            _apply_extracted(state, extracted)
        else:
            reply = "I didn't catch the ticket type. Please choose: Incident, Request, Change, or Problem."

    elif state.stage == ConversationStage.COLLECT_FIELDS:
        assert state.ticket_type is not None
        extracted = await _extract_fields(user_text, state.ticket_type, state.missing_fields)
        _apply_extracted(state, extracted)

        if not state.missing_fields:
            state.stage = ConversationStage.CONFIRM

    elif state.stage == ConversationStage.CONFIRM:
        if _user_confirmed(user_text):
            assert state.ticket_type is not None
            try:
                created = await _snow().create_ticket(state.ticket_type, state.collected_fields)
                ticket_number = created.ticket_number
                state.stage = ConversationStage.SUBMITTED
                reply = (
                    f"Your ticket has been created successfully!\n\n"
                    f"**Ticket Number:** {created.ticket_number}\n"
                    f"You can track it here: {created.snow_url or 'your ServiceNow portal'}"
                )
            except Exception as exc:
                logger.error("Failed to create ticket: %s", exc)
                reply = "I encountered an error submitting the ticket. Please try again or contact IT directly."
        else:
            extracted = await _extract_fields(user_text, state.ticket_type, list(REQUIRED_FIELDS[state.ticket_type]))
            _apply_extracted(state, extracted, replace=True)

    if not reply:
        if state.stage == ConversationStage.COLLECT_FIELDS and state.missing_fields:
            next_field = state.missing_fields[0]
            if "short_description" in state.collected_fields and len(state.collected_fields) == 1:
                similar = await _fetch_similar_suggestion(state.collected_fields["short_description"])
                if similar:
                    reply = similar + "\n\n" + await _generate_reply(state, next_field)
                else:
                    reply = await _generate_reply(state, next_field)
            else:
                reply = await _generate_reply(state, next_field)
        elif state.stage == ConversationStage.CONFIRM:
            reply = format_confirmation(state.ticket_type, state.collected_fields)

    state.messages.append(Message(role="assistant", content=reply))
    return state, ChatResponse(
        conversation_id=state.conversation_id,
        reply=reply,
        stage=state.stage,
        ticket_number=ticket_number,
        ticket_type=state.ticket_type if state.stage == ConversationStage.CONFIRM else None,
        collected_fields=dict(state.collected_fields) if state.stage == ConversationStage.CONFIRM else None,
    )


def _apply_extracted(state: ConversationState, extracted: Dict[str, Any], replace: bool = False) -> None:
    for field, value in extracted.items():
        if field in (state.missing_fields if not replace else REQUIRED_FIELDS.get(state.ticket_type, [])):
            normalized = normalize_field(field, str(value))
            state.collected_fields[field] = normalized
            if field in state.missing_fields:
                state.missing_fields.remove(field)


def _user_confirmed(text: str) -> bool:
    t = text.strip().lower()
    return any(t.startswith(w) for w in ("yes", "confirm", "correct", "submit", "looks good", "ok", "yep", "sure"))


def _user_cancelled(text: str) -> bool:
    words = set(text.strip().lower().split())
    return bool(words & {"no", "cancel", "wrong", "edit", "update", "change"})


async def _fetch_similar_suggestion(description: str) -> Optional[str]:
    try:
        results = await _vector().search_similar(description, limit=1)
        if results:
            r = results[0]
            if r.score > 0.85:
                return (
                    f"Heads up — I found a similar past {r.ticket_type.value}: **{r.ticket_number}**. "
                    f"You may want to check if that covers your issue first."
                )
    except Exception:
        pass
    return None
