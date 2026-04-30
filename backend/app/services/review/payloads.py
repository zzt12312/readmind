"""Review-center payload builders.

The review scheduler (`scheduler.py`) knows timing and mastery rules. This file
turns notes + persisted review progress into UI-ready cards and summaries. The
repository is passed in explicitly so the payload logic can be tested with a
fake repository instead of touching SQLite.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .scheduler import (
    REVIEW_BATCH_SIZE,
    REVIEW_MASTERED_THRESHOLD,
    calculate_review_streak,
    parse_iso_datetime,
)

DEFAULT_DAILY_GOAL = 10
DAILY_GOAL_OPTIONS = [5, 10, 20]
MIN_DAILY_GOAL = 1
MAX_DAILY_GOAL = REVIEW_BATCH_SIZE
QUEUE_OPTIONS = [
    {"value": "due", "label": "今日到期", "description": "今天应该复习的全部卡片，包括新卡和旧卡。"},
    {"value": "weak", "label": "待巩固", "description": "上次不会/模糊记得，或掌握度仍偏低的卡片。"},
    {"value": "new", "label": "新卡片", "description": "还没有任何复习记录的摘录。"},
]
LEVEL_GUIDANCE = [
    {
        "level": "low",
        "label": "不会",
        "hint": "适合完全想不起来的卡片，系统会更快安排它再次出现。",
    },
    {
        "level": "medium",
        "label": "模糊记得",
        "hint": "适合能说出大意但不够稳定的卡片，会进入待巩固队列并安排中等间隔复习。",
    },
    {
        "level": "high",
        "label": "熟练掌握",
        "hint": "适合已经能主动复述的卡片，系统会拉长下次复习间隔。",
    },
]


def build_review_overview(data: dict[str, Any], repository: Any) -> dict[str, Any]:
    notes = data["notes"]
    now = datetime.now()
    progress_map = repository.get_review_progress_map([note["id"] for note in notes]) if notes else {}
    review_logs = repository.get_review_log_dates()

    due_count = 0
    mastered_count = 0
    for note in notes:
        progress = progress_map.get(note["id"])
        if not progress:
            due_count += 1
            continue
        if progress.get("mastery_score", 0) >= REVIEW_MASTERED_THRESHOLD:
            mastered_count += 1
        next_review_at = parse_iso_datetime(progress.get("next_review_at", ""))
        if next_review_at is None or next_review_at <= now:
            due_count += 1

    reviewed_total = len(progress_map)
    mastery_rate = f"{round((mastered_count / reviewed_total) * 100)}%" if reviewed_total else "0%"

    return {
        "due_count": due_count,
        "streak_days": calculate_review_streak(review_logs),
        "mastery_rate": mastery_rate,
    }


def build_review_payload(data: dict[str, Any], repository: Any) -> dict[str, Any]:
    return build_review_payload_with_scope(data, repository)


def build_review_payload_with_scope(
    data: dict[str, Any],
    repository: Any,
    *,
    tag: str = "",
    book_id: int | None = None,
    daily_goal: int | None = None,
    queue: str = "due",
) -> dict[str, Any]:
    notes = data["notes"]
    if book_id is not None:
        notes = [note for note in notes if note["book_id"] == book_id]
    if tag:
        notes = [note for note in notes if tag in note.get("tags", [])]

    progress_map = repository.get_review_progress_map([note["id"] for note in notes]) if notes else {}
    scoped_data = {**data, "notes": notes}
    overview = build_review_overview(scoped_data, repository)
    selected_queue = normalize_queue(queue)
    now = datetime.now()

    queue_notes: dict[str, list[tuple[tuple[int, float, int], dict[str, Any], dict[str, Any] | None]]] = {
        "due": [],
        "weak": [],
        "new": [],
    }
    for note in notes:
        progress = progress_map.get(note["id"])
        next_review_at = parse_iso_datetime(progress.get("next_review_at", "")) if progress else None
        is_due = progress is None or next_review_at is None or next_review_at <= now
        is_weak = progress is not None and (
            int(progress.get("mastery_score") or 0) <= 1
            or progress.get("last_result") in {"low", "medium"}
        )

        overdue_rank = 0 if progress and next_review_at else 1
        due_timestamp = next_review_at.timestamp() if next_review_at else float("inf")
        richness = len(note.get("excerpt") or "") + len(note.get("comment") or "")
        scored_item = ((overdue_rank, due_timestamp, -richness), note, progress)
        if is_due:
            queue_notes["due"].append(scored_item)
        if is_weak:
            queue_notes["weak"].append(scored_item)
        if progress is None and is_due:
            queue_notes["new"].append(scored_item)

    for items in queue_notes.values():
        items.sort(key=lambda item: item[0])

    queue_counts = {key: len(items) for key, items in queue_notes.items()}
    selected_notes = queue_notes[selected_queue]
    selected_daily_goal = normalize_daily_goal(daily_goal)
    review_notes = selected_notes[: min(selected_daily_goal, REVIEW_BATCH_SIZE)]
    queue_options = build_queue_options(queue_counts)
    queue_label = get_queue_label(selected_queue)

    if not review_notes:
        return {
            "summary": build_review_summary(overview),
            "plan": build_review_plan(
                overview,
                selected_count=0,
                selected_daily_goal=selected_daily_goal,
                queue_label=queue_label,
            ),
            "level_guidance": LEVEL_GUIDANCE,
            "queue_options": queue_options,
            "scope": {
                "tag": tag,
                "book_id": book_id,
                "queue": selected_queue,
            },
            "card": empty_review_card(),
            "cards": [],
            "weak_cards": build_review_cards(queue_notes["weak"][:5]),
        }

    cards = build_review_cards(review_notes)

    return {
        "summary": build_review_summary(overview),
        "plan": build_review_plan(
            overview,
            selected_count=len(cards),
            selected_daily_goal=selected_daily_goal,
            queue_label=queue_label,
        ),
        "level_guidance": LEVEL_GUIDANCE,
        "queue_options": queue_options,
        "scope": {
            "tag": tag,
            "book_id": book_id,
            "queue": selected_queue,
        },
        "card": cards[0],
        "cards": cards,
        "weak_cards": build_review_cards(queue_notes["weak"][:5]),
    }


def build_review_cards(
    review_notes: list[tuple[tuple[int, float, int], dict[str, Any], dict[str, Any] | None]],
) -> list[dict[str, Any]]:
    return [
        {
            "id": index + 1,
            "book_id": note["book_id"],
            "note_id": note["id"],
            "question": "这条摘录最值得复述的核心观点是什么？",
            "source": f"{note['book_title']} · {note['chapter'] or '未分章节'}",
            "answer": note["excerpt"],
            "tags": note.get("tags", []),
            "review_count": int((progress or {}).get("review_count") or 0),
            "mastery_score": int((progress or {}).get("mastery_score") or 0),
            "last_reviewed_at": (progress or {}).get("last_reviewed_at", ""),
            "next_review_at": (progress or {}).get("next_review_at", ""),
            "reason": build_card_reason(note, progress),
        }
        for index, (_, note, progress) in enumerate(review_notes)
    ]


def build_card_reason(note: dict[str, Any], progress: dict[str, Any] | None) -> dict[str, str]:
    tags = [str(tag) for tag in note.get("tags", []) if str(tag).strip()]
    topic_text = f"「{tags[0]}」主题" if tags else "这条摘录"

    if not progress:
        return {
            "label": "新卡片",
            "detail": f"{topic_text}还没有复习记录，适合先建立第一印象。",
            "next_action": "先用自己的话复述一遍，再查看原摘录校准理解。",
        }

    last_result = str(progress.get("last_result") or "")
    mastery_score = int(progress.get("mastery_score") or 0)
    review_count = int(progress.get("review_count") or 0)
    next_review_at = str(progress.get("next_review_at") or "")
    last_reviewed_at = str(progress.get("last_reviewed_at") or "")

    if last_result == "low" or mastery_score <= 0:
        return {
            "label": "上次没想起来",
            "detail": f"{topic_text}上次标记为“不会”，今天优先回看可以减少遗忘。",
            "next_action": "不用追求完整背诵，先抓住一个核心观点。",
        }

    if last_result == "medium" or mastery_score == 1:
        return {
            "label": "待巩固",
            "detail": f"{topic_text}上次还不够稳定，适合趁间隔不长再巩固一次。",
            "next_action": "先说出大意，再看摘录里有没有遗漏的关键词。",
        }

    if next_review_at:
        return {
            "label": "按计划到期",
            "detail": f"这张卡片已复习 {review_count} 次，计划在 {next_review_at[:10]} 前后再次出现。",
            "next_action": "如果能主动复述，可以标记“熟练掌握”拉长下次间隔。",
        }

    if last_reviewed_at:
        return {
            "label": "长期未回看",
            "detail": f"这张卡片上次复习在 {last_reviewed_at[:10]}，适合重新唤醒。",
            "next_action": "先回想当时为什么划线，再决定是否继续保留。",
        }

    return {
        "label": "值得回看",
        "detail": f"{topic_text}有较完整的摘录内容，适合放进今天的小组复习。",
        "next_action": "复述后可以跳回原笔记，看看上下文是否还有新理解。",
    }


def build_review_summary(overview: dict[str, Any], due_count: str | None = None) -> list[dict[str, str]]:
    return [
        {"label": "待复习", "value": due_count or str(overview["due_count"])},
        {"label": "连续复习", "value": f"{overview['streak_days']} 天"},
        {"label": "掌握率", "value": overview["mastery_rate"]},
    ]


def normalize_daily_goal(daily_goal: int | None) -> int:
    if daily_goal is not None and MIN_DAILY_GOAL <= daily_goal <= MAX_DAILY_GOAL:
        return int(daily_goal)
    return DEFAULT_DAILY_GOAL


def normalize_queue(queue: str) -> str:
    values = {item["value"] for item in QUEUE_OPTIONS}
    return queue if queue in values else "due"


def build_queue_options(queue_counts: dict[str, int]) -> list[dict[str, Any]]:
    return [
        {
            **item,
            "count": queue_counts.get(str(item["value"]), 0),
        }
        for item in QUEUE_OPTIONS
    ]


def get_queue_label(queue: str) -> str:
    for item in QUEUE_OPTIONS:
        if item["value"] == queue:
            return str(item["label"])
    return "今日到期"


def build_review_plan(
    overview: dict[str, Any],
    *,
    selected_count: int,
    selected_daily_goal: int,
    queue_label: str,
) -> dict[str, Any]:
    due_count = int(overview["due_count"])
    suggested_today = selected_count
    if selected_count:
        message = (
            f"当前队列：{queue_label}。今天先完成 {suggested_today} 张；"
            f"本轮已为你挑出 {selected_count} 张最该复习的卡片，"
            "不用一次清空全部待复习内容。"
        )
    else:
        message = f"当前队列：{queue_label}。这个队列暂时没有可复习卡片，可以切换其他队列或调整复习范围。"

    return {
        "default_daily_goal": DEFAULT_DAILY_GOAL,
        "selected_daily_goal": selected_daily_goal,
        "daily_goal_options": DAILY_GOAL_OPTIONS,
        "suggested_today": suggested_today,
        "due_count": due_count,
        "batch_size": REVIEW_BATCH_SIZE,
        "message": message,
    }


def empty_review_card() -> dict[str, Any]:
    return {
        "id": 0,
        "book_id": 0,
        "note_id": 0,
        "question": "",
        "source": "",
        "answer": "",
        "tags": [],
        "review_count": 0,
        "mastery_score": 0,
        "last_reviewed_at": "",
        "next_review_at": "",
        "reason": {
            "label": "",
            "detail": "",
            "next_action": "",
        },
    }
