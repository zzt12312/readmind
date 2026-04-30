from __future__ import annotations

from collections import Counter
from typing import Any


def build_dashboard_payload(data: dict[str, Any], review_state: dict[str, Any]) -> dict[str, Any]:
    books = data["books"]
    notes = data["notes"]
    stats = data["stats"]

    recent_books = sorted(
        books,
        key=lambda item: item.get("last_read_date") or item.get("reading_date") or "",
        reverse=True,
    )[:5]
    suggested_review_count = min(max(review_state["due_count"], 0), 10)

    return {
        "metrics": [
            {"label": "书籍数", "value": stats["book_count"], "hint": "已接入真实 Obsidian 书单"},
            {"label": "笔记数", "value": stats["note_count"], "hint": "来自微信读书高亮划线"},
            {"label": "分类数", "value": stats["category_count"], "hint": "按目录自动归类"},
            {
                "label": "今日建议复习",
                "value": suggested_review_count,
                "hint": f"总待复习 {review_state['due_count']} 条，建议先完成这一小组",
            },
        ],
        "recent_books": [
            {
                "id": book["id"],
                "title": book["title"],
                "notes": book["notes"],
                "updated": book.get("last_read_date") or book.get("reading_date") or "未知",
                "cover": book.get("cover") or "",
            }
            for book in recent_books
        ],
        "active_topics": stats["top_topics"] or [book["category"] for book in books[:5]],
        "total_notes": len(notes),
        "review_summary": {
            "suggested_count": suggested_review_count,
            "due_count": review_state["due_count"],
            "streak_days": review_state["streak_days"],
            "mastery_rate": review_state["mastery_rate"],
        },
        "activation_report": build_activation_report(books, notes, stats, review_state, recent_books, suggested_review_count),
        "daily_brief": build_daily_brief(books, notes, stats, review_state, suggested_review_count),
        "action_queue": build_action_queue(books, stats, review_state, suggested_review_count),
        "recommended_review": build_recommended_review(books, stats),
    }


def build_daily_brief(
    books: list[dict[str, Any]],
    notes: list[dict[str, Any]],
    stats: dict[str, Any],
    review_state: dict[str, Any],
    suggested_review_count: int,
) -> dict[str, Any]:
    """Build a rule-based daily reading brief that works without AI services."""

    top_topics = [str(topic) for topic in stats.get("top_topics", []) if str(topic).strip()][:3]
    category_counter = Counter(book.get("category") or "未分类" for book in books)
    preferred_topics = top_topics or [category for category, _ in category_counter.most_common(3)]
    favorite_topic = preferred_topics[0] if preferred_topics else "阅读"
    featured_book = pick_featured_book(books)

    summary = build_daily_brief_summary(
        favorite_topic=favorite_topic,
        topics=preferred_topics,
        note_count=len(notes),
        review_state=review_state,
        featured_book=featured_book,
    )

    feedback_items = [
        {
            "label": "今日建议",
            "value": f"{suggested_review_count} 张",
            "hint": f"当前还有 {review_state['due_count']} 张待回看，先完成一小组就好",
        },
        {
            "label": "连续复习",
            "value": f"{review_state['streak_days']} 天",
            "hint": f"当前掌握率 {review_state['mastery_rate']}，继续保持节奏",
        },
        {
            "label": "近期主题",
            "value": favorite_topic,
            "hint": "由高频标签和书籍分类综合生成",
        },
    ]
    if featured_book:
        feedback_items.append(
            {
                "label": "值得回看",
                "value": featured_book["title"],
                "hint": f"这本书沉淀了 {featured_book.get('notes', 0)} 条笔记",
            }
        )

    suggested_actions = [
        {"label": "开始今日复习", "type": "review", "path": "/review"},
        {"label": "查看高价值笔记", "type": "notes", "path": "/notes"},
        {"label": "打开数据看板", "type": "analytics", "path": "/analytics"},
    ]
    if featured_book:
        suggested_actions.insert(
            1,
            {"label": "回看推荐书籍", "type": "book", "path": f"/books/{featured_book['id']}"},
        )

    return {
        "title": "今日阅读回顾",
        "summary": summary,
        "feedback_items": feedback_items,
        "suggested_actions": suggested_actions[:4],
        "highlights": {
            "topics": preferred_topics[:5],
            "book": (
                {
                    "id": featured_book["id"],
                    "title": featured_book["title"],
                }
                if featured_book
                else None
            ),
            "author": pick_favorite_author(books),
        },
    }


def build_activation_report(
    books: list[dict[str, Any]],
    notes: list[dict[str, Any]],
    stats: dict[str, Any],
    review_state: dict[str, Any],
    recent_books: list[dict[str, Any]],
    suggested_review_count: int,
) -> dict[str, Any]:
    """Summarize the first visible value after a vault sync."""

    top_topics = [str(topic) for topic in stats.get("top_topics", []) if str(topic).strip()][:5]
    featured_book = pick_featured_book(books)
    recent_titles = [book["title"] for book in recent_books[:3] if book.get("title")]
    prompt_topic = top_topics[0] if top_topics else "最近阅读"
    prompt_book = featured_book["title"] if featured_book else (recent_titles[0] if recent_titles else "")

    questions = [
        f"我关于「{prompt_topic}」的笔记里，最值得回看的 3 个观点是什么？",
        "哪些摘录适合加入今天的复习？",
    ]
    if prompt_book:
        questions.insert(1, f"《{prompt_book}》里有哪些可以继续追问的问题？")

    asset_cards = [
        {
            "label": "已识别书籍",
            "value": str(stats.get("book_count", len(books))),
            "hint": "来自你的阅读目录",
        },
        {
            "label": "可追问摘录",
            "value": str(stats.get("note_count", len(notes))),
            "hint": "会作为回答依据",
        },
        {
            "label": "高频主题",
            "value": str(len(top_topics)),
            "hint": "适合继续整理",
        },
        {
            "label": "今日小组",
            "value": f"{suggested_review_count} 张",
            "hint": f"总待复习 {review_state['due_count']} 张",
        },
    ]

    return {
        "title": "你的阅读资产已经准备好",
        "summary": build_activation_summary(stats, top_topics, recent_titles),
        "asset_cards": asset_cards,
        "top_topics": top_topics,
        "recent_books": recent_titles,
        "recommended_questions": questions[:3],
        "primary_action": {
            "label": "开始 5 分钟回看",
            "path": "/review",
        },
        "secondary_action": {
            "label": "问自己的笔记",
            "path": "/qa",
        },
    }


def build_activation_summary(stats: dict[str, Any], topics: list[str], recent_titles: list[str]) -> str:
    topic_text = "、".join(topics[:3]) if topics else "你的阅读主题"
    book_text = "、".join(f"《{title}》" for title in recent_titles[:2]) if recent_titles else "最近同步的书"
    return (
        f"系统已整理 {stats.get('book_count', 0)} 本书、{stats.get('note_count', 0)} 条摘录。"
        f"可以先从 {book_text} 和「{topic_text}」开始追问，把旧划线重新变成可用线索。"
    )


def build_daily_brief_summary(
    *,
    favorite_topic: str,
    topics: list[str],
    note_count: int,
    review_state: dict[str, Any],
    featured_book: dict[str, Any] | None,
) -> str:
    topic_text = "、".join(topics[:3]) if topics else favorite_topic
    book_text = f"《{featured_book['title']}》" if featured_book else "最近整理的书籍"
    due_count = int(review_state.get("due_count") or 0)

    if due_count > 0:
        return (
            f"最近你主要在关注「{topic_text}」，已经沉淀 {note_count} 条摘录。"
            f"今天可以先完成一组复习，再回看 {book_text}，把输入变成可复用的知识。"
        )
    return (
        f"最近你主要在关注「{topic_text}」，已沉淀 {note_count} 条摘录。"
        f"今天没有紧急到期卡片，适合回看 {book_text} 或继续整理新的阅读线索。"
    )


def pick_featured_book(books: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not books:
        return None
    return max(
        books,
        key=lambda book: (
            int(book.get("notes") or 0),
            str(book.get("last_read_date") or book.get("reading_date") or ""),
        ),
    )


def build_action_queue(
    books: list[dict[str, Any]],
    stats: dict[str, Any],
    review_state: dict[str, Any],
    suggested_review_count: int,
) -> list[dict[str, str]]:
    featured_book = pick_featured_book(books)
    top_topic = (stats.get("top_topics") or ["全部笔记"])[0]

    queue = [
        {
            "label": "今日复习",
            "title": f"完成 {suggested_review_count} 张卡片",
            "hint": f"待回看 {review_state['due_count']} 张，先做一小组保持节奏",
            "path": "/review",
            "accent": "primary",
        },
        {
            "label": "继续整理",
            "title": featured_book["title"] if featured_book else "打开笔记工作台",
            "hint": (
                f"这本书有 {featured_book.get('notes', 0)} 条摘录，可以继续二次整理"
                if featured_book
                else "从全部笔记里继续筛选、搜索和生成洞察"
            ),
            "path": f"/books/{featured_book['id']}" if featured_book else "/notes",
            "accent": "warm",
        },
        {
            "label": "查看洞察",
            "title": f"关注「{top_topic}」",
            "hint": "去数据看板看看阅读偏好、作者词云和复习趋势",
            "path": "/analytics",
            "accent": "calm",
        },
    ]
    return queue


def build_recommended_review(books: list[dict[str, Any]], stats: dict[str, Any]) -> dict[str, Any]:
    featured_book = pick_featured_book(books)
    top_topics = [str(topic) for topic in stats.get("top_topics", []) if str(topic).strip()][:4]
    if not featured_book:
        return {
            "title": "从最近笔记开始回看",
            "reason": "还没有足够的书籍数据时，先从笔记工作台进入，筛选一个主题做整理。",
            "path": "/notes",
            "topics": top_topics,
            "book": None,
        }

    return {
        "title": featured_book["title"],
        "reason": f"这本书目前沉淀了 {featured_book.get('notes', 0)} 条笔记，是今天最适合重新打开的知识入口。",
        "path": f"/books/{featured_book['id']}",
        "topics": top_topics or [featured_book.get("category") or "未分类"],
        "book": {
            "id": featured_book["id"],
            "title": featured_book["title"],
            "author": featured_book.get("author") or "",
            "notes": featured_book.get("notes", 0),
            "cover": featured_book.get("cover") or "",
        },
    }


def pick_favorite_author(books: list[dict[str, Any]]) -> str:
    authors = [str(book.get("author") or "").strip() for book in books]
    authors = [author for author in authors if author and author not in {"未知", "佚名", "无"}]
    if not authors:
        return ""
    return Counter(authors).most_common(1)[0][0]
