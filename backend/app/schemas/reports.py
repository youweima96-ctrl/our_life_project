from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReportRequest(BaseModel):
    user_id: str = "demo-user"
    room_id: Optional[str] = None


class Report(BaseModel):
    id: str
    user_id: str
    room_id: Optional[str] = None
    report_type: str
    content_markdown: str
    source_event_ids: list[str]
    created_at: datetime
