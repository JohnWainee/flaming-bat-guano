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

from services.email_ingestor.processing import (
    build_reply_body,
    first_text_block,
    reply_subject,
)

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
    return first_text_block(body)


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


# --------------------------------------------------------------------------- #
# IMAP transport                                                              #
# --------------------------------------------------------------------------- #


def _send_reply_smtp(to_addr: str, subject: str, ticket_number: Optional[str]) -> None:
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(build_reply_body(ticket_number))
    msg["Subject"] = reply_subject(subject)
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
            from_addr = parseaddr(msg.get("From", ""))[1]
            subject = _decode_header_value(msg.get("Subject", "(no subject)"))
            message_id = msg.get("Message-ID", str(num))
            body = _extract_body(msg)

            ticket_number = _submit_to_orchestrator_sync(from_addr, subject, body, message_id)
            _send_reply_smtp(from_addr, subject, ticket_number)

            # Move to processed folder
            conn.copy(num, settings.email_processed_folder)
            conn.store(num, "+FLAGS", "\\Deleted")
            logger.info("Processed email from %s — ticket: %s", from_addr, ticket_number)
        except Exception as exc:
            logger.error("Error processing email %s: %s", num, exc, exc_info=True)

    conn.expunge()
    conn.logout()


# --------------------------------------------------------------------------- #
# Exchange Web Services (EWS) transport                                       #
# --------------------------------------------------------------------------- #


def _ews_account():
    """Build an authenticated exchangelib Account (Autodiscover or explicit host).

    exchangelib is imported lazily so the module can be imported (and the IMAP
    path used) in environments where exchangelib isn't installed.
    """
    from exchangelib import (  # type: ignore
        DELEGATE,
        Account,
        Configuration,
        Credentials,
    )

    smtp_address = settings.ews_primary_smtp_address or settings.email_username
    credentials = Credentials(username=settings.email_username, password=settings.email_password)

    if settings.ews_server:
        config = Configuration(server=settings.ews_server, credentials=credentials)
        return Account(
            primary_smtp_address=smtp_address,
            config=config,
            autodiscover=False,
            access_type=DELEGATE,
        )
    return Account(
        primary_smtp_address=smtp_address,
        credentials=credentials,
        autodiscover=True,
        access_type=DELEGATE,
    )


def _process_ews() -> None:
    logger.info("Connecting to Exchange via EWS for %s", settings.email_username)
    account = _ews_account()

    inbox = account.inbox
    unread = list(inbox.filter(is_read=False))
    if not unread:
        logger.info("No unread messages")
        return

    logger.info("Processing %d unread message(s)", len(unread))

    # Resolve/ensure the processed folder under the inbox.
    processed = None
    for child in inbox.children:
        if child.name == settings.email_processed_folder:
            processed = child
            break

    for item in unread:
        try:
            from_addr = item.sender.email_address if item.sender else ""
            subject = item.subject or "(no subject)"
            message_id = item.message_id or str(item.id)
            body = first_text_block(item.text_body or "")

            ticket_number = _submit_to_orchestrator_sync(from_addr, subject, body, message_id)
            _send_reply_ews(item, subject, ticket_number)

            item.is_read = True
            item.save(update_fields=["is_read"])
            if processed is not None:
                item.move(processed)
            logger.info("Processed email from %s — ticket: %s", from_addr, ticket_number)
        except Exception as exc:
            logger.error("Error processing EWS message: %s", exc, exc_info=True)


def _send_reply_ews(item, subject: str, ticket_number: Optional[str]) -> None:
    try:
        item.reply(subject=reply_subject(subject), body=build_reply_body(ticket_number))
    except Exception as exc:
        sender = item.sender.email_address if getattr(item, "sender", None) else "unknown"
        logger.warning("Failed to send EWS reply to %s: %s", sender, exc)


# --------------------------------------------------------------------------- #
# Dispatch + poll loop                                                        #
# --------------------------------------------------------------------------- #


def _process_once() -> None:
    if settings.email_type == "ews":
        _process_ews()
    else:
        _process_imap()


async def poll_forever() -> None:
    loop = asyncio.get_event_loop()
    logger.info("Email ingestor starting in %s mode", settings.email_type)
    while True:
        try:
            await loop.run_in_executor(None, _process_once)
        except Exception as exc:
            logger.error("%s poll error: %s", settings.email_type.upper(), exc, exc_info=True)
        await asyncio.sleep(settings.email_poll_interval_seconds)


if __name__ == "__main__":
    asyncio.run(poll_forever())
