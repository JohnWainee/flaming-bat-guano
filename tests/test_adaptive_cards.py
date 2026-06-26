"""Unit tests for Teams Adaptive Card builders."""
from __future__ import annotations

import pytest

from services.teams_bot.cards.confirmation_card import (
    build_confirmation_card,
    build_submitted_card,
    _display_value,
)
from shared.models import TicketType


class TestDisplayValue:
    def test_urgency_display(self):
        assert _display_value("urgency", "1") == "1 - Critical"
        assert _display_value("urgency", "2") == "2 - High"
        assert _display_value("urgency", "3") == "3 - Medium"
        assert _display_value("urgency", "4") == "4 - Low"

    def test_urgency_passthrough_unknown(self):
        assert _display_value("urgency", "urgent") == "urgent"

    def test_impact_display(self):
        assert _display_value("impact", "1") == "1 - Enterprise-wide"
        assert _display_value("impact", "2") == "2 - Department"
        assert _display_value("impact", "3") == "3 - Individual"

    def test_risk_display(self):
        assert _display_value("risk", "1") == "1 - Critical"
        assert _display_value("risk", "3") == "3 - Moderate"

    def test_known_error_true(self):
        assert _display_value("known_error", True) == "Yes"
        assert _display_value("known_error", "true") == "Yes"
        assert _display_value("known_error", "yes") == "Yes"

    def test_known_error_false(self):
        assert _display_value("known_error", False) == "No"
        assert _display_value("known_error", "no") == "No"

    def test_plain_field_passthrough(self):
        assert _display_value("short_description", "VPN not working") == "VPN not working"


class TestBuildConfirmationCard:
    def _make_card(self, ticket_type=TicketType.INCIDENT, fields=None):
        return build_confirmation_card(
            ticket_type=ticket_type,
            fields=fields or {"short_description": "VPN issue", "urgency": "2", "impact": "3"},
            conversation_id="conv-1",
            user_id="user-1",
        )

    def test_card_type(self):
        card = self._make_card()
        assert card["type"] == "AdaptiveCard"

    def test_card_version(self):
        card = self._make_card()
        assert card["version"] == "1.4"

    def test_has_submit_action(self):
        card = self._make_card()
        actions = card["actions"]
        submit = next((a for a in actions if a.get("data", {}).get("action") == "confirm"), None)
        assert submit is not None
        assert submit["style"] == "positive"

    def test_has_edit_action(self):
        card = self._make_card()
        actions = card["actions"]
        edit = next((a for a in actions if a.get("data", {}).get("action") == "edit"), None)
        assert edit is not None

    def test_action_includes_conversation_id(self):
        card = self._make_card()
        for action in card["actions"]:
            assert action["data"]["conversation_id"] == "conv-1"
            assert action["data"]["user_id"] == "user-1"

    def test_facts_include_ticket_type(self):
        card = self._make_card(ticket_type=TicketType.INCIDENT)
        fact_set = next(b for b in card["body"] if b["type"] == "FactSet")
        types = [f["title"] for f in fact_set["facts"]]
        assert "Ticket Type" in types

    def test_incident_type_value(self):
        card = self._make_card(ticket_type=TicketType.INCIDENT)
        fact_set = next(b for b in card["body"] if b["type"] == "FactSet")
        ticket_fact = next(f for f in fact_set["facts"] if f["title"] == "Ticket Type")
        assert ticket_fact["value"] == "Incident"

    def test_urgency_expanded_in_facts(self):
        card = self._make_card(fields={"urgency": "2"})
        fact_set = next(b for b in card["body"] if b["type"] == "FactSet")
        urgency_fact = next((f for f in fact_set["facts"] if "High" in f["value"]), None)
        assert urgency_fact is not None

    def test_change_ticket_type(self):
        card = self._make_card(
            ticket_type=TicketType.CHANGE,
            fields={"short_description": "Patch servers", "type": "normal"},
        )
        fact_set = next(b for b in card["body"] if b["type"] == "FactSet")
        ticket_fact = next(f for f in fact_set["facts"] if f["title"] == "Ticket Type")
        assert ticket_fact["value"] == "Change"


class TestBuildSubmittedCard:
    def test_card_type(self):
        card = build_submitted_card("INC0001234")
        assert card["type"] == "AdaptiveCard"

    def test_ticket_number_in_body(self):
        card = build_submitted_card("INC0001234")
        # The ticket number should appear somewhere in the card body
        body_text = str(card)
        assert "INC0001234" in body_text

    def test_no_url_action_when_no_url(self):
        card = build_submitted_card("INC0001234")
        assert card["actions"] == []

    def test_url_action_when_snow_url_provided(self):
        card = build_submitted_card("INC0001234", snow_url="https://example.service-now.com/nav_to.do")
        assert len(card["actions"]) == 1
        assert card["actions"][0]["type"] == "Action.OpenUrl"
        assert "example.service-now.com" in card["actions"][0]["url"]


class TestChatResponseFields:
    """Verify ChatResponse model accepts the new ticket_type and collected_fields."""

    def test_chat_response_accepts_ticket_fields(self):
        from shared.models import ChatResponse, ConversationStage, TicketType

        resp = ChatResponse(
            conversation_id="c1",
            reply="Does this look right?",
            stage=ConversationStage.CONFIRM,
            ticket_type=TicketType.INCIDENT,
            collected_fields={"short_description": "VPN issue", "urgency": "2"},
        )
        assert resp.ticket_type == TicketType.INCIDENT
        assert resp.collected_fields["urgency"] == "2"

    def test_chat_response_ticket_fields_optional(self):
        from shared.models import ChatResponse, ConversationStage

        resp = ChatResponse(
            conversation_id="c1",
            reply="Hello",
            stage=ConversationStage.GREETING,
        )
        assert resp.ticket_type is None
        assert resp.collected_fields is None
