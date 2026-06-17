from app.models.enums import EventType, Visibility
from app.services.ai import ai_service


def test_extract_conflict_defaults_to_private_and_review_required():
    result = ai_service.extract_event("今天又因为见面时间和她吵架了，我最近夜班太累。")

    assert result.event_type == EventType.conflict
    assert result.suggested_visibility == Visibility.private
    assert result.review_required is True
    assert "被理解" in result.need_tags


def test_extract_positive_moment_defaults_to_summary_only():
    result = ai_service.extract_event("今天她很支持我，我觉得很开心。")

    assert result.event_type == EventType.positive_moment
    assert result.suggested_visibility == Visibility.summary_only

