from fastapi import APIRouter

from app.models.enums import Visibility
from app.schemas.reports import Report, ReportRequest
from app.services.ai import ai_service
from app.services.repository import repository

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/personal-weekly", response_model=Report)
def personal_weekly(payload: ReportRequest) -> Report:
    events = repository.list_events(user_id=payload.user_id)
    content = ai_service.weekly_report([event.summary for event in events], room=False)
    return repository.create_report(payload.user_id, None, "personal_weekly", content, [event.id for event in events])


@router.post("/room-weekly", response_model=Report)
def room_weekly(payload: ReportRequest) -> Report:
    events = repository.list_events(user_id=payload.user_id, room_id=payload.room_id, viewer_id=payload.user_id)
    allowed = [event for event in events if event.visibility in {Visibility.summary_only, Visibility.room_visible}]
    content = ai_service.weekly_report([event.summary for event in allowed], room=True)
    return repository.create_report(payload.user_id, payload.room_id, "room_weekly", content, [event.id for event in allowed])


@router.get("", response_model=list[Report])
def list_reports(user_id: str = "demo-user") -> list[Report]:
    return repository.list_reports(user_id)
