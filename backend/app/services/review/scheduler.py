from __future__ import annotations

from datetime import datetime, timedelta

REVIEW_BATCH_SIZE = 50
REVIEW_MASTERED_THRESHOLD = 2
REVIEW_INTERVAL_RULES = {
    "low": [1, 2, 3],
    "medium": [2, 4, 7],
    "high": [4, 10, 21],
}


def parse_iso_datetime(value: str) -> datetime | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def serialize_datetime(value: datetime | None) -> str:
    return value.replace(microsecond=0).isoformat() if value else ""


def get_review_interval_days(level: str, review_count: int, mastery_score: int) -> int:
    schedule = REVIEW_INTERVAL_RULES.get(level, REVIEW_INTERVAL_RULES["medium"])
    index = min(max(review_count, 0), len(schedule) - 1)
    base_days = schedule[index]
    if level == "high" and mastery_score >= REVIEW_MASTERED_THRESHOLD:
        return base_days + 7
    return base_days


def calculate_review_streak(date_texts: list[str]) -> int:
    days = sorted(
        {
            parsed.date()
            for value in date_texts
            if (parsed := parse_iso_datetime(value)) is not None
        },
        reverse=True,
    )
    if not days:
        return 0

    streak = 0
    cursor = datetime.now().date()
    remaining = set(days)
    while cursor in remaining:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def update_mastery_score(level: str, mastery_score: int) -> int:
    if level == "low":
        return max(0, mastery_score - 1)
    if level == "medium":
        return min(3, max(mastery_score, 1))
    return min(3, mastery_score + 1)


def calculate_next_review_at(level: str, review_count: int, mastery_score: int, now: datetime) -> datetime:
    return now + timedelta(days=get_review_interval_days(level, review_count, mastery_score))
