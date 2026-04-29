from __future__ import annotations

from datetime import datetime, timedelta

from app.services.review.scheduler import (
    calculate_next_review_at,
    calculate_review_streak,
    get_review_interval_days,
    parse_iso_datetime,
    serialize_datetime,
    update_mastery_score,
)


def test_parse_and_serialize_iso_datetime() -> None:
    value = datetime(2026, 4, 29, 10, 30, 5, 123456)

    serialized = serialize_datetime(value)

    assert serialized == "2026-04-29T10:30:05"
    assert parse_iso_datetime(serialized) == datetime(2026, 4, 29, 10, 30, 5)
    assert parse_iso_datetime("") is None
    assert parse_iso_datetime("not-a-date") is None


def test_review_interval_and_mastery_score_rules() -> None:
    assert get_review_interval_days("low", 0, 0) == 1
    assert get_review_interval_days("medium", 1, 1) == 4
    assert get_review_interval_days("high", 2, 1) == 21
    assert get_review_interval_days("high", 2, 2) == 28
    assert get_review_interval_days("unknown", 0, 0) == 2

    assert update_mastery_score("low", 0) == 0
    assert update_mastery_score("low", 2) == 1
    assert update_mastery_score("medium", 0) == 1
    assert update_mastery_score("medium", 3) == 3
    assert update_mastery_score("high", 2) == 3


def test_calculate_next_review_at_uses_interval_rules() -> None:
    now = datetime(2026, 4, 29, 9, 0, 0)

    next_review_at = calculate_next_review_at("high", 2, 2, now)

    assert next_review_at == now + timedelta(days=28)


def test_calculate_review_streak_counts_consecutive_days_from_today() -> None:
    today = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    three_days_ago = today - timedelta(days=3)

    assert calculate_review_streak([serialize_datetime(today), serialize_datetime(yesterday)]) == 2
    assert calculate_review_streak([serialize_datetime(yesterday), serialize_datetime(three_days_ago)]) == 0

