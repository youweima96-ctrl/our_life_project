from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.core.config import get_settings
from app.schemas.events import DraftEventCreate, EventConfirm, EventDraftResponse, LifeEvent
from app.services.ai import ai_service, content_hash
from app.services.repository import repository

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/draft", response_model=EventDraftResponse)
def create_draft(payload: DraftEventCreate) -> EventDraftResponse:
    settings = get_settings()
    event = repository.create_draft_event(payload)
    extraction = ai_service.extract_event(payload.raw_content, payload.scenario)
    record = repository.add_extraction(
        event=event,
        extraction=extraction,
        raw_content_hash=content_hash(payload.raw_content),
        prompt_version=settings.prompt_version,
        model_name=settings.model_name,
    )
    return EventDraftResponse(event=repository.must_get_event(event.id), extraction=record)


@router.post("/{event_id}/extract", response_model=EventDraftResponse)
def extract_event(event_id: str) -> EventDraftResponse:
    settings = get_settings()
    try:
        event = repository.must_get_event(event_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    extraction = ai_service.extract_event(event.raw_content, event.event_type)
    record = repository.add_extraction(
        event=event,
        extraction=extraction,
        raw_content_hash=content_hash(event.raw_content),
        prompt_version=settings.prompt_version,
        model_name=settings.model_name,
    )
    return EventDraftResponse(event=repository.must_get_event(event.id), extraction=record)


@router.post("/{event_id}/confirm", response_model=LifeEvent)
def confirm_event(event_id: str, payload: EventConfirm) -> LifeEvent:
    try:
        return repository.confirm_event(event_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{event_id}/discard")
def discard_event(event_id: str) -> dict[str, str]:
    try:
        repository.mark_extraction_discarded(event_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "discarded"}


@router.get("", response_model=list[LifeEvent])
def list_events(
    user_id: str = Query(default="demo-user"),
    room_id: Optional[str] = None,
    viewer_id: Optional[str] = None,
) -> list[LifeEvent]:
    return repository.list_events(user_id=user_id, room_id=room_id, viewer_id=viewer_id)


@router.get("/{event_id}", response_model=LifeEvent)
def get_event(event_id: str) -> LifeEvent:
    try:
        return repository.must_get_event(event_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
