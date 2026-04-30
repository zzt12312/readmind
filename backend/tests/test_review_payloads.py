from __future__ import annotations

from datetime import datetime, timedelta

from app.services.review.payloads import build_review_payload_with_scope, normalize_daily_goal
from app.services.review.scheduler import serialize_datetime


class FakeReviewRepository:
    def __init__(self, progress_map: dict[int, dict[str, object]]) -> None:
        self.progress_map = progress_map

    def get_review_progress_map(self, note_ids: list[int]) -> dict[int, dict[str, object]]:
        return {note_id: self.progress_map[note_id] for note_id in note_ids if note_id in self.progress_map}

    def get_review_log_dates(self) -> list[str]:
        return []


def make_note(note_id: int, excerpt: str) -> dict[str, object]:
    return {
        "id": note_id,
        "book_id": 1,
        "book_title": "测试书籍",
        "chapter": "第一章",
        "excerpt": excerpt,
        "comment": "",
        "tags": [],
    }


def test_review_payload_splits_due_weak_and_new_queues() -> None:
    now = datetime.now()
    data = {
        "notes": [
            make_note(1, "已经复习过但仍薄弱的摘录"),
            make_note(2, "还没有任何复习记录的新摘录"),
            make_note(3, "掌握度较高但已经到期的摘录"),
            make_note(4, "模糊记得但还没有再次到期的摘录"),
        ]
    }
    repository = FakeReviewRepository(
        {
            1: {
                "review_count": 2,
                "mastery_score": 1,
                "last_result": "low",
                "last_reviewed_at": serialize_datetime(now - timedelta(days=2)),
                "next_review_at": serialize_datetime(now - timedelta(days=1)),
            },
            3: {
                "review_count": 3,
                "mastery_score": 3,
                "last_result": "high",
                "last_reviewed_at": serialize_datetime(now - timedelta(days=30)),
                "next_review_at": serialize_datetime(now - timedelta(days=1)),
            },
            4: {
                "review_count": 1,
                "mastery_score": 1,
                "last_result": "medium",
                "last_reviewed_at": serialize_datetime(now),
                "next_review_at": serialize_datetime(now + timedelta(days=2)),
            },
        }
    )

    due_payload = build_review_payload_with_scope(data, repository, queue="due")
    weak_payload = build_review_payload_with_scope(data, repository, queue="weak")
    new_payload = build_review_payload_with_scope(data, repository, queue="new")

    assert [option["count"] for option in due_payload["queue_options"]] == [3, 2, 1]
    assert {card["note_id"] for card in due_payload["cards"]} == {1, 2, 3}
    assert [card["note_id"] for card in weak_payload["cards"]] == [1, 4]
    assert [card["note_id"] for card in new_payload["cards"]] == [2]
    assert new_payload["cards"][0]["reason"]["label"] == "新卡片"
    assert weak_payload["cards"][0]["reason"]["label"] == "上次没想起来"
    assert any(card["reason"]["label"] == "按计划到期" for card in due_payload["cards"])


def test_review_daily_goal_accepts_custom_values() -> None:
    assert normalize_daily_goal(1) == 1
    assert normalize_daily_goal(20) == 20
    assert normalize_daily_goal(37) == 37
    assert normalize_daily_goal(0) == 10
    assert normalize_daily_goal(99) == 10
