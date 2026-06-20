"""Unit tests for conversation state machine logic (no LLM/SNOW calls)."""
from __future__ import annotations

import pytest

from services.orchestrator.conversation.field_schemas import (
    REQUIRED_FIELDS,
    normalize_field,
)
from services.orchestrator.conversation.state_machine import _user_confirmed, _user_cancelled, _apply_extracted
from services.orchestrator.llm.prompts import format_confirmation, field_question
from shared.models import ConversationState, ConversationStage, TicketType


def _make_state(ticket_type: TicketType) -> ConversationState:
    state = ConversationState(conversation_id="test-1", user_id="user-1")
    state.ticket_type = ticket_type
    state.missing_fields = list(REQUIRED_FIELDS[ticket_type])
    state.stage = ConversationStage.COLLECT_FIELDS
    return state


class TestFieldNormalization:
    def test_urgency_text(self):
        assert normalize_field("urgency", "critical") == "1"
        assert normalize_field("urgency", "high") == "2"
        assert normalize_field("urgency", "medium") == "3"
        assert normalize_field("urgency", "low") == "4"

    def test_urgency_numeric(self):
        assert normalize_field("urgency", "1") == "1"

    def test_impact(self):
        assert normalize_field("impact", "enterprise-wide") == "1"
        assert normalize_field("impact", "department") == "2"
        assert normalize_field("impact", "individual") == "3"

    def test_change_type(self):
        assert normalize_field("type", "normal") == "normal"
        assert normalize_field("type", "emergency") == "emergency"

    def test_known_error_bool(self):
        assert normalize_field("known_error", "yes") is True
        assert normalize_field("known_error", "no") is False

    def test_passthrough(self):
        assert normalize_field("short_description", "My laptop is broken") == "My laptop is broken"


class TestUserIntent:
    @pytest.mark.parametrize("text", ["yes", "Yes", "confirm", "looks good", "ok", "submit", "yep", "sure"])
    def test_confirmed(self, text):
        assert _user_confirmed(text)

    @pytest.mark.parametrize("text", ["no", "cancel", "change urgency", "wrong", "edit that"])
    def test_cancelled(self, text):
        assert _user_cancelled(text)


class TestRequiredFields:
    def test_incident_has_core_fields(self):
        fields = REQUIRED_FIELDS[TicketType.INCIDENT]
        assert "short_description" in fields
        assert "urgency" in fields
        assert "impact" in fields

    def test_change_has_planning_fields(self):
        fields = REQUIRED_FIELDS[TicketType.CHANGE]
        assert "implementation_plan" in fields
        assert "backout_plan" in fields
        assert "start_date" in fields

    def test_all_types_have_description(self):
        for ticket_type in TicketType:
            assert "short_description" in REQUIRED_FIELDS[ticket_type]
            assert "description" in REQUIRED_FIELDS[ticket_type]


class TestApplyExtracted:
    def test_fills_missing_fields(self):
        state = _make_state(TicketType.INCIDENT)
        extracted = {"short_description": "VPN not connecting", "urgency": "high"}
        _apply_extracted(state, extracted)
        assert state.collected_fields["short_description"] == "VPN not connecting"
        assert state.collected_fields["urgency"] == "2"  # normalized
        assert "short_description" not in state.missing_fields
        assert "urgency" not in state.missing_fields

    def test_ignores_unknown_fields(self):
        state = _make_state(TicketType.INCIDENT)
        extracted = {"short_description": "Issue", "nonexistent_field": "value"}
        _apply_extracted(state, extracted)
        assert "nonexistent_field" not in state.collected_fields

    def test_replace_mode(self):
        state = _make_state(TicketType.INCIDENT)
        state.collected_fields["urgency"] = "1"
        extracted = {"urgency": "low"}
        _apply_extracted(state, extracted, replace=True)
        assert state.collected_fields["urgency"] == "4"


class TestPrompts:
    def test_format_confirmation(self):
        result = format_confirmation(
            TicketType.INCIDENT,
            {"short_description": "VPN issue", "urgency": "2"},
        )
        assert "VPN issue" in result
        assert "Incident" in result

    def test_field_question(self):
        q = field_question("urgency", TicketType.INCIDENT)
        assert "urgency" in q.lower() or "critical" in q.lower()
