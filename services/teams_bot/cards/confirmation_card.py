from __future__ import annotations

from typing import Any, Dict, Optional

from services.orchestrator.llm.prompts import FIELD_LABELS
from shared.models import TicketType


_URGENCY_DISPLAY = {"1": "1 - Critical", "2": "2 - High", "3": "3 - Medium", "4": "4 - Low"}
_IMPACT_DISPLAY = {"1": "1 - Enterprise-wide", "2": "2 - Department", "3": "3 - Individual"}
_RISK_DISPLAY = {"1": "1 - Critical", "2": "2 - High", "3": "3 - Moderate", "4": "4 - Low"}


def _display_value(field: str, value: Any) -> str:
    v = str(value)
    if field == "urgency":
        return _URGENCY_DISPLAY.get(v, v)
    if field == "impact":
        return _IMPACT_DISPLAY.get(v, v)
    if field == "risk":
        return _RISK_DISPLAY.get(v, v)
    if field == "known_error":
        return "Yes" if value is True or v.lower() in ("true", "yes") else "No"
    return v


def build_confirmation_card(
    ticket_type: TicketType,
    fields: Dict[str, Any],
    conversation_id: str,
    user_id: str,
) -> Dict[str, Any]:
    """Build an Adaptive Card for the CONFIRM stage."""
    facts = [{"title": "Ticket Type", "value": ticket_type.value.title()}]
    for field, value in fields.items():
        label = FIELD_LABELS.get(field, field.replace("_", " ").title())
        facts.append({"title": label.split(" (")[0].title(), "value": _display_value(field, value)})

    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "Container",
                "style": "emphasis",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "Ticket Ready to Submit",
                        "weight": "Bolder",
                        "size": "Medium",
                        "color": "Accent",
                    }
                ],
            },
            {
                "type": "FactSet",
                "facts": facts,
                "separator": True,
            },
            {
                "type": "TextBlock",
                "text": "Does everything look correct?",
                "wrap": True,
                "spacing": "Medium",
            },
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Submit Ticket",
                "style": "positive",
                "data": {
                    "action": "confirm",
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                },
            },
            {
                "type": "Action.Submit",
                "title": "Make Changes",
                "style": "default",
                "data": {
                    "action": "edit",
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                },
            },
        ],
    }


def build_submitted_card(ticket_number: str, snow_url: Optional[str] = None) -> Dict[str, Any]:
    """Adaptive Card shown after successful ticket creation."""
    url_action = []
    if snow_url:
        url_action = [
            {
                "type": "Action.OpenUrl",
                "title": "View in ServiceNow",
                "url": snow_url,
            }
        ]

    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "Container",
                "style": "good",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "Ticket Created Successfully",
                        "weight": "Bolder",
                        "size": "Medium",
                        "color": "Good",
                    },
                    {
                        "type": "TextBlock",
                        "text": f"Your ticket number is **{ticket_number}**.",
                        "wrap": True,
                    },
                ],
            }
        ],
        "actions": url_action,
    }
