from enum import Enum


class EventType(str, Enum):
    conflict = "conflict"
    communication = "communication"
    positive_moment = "positive_moment"
    stress = "stress"
    decision = "decision"
    plan = "plan"
    health = "health"
    career = "career"
    finance = "finance"
    self_reflection = "self_reflection"
    other = "other"


class Visibility(str, Enum):
    private = "private"
    summary_only = "summary_only"
    room_visible = "room_visible"


class ReviewStatus(str, Enum):
    unreviewed = "unreviewed"
    reviewed = "reviewed"
    ignored = "ignored"


class SourceType(str, Enum):
    text = "text"
    voice = "voice"
    template = "template"


class AIUserAction(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    edited = "edited"
    regenerated = "regenerated"
    discarded = "discarded"


class RoomType(str, Enum):
    couple = "couple"
    friend = "friend"
    custom = "custom"


class ConflictStatus(str, Enum):
    draft = "draft"
    waiting_partner = "waiting_partner"
    completed = "completed"
    archived = "archived"


class DecisionStatus(str, Enum):
    active = "active"
    done = "done"
    expired = "expired"
    archived = "archived"

