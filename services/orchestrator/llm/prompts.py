from __future__ import annotations

from shared.models import TicketType

SYSTEM_PROMPT = """You are a helpful IT service desk assistant that guides users through creating ServiceNow tickets.

Your job is to:
1. Understand what kind of IT issue or request the user has
2. Collect all required information conversationally and naturally
3. Confirm the details before submitting

Rules:
- Be concise and friendly. Ask for one piece of information at a time.
- If the user's message contains multiple pieces of information, extract all of them.
- Never make up information the user hasn't provided.
- For urgency/impact/priority fields, explain the options if the user seems unsure.
- If the user asks about a previous or similar issue, note it but still collect required fields.
- Keep responses under 3 sentences unless explaining options."""

CLASSIFY_PROMPT = """Based on the user's message, determine what type of ServiceNow ticket to create.

Ticket types:
- incident: Something is broken, not working, or causing disruption (outages, errors, degraded performance)
- request: Requesting access, software, hardware, a service, or a change for the user's benefit
- change: A planned modification to IT systems, infrastructure, or services (requires approval workflow)
- problem: Investigating the root cause of recurring incidents or known errors

Respond with JSON only: {{"ticket_type": "<incident|request|change|problem>", "confidence": <0.0-1.0>, "reasoning": "<brief>"}}"""

CONFIRM_TEMPLATE = """Here's a summary of the ticket I'll create for you:

**Type:** {ticket_type}
{fields_summary}

Does this look correct? Reply **yes** to submit, or tell me what to change."""

FIELD_LABELS: dict[str, str] = {
    "short_description": "brief summary",
    "description": "detailed description",
    "urgency": "urgency (1=Critical, 2=High, 3=Medium, 4=Low)",
    "impact": "business impact (1=Enterprise-wide, 2=Department, 3=Individual)",
    "category": "category",
    "subcategory": "subcategory",
    "requested_for": "who this request is for",
    "request_type": "type of request",
    "risk": "risk level (1=Critical, 2=High, 3=Moderate, 4=Low)",
    "type": "change type (normal, standard, or emergency)",
    "implementation_plan": "implementation plan",
    "backout_plan": "backout/rollback plan",
    "test_plan": "test plan",
    "start_date": "planned start date",
    "end_date": "planned end date",
    "known_error": "is this a known error? (yes/no)",
}


def field_question(field_name: str, ticket_type: TicketType) -> str:
    label = FIELD_LABELS.get(field_name, field_name.replace("_", " "))
    return f"Could you provide the {label}?"


def format_confirmation(ticket_type: TicketType, fields: dict) -> str:
    lines = []
    for k, v in fields.items():
        label = FIELD_LABELS.get(k, k.replace("_", " ").title())
        lines.append(f"**{label}:** {v}")
    return CONFIRM_TEMPLATE.format(
        ticket_type=ticket_type.value.title(),
        fields_summary="\n".join(lines),
    )
