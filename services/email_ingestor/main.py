from __future__ import annotations

import asyncio
import email
import imaplib
import logging
from email.header import decode_header
from email.utils import parseaddr
from typing import Optional

import httpx

from shared.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def _decode_header_value(value: str) -> str:
    parts = decode_header(value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return " ".join(decoded)


def _extract_body(msg: email.message.Message) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    body += payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                break
    else:
        payload = msg.get_payload(decode=True)
        if isinstance(payload, bytes):
            body = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
    return body.strip()


def _submit_to_orchestrator_sync(from_addr: str, subject: str, body: str, message_id: str) -> Optional[str]:
    with httpx.Client(timeout=60) as client:
        resp = client.post(
            f"{settings.orchestrator_url}/email",
            json={
                "from_address": from_addr,
                "subject": subject,
                "body": body,
                "message_id": message_id,
            },
        )
        resp.raise_for_status()
        return resp.json().get("ticket_number")


def _build_reply_body(ticket_number: Optional[str]) -> str:
    if ticket_number:
        return (
            f"Thank you for contacting IT Support.\n\n"
            f"Your ticket has been created: {ticket_number}\n\n"
            f"You will receive updates as your ticket is worked on.\n\n"
            f"IT Service Desk"
        )
    return (
        "Thank you for contacting IT Support.\n\n"
        "We were unable to automatically create a ticket from your email. "
        "Please provide more details about your issue and we will follow up shortly.\n\n"
        "IT Service Desk"
    )


# ---------------------------------------------------------------------------
# IMAP implementation
# ---------------------------------------------------------------------------

def _imap_send_reply(to_addr: str, subject: str, ticket_number: Optional[str]) -> None:
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(_build_reply_body(ticket_number))
    msg["Subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject
    msg["From"] = settings.email_username
    msg["To"] = to_addr

    try:
        with smtplib.SMTP_SSL(settings.email_host, 465) as smtp:
            smtp.login(settings.email_username, settings.email_password)
            smtp.send_message(msg)
    except Exception as exc:
        logger.warning("Failed to send IMAP reply to %s: %s", to_addr, exc)


def _process_imap() -> None:
    logger.info("Connecting to IMAP server %s:%s", settings.email_host, settings.email_port)
    conn = imaplib.IMAP4_SSL(settings.email_host, settings.email_port)
    conn.login(settings.email_username, settings.email_password)
    conn.select(settings.email_inbox_folder)

    _, msg_ids = conn.search(None, "UNSEEN")
    if not msg_ids or not msg_ids[0]:
        logger.info("No unread messages")
        conn.logout()
        return

    ids = msg_ids[0].split()
    logger.info("Processing %d unread message(s)", len(ids))

    for num in ids:
        try:
            _, data = conn.fetch(num, "(RFC822)")
            raw = data[0][1] if data and data[0] else None
            if not raw:
                continue

            msg = email.message_from_bytes(raw)
            from_addr = parseaddr(msg.get("From", ""))[1]
            subject = _decode_header_value(msg.get("Subject", "(no subject)"))
            message_id = msg.get("Message-ID", str(num))
            body = _extract_body(msg)

            ticket_number = _submit_to_orchestrator_sync(from_addr, subject, body, message_id)
            _imap_send_reply(from_addr, subject, ticket_number)

            conn.copy(num, settings.email_processed_folder)
            conn.store(num, "+FLAGS", "\\Deleted")
            logger.info("Processed email from %s — ticket: %s", from_addr, ticket_number)
        except Exception as exc:
            logger.error("Error processing email %s: %s", num, exc, exc_info=True)

    conn.expunge()
    conn.logout()


# ---------------------------------------------------------------------------
# EWS (Exchange Web Services) implementation
# ---------------------------------------------------------------------------

def _process_ews() -> None:
    try:
        from exchangelib import (
            Account,
            Credentials,
            DELEGATE,
            Mailbox,
        )
        from exchangelib.items import Message as EwsMessage
    except ImportError as exc:
        raise RuntimeError(
            "exchangelib is required for EWS mode. Install it with: pip install exchangelib"
        ) from exc

    logger.info("Connecting to Exchange via EWS for %s", settings.email_username)
    credentials = Credentials(
        username=settings.email_username,
        password=settings.email_password,
    )
    account = Account(
        primary_smtp_address=settings.email_username,
        credentials=credentials,
        autodiscover=True,
        access_type=DELEGATE,
    )

    unread_items = list(account.inbox.filter(is_read=False).only(
        "subject", "sender", "text_body", "message_id",
    ))
    logger.info("Processing %d unread EWS message(s)", len(unread_items))

    processed_folder = None
    try:
        processed_folder = account.root / "Top of Information Store" / settings.email_processed_folder
    except Exception:
        logger.warning("Could not locate processed folder '%s', items will be marked read only", settings.email_processed_folder)

    for item in unread_items:
        try:
            from_addr = item.sender.email_address if item.sender else ""
            subject = item.subject or "(no subject)"
            body = (item.text_body or "").strip()
            message_id = item.message_id or str(item.id)

            ticket_number = _submit_to_orchestrator_sync(from_addr, subject, body, message_id)

            # Reply via EWS
            try:
                reply_msg = EwsMessage(
                    account=account,
                    subject=f"Re: {subject}" if not subject.startswith("Re:") else subject,
                    body=_build_reply_body(ticket_number),
                    to_recipients=[Mailbox(email_address=from_addr)],
                )
                reply_msg.send()
            except Exception as exc:
                logger.warning("Failed to send EWS reply to %s: %s", from_addr, exc)

            item.is_read = True
            item.save()
            if processed_folder:
                item.move(processed_folder)

            logger.info("Processed EWS email from %s — ticket: %s", from_addr, ticket_number)
        except Exception as exc:
            logger.error("Error processing EWS item %s: %s", getattr(item, "id", "?"), exc, exc_info=True)


# ---------------------------------------------------------------------------
# Main poll loop
# ---------------------------------------------------------------------------

async def poll_forever() -> None:
    processor = _process_ews if settings.email_type == "ews" else _process_imap
    loop = asyncio.get_event_loop()
    while True:
        try:
            await loop.run_in_executor(None, processor)
        except Exception as exc:
            logger.error("Email poll error (%s): %s", settings.email_type, exc, exc_info=True)
        await asyncio.sleep(settings.email_poll_interval_seconds)


if __name__ == "__main__":
    asyncio.run(poll_forever())
