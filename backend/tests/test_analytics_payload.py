from __future__ import annotations

from datetime import datetime, timedelta

from app.services.payloads.analytics import build_analytics_payload, build_reading_time_rank
from app.services.review.scheduler import serialize_datetime


class FakeAnalyticsRepository:
    def __init__(self, progress_map: dict[int, dict[str, object]]) -> None:
        self.progress_map = progress_map

    def get_review_progress_map(self, note_ids: list[int] | None = None) -> dict[int, dict[str, object]]:
        if not note_ids:
            return self.progress_map
        return {note_id: self.progress_map[note_id] for note_id in note_ids if note_id in self.progress_map}

    def get_review_log_dates(self) -> list[str]:
        return [serialize_datetime(datetime.now())]


def test_build_analytics_payload_aggregates_reading_and_review_metrics() -> None:
    now = datetime.now()
    data = {
        "books": [
            {
                "id": 1,
                "title": "投资书",
                "author": "作者 A",
                "category": "投资",
                "notes": 2,
                "reading_date": "2026-04-01",
                "last_read_date": "2026-04-20",
                "reading_time": "2小时30分钟",
                "cover": "",
            },
            {
                "id": 2,
                "title": "哲学书",
                "author": "作者 B",
                "category": "哲学",
                "notes": 1,
                "reading_date": "2026-03-01",
                "last_read_date": "",
                "reading_time": "45分钟",
                "cover": "",
            },
        ],
        "notes": [
            {
                "id": 1,
                "book_id": 1,
                "category": "投资",
                "tags": ["投资", "长期主义"],
                "timestamp": serialize_datetime(now),
            },
            {"id": 2, "book_id": 1, "category": "投资", "tags": ["投资"], "timestamp": ""},
            {"id": 3, "book_id": 2, "category": "哲学", "tags": ["哲学"], "timestamp": ""},
        ],
    }
    repository = FakeAnalyticsRepository(
        {
            1: {
                "review_count": 1,
                "mastery_score": 1,
                "last_result": "medium",
                "last_reviewed_at": serialize_datetime(now),
                "next_review_at": serialize_datetime(now + timedelta(days=2)),
            },
            3: {
                "review_count": 3,
                "mastery_score": 3,
                "last_result": "high",
                "last_reviewed_at": serialize_datetime(now - timedelta(days=3)),
                "next_review_at": serialize_datetime(now - timedelta(days=1)),
            },
        }
    )

    payload = build_analytics_payload(data, repository)

    assert payload["metrics"][0]["value"] == 2
    assert payload["category_preferences"][0]["category"] == "投资"
    assert payload["reading_time_rank"][0]["title"] == "投资书"
    assert payload["reading_time_rank"][0]["reading_time_minutes"] == 150
    assert payload["preference_radar"][0]["label"] == "投资"
    assert payload["high_value_matrix"][0]["title"] == "投资书"
    assert payload["author_cloud"][0]["author"] == "作者 A"
    assert payload["author_cloud"][0]["book_count"] == 1
    assert len(payload["activity_heatmap"]) == 35
    assert payload["long_term_metrics"][0]["label"] == "连续复习"
    assert payload["topic_rank"][0]["topic"] == "投资"
    assert payload["review_funnel"] == [
        {"label": "新卡片", "value": 1, "hint": "还没有复习记录"},
        {"label": "待巩固", "value": 1, "hint": "不会/模糊或掌握度偏低"},
        {"label": "今日到期", "value": 2, "hint": "今天应该回看"},
        {"label": "已掌握", "value": 1, "hint": "掌握度达到阈值"},
    ]


def test_reading_time_rank_keeps_more_than_ten_books() -> None:
    books = [
        {
            "id": index,
            "title": f"书籍 {index}",
            "category": "未分类",
            "reading_time": f"{index}分钟",
        }
        for index in range(1, 13)
    ]

    rank = build_reading_time_rank(books, notes=[], progress_map={})

    assert len(rank) == 12
    assert rank[0]["title"] == "书籍 12"
