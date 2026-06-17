from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import EventType, Visibility, ReviewStatus, SourceType, AIUserAction


class SafetyFlags(BaseModel):
    self_harm: bool = False
    violence: bool = False
    abuse: bool = False
    financial_risk: bool = False
    medical_risk: bool = False


class AIEventExtraction(BaseModel):
    title: str
    summary: str
    event_type: EventType
    topic_tags: list[str] = Field(default_factory=list)
    emotion_tags: list[str] = Field(default_factory=list)
    need_tags: list[str] = Field(default_factory=list)
    people_involved: list[str] = Field(default_factory=list)
    suggested_visibility: Visibility
    sensitivity_level: str = "medium"
    review_required: bool = True
    follow_up_questions: list[str] = Field(default_factory=list)
    safety_flags: SafetyFlags = Field(default_factory=SafetyFlags)


class DraftEventCreate(BaseModel):
    user_id: str = "demo-user"
    raw_content: str = Field(min_length=1, max_length=5000)
    room_id: Optional[str] = None
    source_type: SourceType = SourceType.text
    scenario: Optional[EventType] = None


class EventConfirm(BaseModel):
    title: str
    summary: str
    event_type: EventType
    topic_tags: list[str] = Field(default_factory=list)
    emotion_tags: list[str] = Field(default_factory=list)
    need_tags: list[str] = Field(default_factory=list)
    visibility: Visibility
    event_time: Optional[datetime] = None
    accuracy_feedback: Optional[str] = None


class LifeEvent(BaseModel):
    id: str
    user_id: str
    room_id: Optional[str] = None
    raw_content: str
    event_type: EventType = EventType.other
    title: str = ""
    summary: str = ""
    topic_tags: list[str] = Field(default_factory=list)
    emotion_tags: list[str] = Field(default_factory=list)
    need_tags: list[str] = Field(default_factory=list)
    visibility: Visibility = Visibility.private
    event_time: datetime
    review_status: ReviewStatus = ReviewStatus.unreviewed
    source_type: SourceType = SourceType.text
    ai_extraction_id: Optional[str] = None
    confirmed: bool = False
    created_at: datetime
    updated_at: datetime


class AIExtractionRecord(BaseModel):
    id: str
    event_id: str
    user_id: str
    raw_content_hash: str
    prompt_version: str
    model_name: str
    output_json: AIEventExtraction
    user_action: AIUserAction = AIUserAction.pending
    accuracy_feedback: Optional[str] = None
    created_at: datetime


class EventDraftResponse(BaseModel):
    event: LifeEvent
    extraction: AIExtractionRecord
