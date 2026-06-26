"""Unit tests for the email ingestor's transport-agnostic helpers.

These cover the pure logic shared by the IMAP and EWS paths without importing
the transport libraries (httpx/imaplib/exchangelib), so they run with only
stdlib + pytest available.
"""
from __future__ import annotations

from services.email_ingestor.processing import (
    build_reply_body,
    first_text_block,
    reply_subject,
)


class TestBuildReplyBody:
    def test_success_includes_ticket_number(self):
        body = build_reply_body("INC0012345")
        assert "INC0012345" in body
        assert "created" in body.lower()

    def test_failure_when_no_ticket(self):
        body = build_reply_body(None)
        assert "unable to automatically create" in body.lower()
        # Must not claim a ticket was created.
        assert "created:" not in body.lower()

    def test_empty_string_treated_as_failure(self):
        # An empty ticket number is falsy — no ticket was created.
        assert build_reply_body("") == build_reply_body(None)


class TestReplySubject:
    def test_adds_prefix(self):
        assert reply_subject("VPN is down") == "Re: VPN is down"

    def test_does_not_double_prefix(self):
        assert reply_subject("Re: VPN is down") == "Re: VPN is down"

    def test_prefix_is_case_insensitive(self):
        assert reply_subject("RE: VPN is down") == "RE: VPN is down"

    def test_strips_whitespace(self):
        assert reply_subject("  VPN is down  ") == "Re: VPN is down"

    def test_empty_subject(self):
        assert reply_subject("") == "Re: (no subject)"


class TestFirstTextBlock:
    def test_strips_surrounding_whitespace(self):
        assert first_text_block("\n  hello world \n") == "hello world"

    def test_handles_none(self):
        assert first_text_block(None) == ""

    def test_preserves_internal_newlines(self):
        assert first_text_block("line1\nline2\n") == "line1\nline2"
