from __future__ import annotations

import hashlib
import re
from typing import Optional

from app.core.config import get_settings
from app.models.enums import EventType, Visibility
from app.schemas.conflicts import AIConflictReview
from app.schemas.events import AIEventExtraction, SafetyFlags


CONFLICT_WORDS = ("吵", "争执", "冲突", "生气", "冷战", "不主动", "委屈")
STRESS_WORDS = ("压力", "疲惫", "夜班", "焦虑", "累", "崩溃")
POSITIVE_WORDS = ("开心", "支持", "感谢", "高兴", "幸福", "温暖")
DECISION_WORDS = ("决定", "约定", "确认", "同意")
PLAN_WORDS = ("计划", "安排", "下次", "见面", "周末")
HEALTH_WORDS = ("失眠", "身体", "生病", "疼", "医院")
FINANCE_WORDS = ("钱", "预算", "消费", "储蓄", "理财")
CAREER_WORDS = ("工作", "项目", "学习", "考试", "职业")


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class AIService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def extract_event(self, raw_content: str, scenario: Optional[EventType] = None) -> AIEventExtraction:
        event_type = scenario or self._classify(raw_content)
        visibility = self._suggest_visibility(event_type)
        safety_flags = self._safety_flags(raw_content)
        title = self._title(raw_content, event_type)
        summary = self._summary(raw_content, event_type)
        return AIEventExtraction(
            title=title,
            summary=summary,
            event_type=event_type,
            topic_tags=self._topic_tags(raw_content, event_type),
            emotion_tags=self._emotion_tags(raw_content),
            need_tags=self._need_tags(raw_content, event_type),
            people_involved=self._people(raw_content),
            suggested_visibility=visibility,
            sensitivity_level="high" if visibility == Visibility.private else "medium",
            review_required=event_type in {EventType.conflict, EventType.stress, EventType.decision},
            follow_up_questions=self._follow_up_questions(event_type),
            safety_flags=safety_flags,
        )

    def conflict_review(self, user_view: str, partner_view: Optional[str] = None) -> AIConflictReview:
        shared_facts = [self._summary(user_view, EventType.conflict)]
        if partner_view:
            shared_facts.append(self._summary(partner_view, EventType.conflict))
        return AIConflictReview(
            shared_facts=shared_facts,
            user_emotions=self._emotion_tags(user_view),
            partner_possible_emotions=self._emotion_tags(partner_view or ""),
            user_needs=self._need_tags(user_view, EventType.conflict),
            partner_possible_needs=self._need_tags(partner_view or "", EventType.conflict),
            escalation_points=["表达中可能混合了疲惫、期待和防御，需要冷静后确认。"],
            unresolved_questions=[
                "双方各自最想被理解的一点是什么？",
                "下次类似场景出现前，可以提前做什么约定？",
            ],
            suggested_agreements=["在疲惫或情绪高峰时先暂停争论，约定一个具体复盘时间。"],
            neutral_reframe="这次争执可能围绕期待、精力和计划确定性展开；双方需要确认事实、感受和下一步安排。",
        )

    def weekly_report(self, event_summaries: list[str], room: bool = False) -> str:
        title = "本周共同复盘" if room else "本周个人复盘"
        if not event_summaries:
            return f"# {title}\n\n本周记录不足，暂时无法生成有价值的复盘。"
        joined = "\n".join(f"- {summary}" for summary in event_summaries[:20])
        return (
            f"# {title}\n\n"
            "## 本周发生了什么\n"
            f"{joined}\n\n"
            "## 高频主题\n"
            "请关注反复出现的沟通、压力、计划和决定类事件。\n\n"
            "## 建议下周行动\n"
            "1. 选择一件最重要的未解决问题进行复盘。\n"
            "2. 将模糊期待改成一个具体约定。\n"
            "3. 保留原始记录，避免只依赖事后记忆。"
        )

    def _classify(self, text: str) -> EventType:
        if self._has_any(text, CONFLICT_WORDS):
            return EventType.conflict
        if self._has_any(text, STRESS_WORDS):
            return EventType.stress
        if self._has_any(text, POSITIVE_WORDS):
            return EventType.positive_moment
        if self._has_any(text, DECISION_WORDS):
            return EventType.decision
        if self._has_any(text, PLAN_WORDS):
            return EventType.plan
        if self._has_any(text, HEALTH_WORDS):
            return EventType.health
        if self._has_any(text, FINANCE_WORDS):
            return EventType.finance
        if self._has_any(text, CAREER_WORDS):
            return EventType.career
        return EventType.other

    def _suggest_visibility(self, event_type: EventType) -> Visibility:
        if event_type in {EventType.conflict, EventType.stress, EventType.health, EventType.finance, EventType.self_reflection}:
            return Visibility.private
        if event_type in {EventType.decision, EventType.plan}:
            return Visibility.room_visible
        return Visibility.summary_only

    def _title(self, text: str, event_type: EventType) -> str:
        labels = {
            EventType.conflict: "一次需要复盘的冲突",
            EventType.communication: "一次重要沟通",
            EventType.positive_moment: "一个积极时刻",
            EventType.stress: "一次压力事件",
            EventType.decision: "一个重要决定",
            EventType.plan: "一个计划安排",
            EventType.health: "一次健康状态记录",
            EventType.career: "一次工作/学习记录",
            EventType.finance: "一次财务事件",
            EventType.self_reflection: "一次自我反思",
            EventType.other: "一条生活记录",
        }
        if "见面" in text and event_type == EventType.conflict:
            return "因见面计划产生争执"
        return labels[event_type]

    def _summary(self, text: str, event_type: EventType) -> str:
        clean = re.sub(r"\s+", " ", text).strip()
        if len(clean) > 140:
            clean = clean[:137] + "..."
        if event_type == EventType.conflict:
            return f"这是一条关系冲突记录。已识别到需要区分事实、情绪和需求：{clean}"
        return clean or "信息不足，暂无法判断完整背景。"

    def _topic_tags(self, text: str, event_type: EventType) -> list[str]:
        tags = [event_type.value]
        for keyword in ("见面", "异地", "夜班", "工作", "未来", "金钱", "回复消息"):
            if keyword in text:
                tags.append(keyword)
        return list(dict.fromkeys(tags))

    def _emotion_tags(self, text: str) -> list[str]:
        tags = []
        mapping = {
            "疲惫": ("累", "疲惫", "夜班"),
            "委屈": ("委屈", "不理解"),
            "焦虑": ("焦虑", "担心", "不安"),
            "生气": ("生气", "吵", "争执"),
            "开心": ("开心", "高兴", "幸福"),
        }
        for label, words in mapping.items():
            if self._has_any(text, words):
                tags.append(label)
        return tags

    def _need_tags(self, text: str, event_type: EventType) -> list[str]:
        tags = []
        if event_type == EventType.conflict:
            tags.extend(["被理解", "明确计划"])
        if "安全感" in text or "不主动" in text:
            tags.append("关系安全感")
        if "空间" in text:
            tags.append("个人空间")
        return list(dict.fromkeys(tags))

    def _people(self, text: str) -> list[str]:
        people = ["self"]
        if any(word in text for word in ("她", "他", "对象", "伴侣", "女朋友", "男朋友")):
            people.append("partner")
        return people

    def _follow_up_questions(self, event_type: EventType) -> list[str]:
        if event_type == EventType.conflict:
            return [
                "如果只描述事实，这次发生了什么？",
                "你真正想让对方理解的是什么？",
                "下次遇到类似情况，可以提前约定什么？",
            ]
        if event_type == EventType.stress:
            return ["压力主要来自哪里？", "有没有一件可以降低负担的小行动？"]
        return ["这件事对你为什么重要？", "是否需要后续行动？"]

    def _safety_flags(self, text: str) -> SafetyFlags:
        return SafetyFlags(
            self_harm=self._has_any(text, ("自杀", "不想活", "伤害自己")),
            violence=self._has_any(text, ("打人", "威胁", "暴力")),
            abuse=self._has_any(text, ("控制", "强迫", "跟踪")),
            financial_risk=self._has_any(text, ("借贷", "赌博", "高利贷")),
            medical_risk=self._has_any(text, ("诊断", "药", "医院", "疼")),
        )

    def _has_any(self, text: str, words: tuple[str, ...]) -> bool:
        return any(word in text for word in words)


ai_service = AIService()
