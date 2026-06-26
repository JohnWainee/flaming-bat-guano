from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

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

# Date/datetime fields that ServiceNow expects in "YYYY-MM-DD HH:MM:SS" form.
DATE_FIELDS = {"start_date", "end_date"}

# Input formats we accept from users before converting to the SNOW datetime format.
_DATE_INPUT_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%d",
    "%m/%d/%Y %H:%M",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%B %d %Y",
    "%b %d %Y",
)

_SNOW_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def normalize_date(value: str) -> str:
    """Convert a user-supplied date into ServiceNow's 'YYYY-MM-DD HH:MM:SS' format.

    Returns the original string unchanged if it can't be parsed, so the user's
    intent is never silently dropped — downstream validation/SNOW can surface it.
    """
    raw = str(value).strip()
    for fmt in _DATE_INPUT_FORMATS:
        try:
            parsed = datetime.strptime(raw, fmt)
            return parsed.strftime(_SNOW_DATETIME_FORMAT)
        except ValueError:
            continue
    return raw


def normalize_field(field_name: str, value: str) -> Any:
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
        return KNOWN_ERROR_MAP.get(v, value)
    if field_name in DATE_FIELDS:
        return normalize_date(value)
    return value


# Reverse maps for rendering coded values back to human-readable labels in the
# confirmation summary (e.g. urgency "2" -> "High").
URGENCY_LABELS = {"1": "Critical", "2": "High", "3": "Medium", "4": "Low"}
IMPACT_LABELS = {"1": "Enterprise-wide", "2": "Department", "3": "Individual"}
RISK_LABELS = {"1": "Critical", "2": "High", "3": "Moderate", "4": "Low"}


def display_value(field_name: str, value: Any) -> str:
    """Render a stored (possibly coded) field value as human-readable text."""
    if field_name == "urgency":
        return URGENCY_LABELS.get(str(value), str(value))
    if field_name == "impact":
        return IMPACT_LABELS.get(str(value), str(value))
    if field_name == "risk":
        return RISK_LABELS.get(str(value), str(value))
    if field_name == "type":
        return str(value).title()
    if field_name == "known_error":
        if value is True:
            return "Yes"
        if value is False:
            return "No"
        # Unrecognized value (e.g. an un-normalized string) — surface it as-is
        # rather than silently asserting "No".
        return str(value)
    return str(value)
