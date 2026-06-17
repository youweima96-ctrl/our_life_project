from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import ConflictStatus, Visibility


class ConflictCreate(BaseModel):
    event_id: str
    room_id: Optional[str] = None
    creator_id: str = "demo-user"
    user_view: str = Field(min_length=1, max_length=5000)


class PartnerViewCreate(BaseModel):
    partner_id: str = "demo-partner"
    partner_view: str = Field(min_length=1, max_length=5000)


class AIConflictReview(BaseModel):
    shared_facts: list[str] = Field(default_factory=list)
    user_emotions: list[str] = Field(default_factory=list)
    partner_possible_emotions: list[str] = Field(default_factory=list)
    user_needs: list[str] = Field(default_factory=list)
    partner_possible_needs: list[str] = Field(default_factory=list)
    escalation_points: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    suggested_agreements: list[str] = Field(default_factory=list)
    neutral_reframe: str = ""


class ConflictReview(BaseModel):
    id: str
    event_id: str
    room_id: Optional[str] = None
    creator_id: str
    user_view: str
    partner_view: Optional[str] = None
    ai_review_json: Optional[AIConflictReview] = None
    status: ConflictStatus = ConflictStatus.draft
    visibility: Visibility = Visibility.private
    created_at: datetime
    updated_at: datetime
