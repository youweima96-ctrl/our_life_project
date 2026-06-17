from app.models.enums import Visibility
from app.schemas.events import DraftEventCreate, EventConfirm
from app.schemas.rooms import RoomCreate
from app.services.ai import ai_service, content_hash
from app.services.repository import InMemoryRepository


def test_room_view_hides_private_event_from_partner():
    repo = InMemoryRepository()
    room = repo.create_room(RoomCreate(owner_user_id="u1", name="关系房间"))
    repo.join_room("u2", room.invite_code)
    draft = repo.create_draft_event(DraftEventCreate(user_id="u1", room_id=room.id, raw_content="我很累，不想共享原文"))
    extraction = ai_service.extract_event(draft.raw_content)
    repo.add_extraction(draft, extraction, content_hash(draft.raw_content), "test", "test")
    repo.confirm_event(
        draft.id,
        EventConfirm(
            title="私密压力",
            summary="压力事件",
            event_type=extraction.event_type,
            visibility=Visibility.private,
        ),
    )

    events = repo.list_events(user_id="u2", room_id=room.id, viewer_id="u2")

    assert events == []


def test_room_view_removes_raw_content_for_summary_only():
    repo = InMemoryRepository()
    room = repo.create_room(RoomCreate(owner_user_id="u1", name="关系房间"))
    repo.join_room("u2", room.invite_code)
    draft = repo.create_draft_event(DraftEventCreate(user_id="u1", room_id=room.id, raw_content="原始内容不应展示"))
    extraction = ai_service.extract_event(draft.raw_content)
    repo.add_extraction(draft, extraction, content_hash(draft.raw_content), "test", "test")
    repo.confirm_event(
        draft.id,
        EventConfirm(
            title="摘要可见",
            summary="只展示摘要",
            event_type=extraction.event_type,
            visibility=Visibility.summary_only,
        ),
    )

    events = repo.list_events(user_id="u2", room_id=room.id, viewer_id="u2")

    assert len(events) == 1
    assert events[0].raw_content == ""
    assert events[0].summary == "只展示摘要"

