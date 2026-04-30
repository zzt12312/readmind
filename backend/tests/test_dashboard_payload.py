from __future__ import annotations

from app.services.payloads.dashboard import build_dashboard_payload


def test_dashboard_payload_includes_daily_brief() -> None:
    data = {
        "books": [
            {
                "id": 1,
                "title": "长期主义",
                "author": "作者 A",
                "category": "投资",
                "notes": 8,
                "reading_date": "2026-04-01",
                "last_read_date": "2026-04-20",
                "cover": "",
            },
            {
                "id": 2,
                "title": "认知升级",
                "author": "作者 B",
                "category": "认知",
                "notes": 3,
                "reading_date": "2026-04-02",
                "last_read_date": "",
                "cover": "",
            },
        ],
        "notes": [
            {"id": 1, "book_id": 1, "category": "投资", "tags": ["长期主义"]},
            {"id": 2, "book_id": 1, "category": "投资", "tags": ["现金流"]},
        ],
        "stats": {
            "book_count": 2,
            "note_count": 2,
            "category_count": 2,
            "top_topics": ["长期主义", "现金流"],
        },
    }
    review_state = {
        "due_count": 6,
        "streak_days": 3,
        "mastery_rate": "50%",
    }

    payload = build_dashboard_payload(data, review_state)

    assert payload["daily_brief"]["title"] == "今日阅读回顾"
    assert "长期主义" in payload["daily_brief"]["summary"]
    assert payload["daily_brief"]["feedback_items"][0]["value"] == "6 张"
    assert payload["daily_brief"]["highlights"]["book"]["title"] == "长期主义"
    assert payload["daily_brief"]["highlights"]["author"] == "作者 A"
    assert payload["daily_brief"]["suggested_actions"][0]["path"] == "/review"
    assert payload["activation_report"]["title"] == "你的阅读资产已经准备好"
    assert payload["activation_report"]["asset_cards"][0]["value"] == "2"
    assert payload["activation_report"]["top_topics"] == ["长期主义", "现金流"]
    assert payload["activation_report"]["recommended_questions"][0].startswith("我关于「长期主义」")
    assert payload["activation_report"]["primary_action"]["path"] == "/review"
    assert payload["action_queue"][0]["title"] == "完成 6 张卡片"
    assert payload["action_queue"][1]["path"] == "/books/1"
    assert payload["recommended_review"]["title"] == "长期主义"
    assert payload["recommended_review"]["book"]["notes"] == 8
