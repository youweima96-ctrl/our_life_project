from fastapi import APIRouter, HTTPException, Query

from app.schemas.events import LifeEvent
from app.schemas.rooms import JoinRoomRequest, Room, RoomCreate, SharedDecision, SharedDecisionCreate
from app.services.repository import repository

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("", response_model=Room)
def create_room(payload: RoomCreate) -> Room:
    return repository.create_room(payload)


@router.get("", response_model=list[Room])
def list_rooms(user_id: str = Query(default="demo-user")) -> list[Room]:
    return repository.list_rooms(user_id)


@router.get("/{room_id}", response_model=Room)
def get_room(room_id: str) -> Room:
    try:
        return repository.must_get_room(room_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/join", response_model=Room)
def join_room(payload: JoinRoomRequest) -> Room:
    try:
        return repository.join_room(payload.user_id, payload.invite_code)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{room_id}/events", response_model=list[LifeEvent])
def room_events(room_id: str, viewer_id: str = Query(default="demo-user")) -> list[LifeEvent]:
    try:
        repository.must_get_room(room_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return repository.list_events(user_id=viewer_id, room_id=room_id, viewer_id=viewer_id)


@router.post("/{room_id}/decisions", response_model=SharedDecision)
def create_decision(room_id: str, payload: SharedDecisionCreate) -> SharedDecision:
    if payload.room_id != room_id:
        raise HTTPException(status_code=400, detail="room_id mismatch")
    return repository.create_decision(payload)

