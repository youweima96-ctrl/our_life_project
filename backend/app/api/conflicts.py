from fastapi import APIRouter, HTTPException

from app.schemas.conflicts import ConflictCreate, ConflictReview, PartnerViewCreate
from app.services.ai import ai_service
from app.services.repository import repository

router = APIRouter(prefix="/conflicts", tags=["conflicts"])


@router.post("", response_model=ConflictReview)
def create_conflict(payload: ConflictCreate) -> ConflictReview:
    try:
        repository.must_get_event(payload.event_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return repository.create_conflict(
        event_id=payload.event_id,
        room_id=payload.room_id,
        creator_id=payload.creator_id,
        user_view=payload.user_view,
    )


@router.get("/{conflict_id}", response_model=ConflictReview)
def get_conflict(conflict_id: str) -> ConflictReview:
    try:
        return repository.must_get_conflict(conflict_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{conflict_id}/partner-view", response_model=ConflictReview)
def add_partner_view(conflict_id: str, payload: PartnerViewCreate) -> ConflictReview:
    try:
        return repository.update_partner_view(conflict_id, payload.partner_view)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{conflict_id}/generate-review", response_model=ConflictReview)
def generate_review(conflict_id: str) -> ConflictReview:
    try:
        review = repository.must_get_conflict(conflict_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    ai_review = ai_service.conflict_review(review.user_view, review.partner_view)
    return repository.save_conflict_ai_review(conflict_id, ai_review)

