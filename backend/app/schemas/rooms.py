from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import RoomType, DecisionStatus


class RoomCreate(BaseModel):
    owner_user_id: str = "demo-user"
    name: str = Field(min_length=1, max_length=80)
    room_type: RoomType = RoomType.couple


class Room(BaseModel):
    id: str
    name: str
    room_type: RoomType
    owner_user_id: str
    member_ids: list[str]
    invite_code: str
    created_at: datetime


class JoinRoomRequest(BaseModel):
    user_id: str = "demo-partner"
    invite_code: str


class SharedDecisionCreate(BaseModel):
    room_id: str
    source_event_id: Optional[str] = None
    title: str
    content: str
    owner_user_id: Optional[str] = None
    due_date: Optional[str] = None


class SharedDecision(BaseModel):
    id: str
    room_id: str
    source_event_id: Optional[str] = None
    title: str
    content: str
    owner_user_id: Optional[str] = None
    due_date: Optional[str] = None
    status: DecisionStatus = DecisionStatus.active
    created_at: datetime
