from __future__ import annotations

from typing import Dict, List

from shared.models import TicketType

# Required fields per ticket type (in preferred collection order)
REQUIRED_FIELDS: Dict[TicketType, List[str]] = {
    TicketType.INCIDENT: [
        "short_description",
        "description",
        "urgency",
        "impact",
    ],
    TicketType.REQUEST: [
        "short_description",
        "description",
        "requested_for",
    ],
    TicketType.CHANGE: [
        "short_description",
        "description",
        "type",
        "risk",
        "impact",
        "implementation_plan",
        "backout_plan",
        "test_plan",
        "start_date",
        "end_date",
    ],
    TicketType.PROBLEM: [
        "short_description",
        "description",
        "impact",
        "urgency",
        "known_error",
    ],
}

# Field value normalization helpers
URGENCY_MAP = {
    "critical": "1", "high": "2", "medium": "3", "low": "4",
    "1": "1", "2": "2", "3": "3", "4": "4",
}
IMPACT_MAP = {
    "enterprise": "1", "enterprise-wide": "1", "department": "2", "individual": "3",
    "1": "1", "2": "2", "3": "3",
}
CHANGE_TYPE_MAP = {
    "normal": "normal", "standard": "standard", "emergency": "emergency",
}
RISK_MAP = {
    "critical": "1", "high": "2", "moderate": "3", "medium": "3", "low": "4",
    "1": "1", "2": "2", "3": "3", "4": "4",
}
KNOWN_ERROR_MAP = {
    "yes": True, "y": True, "true": True, "no": False, "n": False, "false": False,
}


def normalize_field(field_name: str, value: str) -> str | bool:
    v = str(value).strip().lower()
    if field_name == "urgency":
        return URGENCY_MAP.get(v, value)
    if field_name == "impact":
        return IMPACT_MAP.get(v, value)
    if field_name == "type":
        return CHANGE_TYPE_MAP.get(v, value)
    if field_name == "risk":
        return RISK_MAP.get(v, value)
    if field_name == "known_error":
        return KNOWN_ERROR_MAP.get(v, False)
    return value
