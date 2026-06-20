"""Unit tests for the ingestion pipeline chunking logic."""
from __future__ import annotations

import pytest

from services.ingestion_pipeline.main import _chunk_text, _record_to_text
from shared.models import TicketType


class TestChunking:
    def test_short_text_single_chunk(self):
        text = "This is a short description."
        chunks = _chunk_text(text, max_chars=500)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_long_text_split(self):
        text = "A" * 2000
        chunks = _chunk_text(text, max_chars=400)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 400

    def test_split_on_newline_boundary(self):
        text = ("word " * 80 + "\n") * 5
        chunks = _chunk_text(text, max_chars=400)
        for chunk in chunks:
            assert len(chunk) <= 400

    def test_no_empty_chunks(self):
        text = "Hello world\n\n\nThis is a test\n"
        chunks = _chunk_text(text, max_chars=200)
        assert all(c.strip() for c in chunks)


class TestRecordToText:
    def test_basic_incident(self):
        record = {
            "short_description": "VPN not working",
            "description": "Users cannot connect to VPN",
            "work_notes": "Restarted VPN gateway",
            "close_notes": "Gateway restart resolved the issue",
        }
        text = _record_to_text(record, TicketType.INCIDENT)
        assert "VPN not working" in text
        assert "Users cannot connect" in text
        assert "Restarted VPN gateway" in text

    def test_empty_fields_excluded(self):
        record = {
            "short_description": "Test",
            "description": "",
            "work_notes": None,
        }
        text = _record_to_text(record, TicketType.INCIDENT)
        assert "Test" in text
        assert "None" not in text

    def test_change_includes_plans(self):
        record = {
            "short_description": "Deploy patch",
            "description": "Monthly patching cycle",
            "implementation_plan": "Run ansible playbook",
            "backout_plan": "Restore from snapshot",
            "test_plan": "Run smoke tests",
        }
        text = _record_to_text(record, TicketType.CHANGE)
        assert "ansible" in text
        assert "snapshot" in text
