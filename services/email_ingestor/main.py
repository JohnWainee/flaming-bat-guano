from __future__ import annotations

import asyncio
import email
import imaplib
import logging
from email.header import decode_header
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


async def _submit_to_orchestrator(from_addr: str, subject: str, body: str, message_id: str) -> Optional[str]:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.orchestrator_url}/email",
            json={
                "from_address": from_addr,
                "subject": subject,
                "body": body,
                "message_id": message_id,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("ticket_number")


def _send_reply(conn: imaplib.IMAP4_SSL, to_addr: str, subject: str, ticket_number: Optional[str]) -> None:
    import smtplib
    from email.mime.text import MIMEText

    if ticket_number:
        reply_body = (
            f"Thank you for contacting IT Support.\n\n"
            f"Your ticket has been created: {ticket_number}\n\n"
            f"You will receive updates as your ticket is worked on.\n\n"
            f"IT Service Desk"
        )
    else:
        reply_body = (
            "Thank you for contacting IT Support.\n\n"
            "We were unable to automatically create a ticket from your email. "
            "Please provide more details about your issue and we will follow up shortly.\n\n"
            "IT Service Desk"
        )

    msg = MIMEText(reply_body)
    msg["Subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject
    msg["From"] = settings.email_username
    msg["To"] = to_addr

    try:
        with smtplib.SMTP_SSL(settings.email_host, 465) as smtp:
            smtp.login(settings.email_username, settings.email_password)
            smtp.send_message(msg)
    except Exception as exc:
        logger.warning("Failed to send reply to %s: %s", to_addr, exc)


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
            from_addr = msg.get("From", "")
            subject = _decode_header_value(msg.get("Subject", "(no subject)"))
            message_id = msg.get("Message-ID", str(num))
            body = _extract_body(msg)

            ticket_number = asyncio.run(_submit_to_orchestrator(from_addr, subject, body, message_id))
            _send_reply(conn, from_addr, subject, ticket_number)

            # Move to processed folder
            conn.copy(num, settings.email_processed_folder)
            conn.store(num, "+FLAGS", "\\Deleted")
            logger.info("Processed email from %s — ticket: %s", from_addr, ticket_number)
        except Exception as exc:
            logger.error("Error processing email %s: %s", num, exc, exc_info=True)

    conn.expunge()
    conn.logout()


async def poll_forever() -> None:
    while True:
        try:
            _process_imap()
        except Exception as exc:
            logger.error("IMAP poll error: %s", exc, exc_info=True)
        await asyncio.sleep(settings.email_poll_interval_seconds)


if __name__ == "__main__":
    asyncio.run(poll_forever())
