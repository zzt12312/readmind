from __future__ import annotations

from app.services.graph.payloads import build_category_graph_payload, build_filtered_topic_graph_payload


def make_book(book_id: int, title: str, category: str) -> dict[str, object]:
    return {
        "id": book_id,
        "title": title,
        "category": category,
        "notes": 3,
        "reading_date": "2026-04-01",
        "last_read_date": "2026-04-20",
        "cover": "",
    }


def make_note(note_id: int, book_id: int, book_title: str, category: str, tags: list[str]) -> dict[str, object]:
    return {
        "id": note_id,
        "book_id": book_id,
        "book_title": book_title,
        "category": category,
        "chapter": "行动系统",
        "excerpt": "把长期主义落实到每天可以执行的系统里。",
        "tags": tags,
    }


def test_topic_graph_clusters_include_action_entry_points() -> None:
    data = {
        "books": [
            make_book(1, "长期主义 A", "商业"),
            make_book(2, "长期主义 B", "心理"),
        ],
        "notes": [
            make_note(1, 1, "长期主义 A", "商业", ["长期主义", "行动"]),
            make_note(2, 2, "长期主义 B", "心理", ["长期主义", "系统"]),
        ],
    }

    payload = build_filtered_topic_graph_payload(data)
    cluster = payload["clusters"][0]

    assert cluster["actions"][0]["type"] == "qa"
    assert cluster["actions"][1]["path"].startswith("/notes?tag=")
    assert cluster["actions"][2]["path"].startswith("/review?tag=")


def test_category_graph_clusters_include_category_note_action() -> None:
    data = {
        "books": [
            make_book(1, "商业书", "商业"),
            make_book(2, "心理书", "心理"),
        ],
        "notes": [
            make_note(1, 1, "商业书", "商业", ["长期主义", "系统"]),
            make_note(2, 2, "心理书", "心理", ["长期主义", "系统"]),
        ],
    }

    payload = build_category_graph_payload(data)
    cluster = payload["clusters"][0]

    assert cluster["actions"][0]["path"].startswith("/qa?preset=")
    assert cluster["actions"][1]["path"].startswith("/notes?category=")
