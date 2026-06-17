from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.models.enums import AIUserAction, ConflictStatus, EventType, ReviewStatus, Visibility
from app.schemas.conflicts import AIConflictReview, ConflictReview
from app.schemas.events import (
    AIEventExtraction,
    AIExtractionRecord,
    DraftEventCreate,
    EventConfirm,
    LifeEvent,
)
from app.schemas.reports import Report
from app.schemas.rooms import Room, RoomCreate, SharedDecision, SharedDecisionCreate


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class InMemoryRepository:
    def __init__(self) -> None:
        self.events: dict[str, LifeEvent] = {}
        self.extractions: dict[str, AIExtractionRecord] = {}
        self.rooms: dict[str, Room] = {}
        self.conflicts: dict[str, ConflictReview] = {}
        self.decisions: dict[str, SharedDecision] = {}
        self.reports: dict[str, Report] = {}

    def create_draft_event(self, payload: DraftEventCreate) -> LifeEvent:
        event = LifeEvent(
            id=new_id("evt"),
            user_id=payload.user_id,
            room_id=payload.room_id,
            raw_content=payload.raw_content,
            event_type=payload.scenario or EventType.other,
            event_time=now_utc(),
            source_type=payload.source_type,
            created_at=now_utc(),
            updated_at=now_utc(),
        )
        self.events[event.id] = event
        return event

    def add_extraction(
        self,
        event: LifeEvent,
        extraction: AIEventExtraction,
        raw_content_hash: str,
        prompt_version: str,
        model_name: str,
    ) -> AIExtractionRecord:
        record = AIExtractionRecord(
            id=new_id("aix"),
            event_id=event.id,
            user_id=event.user_id,
            raw_content_hash=raw_content_hash,
            prompt_version=prompt_version,
            model_name=model_name,
            output_json=extraction,
            created_at=now_utc(),
        )
        self.extractions[record.id] = record
        self.events[event.id] = event.model_copy(update={"ai_extraction_id": record.id, "updated_at": now_utc()})
        return record

    def confirm_event(self, event_id: str, payload: EventConfirm) -> LifeEvent:
        event = self.must_get_event(event_id)
        updated = event.model_copy(
            update={
                "title": payload.title,
                "summary": payload.summary,
                "event_type": payload.event_type,
                "topic_tags": payload.topic_tags,
                "emotion_tags": payload.emotion_tags,
                "need_tags": payload.need_tags,
                "visibility": payload.visibility,
                "event_time": payload.event_time or event.event_time,
                "confirmed": True,
                "review_status": ReviewStatus.unreviewed,
                "updated_at": now_utc(),
            }
        )
        self.events[event_id] = updated
        if updated.ai_extraction_id and updated.ai_extraction_id in self.extractions:
            extraction = self.extractions[updated.ai_extraction_id]
            action = AIUserAction.confirmed
            if payload.accuracy_feedback == "edited":
                action = AIUserAction.edited
            self.extractions[extraction.id] = extraction.model_copy(
                update={"user_action": action, "accuracy_feedback": payload.accuracy_feedback}
            )
        return updated

    def list_events(
        self,
        user_id: str,
        room_id: str | None = None,
        viewer_id: str | None = None,
        confirmed_only: bool = True,
    ) -> list[LifeEvent]:
        events = list(self.events.values())
        if confirmed_only:
            events = [event for event in events if event.confirmed]
        if room_id:
            events = [event for event in events if event.room_id == room_id]
            events = [self.visible_event_for_room(event, viewer_id or user_id) for event in events]
            events = [event for event in events if event is not None]
        else:
            events = [event for event in events if event.user_id == user_id]
        return sorted(events, key=lambda item: item.event_time, reverse=True)

    def visible_event_for_room(self, event: LifeEvent, viewer_id: str) -> LifeEvent | None:
        if event.visibility == Visibility.private and event.user_id != viewer_id:
            return None
        if event.visibility == Visibility.summary_only and event.user_id != viewer_id:
            return event.model_copy(update={"raw_content": ""})
        return event

    def must_get_event(self, event_id: str) -> LifeEvent:
        if event_id not in self.events:
            raise KeyError("event not found")
        return self.events[event_id]

    def mark_extraction_discarded(self, event_id: str) -> None:
        event = self.must_get_event(event_id)
        if event.ai_extraction_id and event.ai_extraction_id in self.extractions:
            extraction = self.extractions[event.ai_extraction_id]
            self.extractions[extraction.id] = extraction.model_copy(update={"user_action": AIUserAction.discarded})

    def create_room(self, payload: RoomCreate) -> Room:
        room = Room(
            id=new_id("room"),
            name=payload.name,
            room_type=payload.room_type,
            owner_user_id=payload.owner_user_id,
            member_ids=[payload.owner_user_id],
            invite_code=uuid4().hex[:8],
            created_at=now_utc(),
        )
        self.rooms[room.id] = room
        return room

    def list_rooms(self, user_id: str) -> list[Room]:
        return [room for room in self.rooms.values() if user_id in room.member_ids]

    def join_room(self, user_id: str, invite_code: str) -> Room:
        for room in self.rooms.values():
            if room.invite_code == invite_code:
                member_ids = list(dict.fromkeys([*room.member_ids, user_id]))
                updated = room.model_copy(update={"member_ids": member_ids})
                self.rooms[room.id] = updated
                return updated
        raise KeyError("invite code not found")

    def must_get_room(self, room_id: str) -> Room:
        if room_id not in self.rooms:
            raise KeyError("room not found")
        return self.rooms[room_id]

    def create_conflict(self, event_id: str, room_id: str | None, creator_id: str, user_view: str) -> ConflictReview:
        review = ConflictReview(
            id=new_id("cfr"),
            event_id=event_id,
            room_id=room_id,
            creator_id=creator_id,
            user_view=user_view,
            created_at=now_utc(),
            updated_at=now_utc(),
        )
        self.conflicts[review.id] = review
        return review

    def update_partner_view(self, conflict_id: str, partner_view: str) -> ConflictReview:
        review = self.must_get_conflict(conflict_id)
        updated = review.model_copy(
            update={
                "partner_view": partner_view,
                "status": ConflictStatus.waiting_partner,
                "updated_at": now_utc(),
            }
        )
        self.conflicts[conflict_id] = updated
        return updated

    def save_conflict_ai_review(self, conflict_id: str, ai_review: AIConflictReview) -> ConflictReview:
        review = self.must_get_conflict(conflict_id)
        updated = review.model_copy(
            update={
                "ai_review_json": ai_review,
                "status": ConflictStatus.completed,
                "visibility": Visibility.room_visible if review.room_id else Visibility.private,
                "updated_at": now_utc(),
            }
        )
        self.conflicts[conflict_id] = updated
        return updated

    def must_get_conflict(self, conflict_id: str) -> ConflictReview:
        if conflict_id not in self.conflicts:
            raise KeyError("conflict review not found")
        return self.conflicts[conflict_id]

    def create_decision(self, payload: SharedDecisionCreate) -> SharedDecision:
        decision = SharedDecision(id=new_id("dec"), created_at=now_utc(), **payload.model_dump())
        self.decisions[decision.id] = decision
        return decision

    def create_report(self, user_id: str, room_id: str | None, report_type: str, content: str, event_ids: list[str]) -> Report:
        report = Report(
            id=new_id("rpt"),
            user_id=user_id,
            room_id=room_id,
            report_type=report_type,
            content_markdown=content,
            source_event_ids=event_ids,
            created_at=now_utc(),
        )
        self.reports[report.id] = report
        return report

    def list_reports(self, user_id: str) -> list[Report]:
        return [report for report in self.reports.values() if report.user_id == user_id]


repository = InMemoryRepository()
