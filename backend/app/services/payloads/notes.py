from __future__ import annotations

from collections import Counter
from math import ceil
from typing import Any

from ..search.ranker import build_query_rewrite_summary, rank_notes_for_query, rewrite_query


def build_notes_payload(
    data: dict[str, Any],
    book_id: int | None = None,
    query: str = "",
    note_id: int | None = None,
    category: str = "",
    tag: str = "",
    chapter: str = "",
    sort: str = "relevance",
    page: int = 1,
    per_page: int = 120,
) -> dict[str, Any]:
    notes = data["notes"]
    rewrite_info = rewrite_query(query) if query else None

    if book_id is not None:
        notes = [note for note in notes if note["book_id"] == book_id]

    if category:
        notes = [note for note in notes if note["category"] == category]

    if tag:
        notes = [note for note in notes if tag in note["tags"]]

    if chapter:
        notes = [note for note in notes if note["chapter"] == chapter]

    if query:
        scored_notes = rank_notes_for_query(notes, query, rewrite_info=rewrite_info)
        notes = [note for note, _ in scored_notes]

    chapter_counter = Counter(note["chapter"] for note in notes if note["chapter"])
    topic_counter = Counter(tag_name for note in notes for tag_name in note["tags"])
    category_counter = Counter(note["category"] for note in notes if note["category"])
    selected_note = next((note for note in notes if note["id"] == note_id), None) if note_id else None

    if sort == "time_desc":
        notes = sorted(notes, key=lambda note: note.get("timestamp") or "", reverse=True)
    elif sort == "time_asc":
        notes = sorted(notes, key=lambda note: note.get("timestamp") or "")
    elif sort == "length_desc":
        notes = sorted(notes, key=lambda note: len(note.get("excerpt") or ""), reverse=True)

    if selected_note:
        notes = [selected_note] + [note for note in notes if note["id"] != note_id]

    total = len(notes)
    page = max(page, 1)
    per_page = max(1, min(per_page, 200))
    start = (page - 1) * per_page
    end = start + per_page
    paged_notes = notes[start:end]

    insight = {
        "summary": summarize_notes(notes),
        "related_topics": [tag for tag, _ in topic_counter.most_common(5)],
        "related_note": notes[0]["excerpt"][:120] if notes else "",
        "retrieval_mode": "hybrid" if query else "browse",
        "query_rewrite": build_query_rewrite_summary(rewrite_info),
    }

    return {
        "items": paged_notes,
        "insight": insight,
        "filters": {
            "categories": [name for name, _ in category_counter.most_common()],
            "tags": [name for name, _ in topic_counter.most_common(12)],
            "chapters": [name for name, _ in chapter_counter.most_common(20)],
        },
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": max(1, ceil(total / per_page)) if total else 1,
            "has_more": end < total,
        },
    }


def summarize_notes(notes: list[dict[str, Any]]) -> str:
    if not notes:
        return "当前范围内还没有解析出笔记内容。"

    chapters = [note["chapter"] for note in notes if note["chapter"]]
    top_chapters = [name for name, _ in Counter(chapters).most_common(3)]
    sample = "；".join(note["excerpt"][:28] for note in notes[:3])
    if top_chapters:
        return f"当前笔记主要集中在《{'、'.join(top_chapters)}》等章节，摘录内容显示你关注的核心主题包括：{sample}。"
    return f"当前范围内共解析出 {len(notes)} 条高亮，代表性内容包括：{sample}。"
