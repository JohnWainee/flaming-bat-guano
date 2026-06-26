"""Transport-agnostic helpers for the email ingestor.

Kept free of third-party dependencies (no httpx/imaplib/exchangelib) so the
pure logic — reply text, subject handling, body cleanup — can be unit tested
without standing up a mail server or installing the transport libraries.
"""
from __future__ import annotations

from typing import Optional

_REPLY_SUCCESS = (
    "Thank you for contacting IT Support.\n\n"
    "Your ticket has been created: {ticket_number}\n\n"
    "You will receive updates as your ticket is worked on.\n\n"
    "IT Service Desk"
)

_REPLY_FAILURE = (
    "Thank you for contacting IT Support.\n\n"
    "We were unable to automatically create a ticket from your email. "
    "Please provide more details about your issue and we will follow up shortly.\n\n"
    "IT Service Desk"
)


def build_reply_body(ticket_number: Optional[str]) -> str:
    """Compose the auto-reply body for a processed inbound email."""
    if ticket_number:
        return _REPLY_SUCCESS.format(ticket_number=ticket_number)
    return _REPLY_FAILURE


def reply_subject(subject: str) -> str:
    """Prefix the subject with 'Re:' unless it already has one (case-insensitive)."""
    subject = (subject or "").strip()
    if subject.lower().startswith("re:"):
        return subject
    return f"Re: {subject}" if subject else "Re: (no subject)"


def first_text_block(text: str) -> str:
    """Normalize a plain-text body: strip surrounding whitespace.

    Both the IMAP and EWS paths funnel their extracted plain-text body through
    here so downstream submission sees consistent input.
    """
    return (text or "").strip()
