from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TicketType(str, Enum):
    INCIDENT = "incident"
    REQUEST = "request"
    CHANGE = "change"
    PROBLEM = "problem"


class ConversationStage(str, Enum):
    GREETING = "greeting"
    CLASSIFY_TYPE = "classify_type"
    COLLECT_FIELDS = "collect_fields"
    CONFIRM = "confirm"
    SUBMITTED = "submitted"


class Message(BaseModel):
    role: str
    content: str


class ConversationState(BaseModel):
    conversation_id: str
    user_id: str
    stage: ConversationStage = ConversationStage.GREETING
    ticket_type: Optional[TicketType] = None
    collected_fields: Dict[str, Any] = Field(default_factory=dict)
    missing_fields: List[str] = Field(default_factory=list)
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    conversation_id: str
    user_id: str
    message: str


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    stage: ConversationStage
    ticket_number: Optional[str] = None


class EmailRequest(BaseModel):
    from_address: str
    subject: str
    body: str
    message_id: str


class TicketDraft(BaseModel):
    ticket_type: TicketType
    fields: Dict[str, Any]


class TicketCreated(BaseModel):
    ticket_number: str
    sys_id: str
    ticket_type: TicketType
    snow_url: Optional[str] = None


class TicketChunk(BaseModel):
    """A chunk of a ServiceNow ticket for vector storage."""
    ticket_number: str
    sys_id: str
    ticket_type: TicketType
    chunk_index: int
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResult(BaseModel):
    ticket_number: str
    sys_id: str
    ticket_type: TicketType
    score: float
    excerpt: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
