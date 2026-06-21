"""Unit tests for conversation state machine logic (no LLM/SNOW calls)."""
from __future__ import annotations

import pytest

from services.orchestrator.conversation.field_schemas import (
    REQUIRED_FIELDS,
    display_value,
    normalize_date,
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


class TestDateNormalization:
    def test_iso_date_gets_time_component(self):
        assert normalize_date("2026-07-01") == "2026-07-01 00:00:00"

    def test_iso_datetime_passthrough(self):
        assert normalize_date("2026-07-01 14:30:00") == "2026-07-01 14:30:00"

    def test_iso_datetime_without_seconds(self):
        assert normalize_date("2026-07-01 14:30") == "2026-07-01 14:30:00"

    def test_us_slash_format(self):
        assert normalize_date("07/01/2026") == "2026-07-01 00:00:00"

    def test_month_name_format(self):
        assert normalize_date("July 1, 2026") == "2026-07-01 00:00:00"

    def test_unparseable_passes_through(self):
        # We never silently drop the user's intent.
        assert normalize_date("next Monday") == "next Monday"

    def test_normalize_field_routes_date_fields(self):
        assert normalize_field("start_date", "2026-07-01") == "2026-07-01 00:00:00"
        assert normalize_field("end_date", "2026-07-02") == "2026-07-02 00:00:00"


class TestDisplayValue:
    def test_urgency_label(self):
        assert display_value("urgency", "2") == "High"

    def test_impact_label(self):
        assert display_value("impact", "1") == "Enterprise-wide"

    def test_risk_label(self):
        assert display_value("risk", "3") == "Moderate"

    def test_known_error_bool(self):
        assert display_value("known_error", True) == "Yes"
        assert display_value("known_error", False) == "No"

    def test_change_type_titlecased(self):
        assert display_value("type", "emergency") == "Emergency"

    def test_plain_passthrough(self):
        assert display_value("short_description", "VPN down") == "VPN down"

    def test_unknown_code_passthrough(self):
        assert display_value("urgency", "9") == "9"


class TestUserIntent:
    @pytest.mark.parametrize("text", ["yes", "Yes", "confirm", "looks good", "ok", "submit", "yep", "sure"])
    def test_confirmed(self, text):
        assert _user_confirmed(text)

    @pytest.mark.parametrize("text", ["no", "cancel", "change urgency", "wrong", "edit that"])
    def test_cancelled(self, text):
        assert _user_cancelled(text)

    @pytest.mark.parametrize("text", ["not working", "nothing helps", "notable issue"])
    def test_not_cancelled_by_substring(self, text):
        assert not _user_cancelled(text)


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


class TestChangeAndProblemIntake:
    def test_change_collects_all_required_fields(self):
        state = _make_state(TicketType.CHANGE)
        extracted = {
            "short_description": "Upgrade DB cluster",
            "description": "Apply 14.2 patch to prod Postgres",
            "type": "normal",
            "risk": "moderate",
            "impact": "department",
            "implementation_plan": "Rolling restart",
            "backout_plan": "Restore snapshot",
            "test_plan": "Smoke tests",
            "start_date": "2026-07-01",
            "end_date": "2026-07-02 02:00",
        }
        _apply_extracted(state, extracted)
        assert state.missing_fields == []
        assert state.collected_fields["risk"] == "3"  # normalized
        assert state.collected_fields["impact"] == "2"
        assert state.collected_fields["start_date"] == "2026-07-01 00:00:00"
        assert state.collected_fields["end_date"] == "2026-07-02 02:00:00"

    def test_problem_collects_all_required_fields(self):
        state = _make_state(TicketType.PROBLEM)
        extracted = {
            "short_description": "Recurring VPN drops",
            "description": "VPN disconnects every hour for remote users",
            "impact": "department",
            "urgency": "high",
            "known_error": "yes",
        }
        _apply_extracted(state, extracted)
        assert state.missing_fields == []
        assert state.collected_fields["known_error"] is True
        assert state.collected_fields["urgency"] == "2"

    def test_change_confirmation_is_human_readable(self):
        state = _make_state(TicketType.CHANGE)
        _apply_extracted(state, {"risk": "high", "type": "emergency", "impact": "enterprise-wide"})
        summary = format_confirmation(TicketType.CHANGE, state.collected_fields)
        assert "High" in summary
        assert "Emergency" in summary
        assert "Enterprise-wide" in summary
        assert "Change" in summary

    def test_problem_confirmation_renders_known_error_as_yes(self):
        summary = format_confirmation(
            TicketType.PROBLEM,
            {"short_description": "Recurring outage", "known_error": True},
        )
        assert "Yes" in summary
        assert "True" not in summary


class TestPrompts:
    def test_format_confirmation(self):
        result = format_confirmation(
            TicketType.INCIDENT,
            {"short_description": "VPN issue", "urgency": "2"},
        )
        assert "VPN issue" in result
        assert "Incident" in result
        # Coded value rendered as a readable label, not the raw code.
        assert "High" in result

    def test_field_question(self):
        q = field_question("urgency", TicketType.INCIDENT)
        assert "urgency" in q.lower() or "critical" in q.lower()
