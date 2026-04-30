from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any

from ..review.payloads import build_review_overview
from ..review.scheduler import REVIEW_MASTERED_THRESHOLD, parse_iso_datetime


def build_analytics_payload(data: dict[str, Any], repository: Any) -> dict[str, Any]:
    books = data["books"]
    notes = data["notes"]
    progress_map = repository.get_review_progress_map([note["id"] for note in notes]) if notes else {}
    review_logs = repository.get_review_log_dates()
    review_state = build_review_overview(data, repository)

    category_counter = Counter(book.get("category") or "未分类" for book in books)
    category_note_counter = Counter(note.get("category") or "未分类" for note in notes)
    topic_counter = build_topic_counter(notes)
    review_funnel = build_review_funnel(notes, progress_map, review_state["due_count"])
    reading_time_rank = build_reading_time_rank(books, notes, progress_map)
    high_value_matrix = build_high_value_matrix(books, notes, progress_map)
    topic_rank = build_topic_rank(topic_counter)
    long_term_metrics = build_long_term_metrics(notes, progress_map, review_state, review_logs)

    return {
        "metrics": build_metrics(books, notes, progress_map, review_state, category_counter),
        "category_preferences": build_category_preferences(category_counter, category_note_counter),
        "preference_radar": build_preference_radar(category_counter, category_note_counter),
        "reading_time_rank": reading_time_rank,
        "high_value_matrix": high_value_matrix,
        "topic_rank": topic_rank,
        "review_funnel": review_funnel,
        "review_progress": {
            "due_count": review_state["due_count"],
            "streak_days": review_state["streak_days"],
            "mastery_rate": review_state["mastery_rate"],
            "reviewed_count": len(progress_map),
            "total_notes": len(notes),
        },
        "reading_timeline": build_reading_timeline(books),
        "author_cloud": build_author_cloud(books, notes),
        "activity_heatmap": build_activity_heatmap(notes, review_logs),
        "long_term_metrics": long_term_metrics,
        "recommendations": build_recommendations(
            reading_time_rank=reading_time_rank,
            high_value_matrix=high_value_matrix,
            topic_rank=topic_rank,
            review_funnel=review_funnel,
            review_state=review_state,
            long_term_metrics=long_term_metrics,
        ),
    }


def build_metrics(
    books: list[dict[str, Any]],
    notes: list[dict[str, Any]],
    progress_map: dict[int, dict[str, Any]],
    review_state: dict[str, Any],
    category_counter: Counter[str],
) -> list[dict[str, str | int]]:
    favorite_category = category_counter.most_common(1)[0][0] if category_counter else "暂无"
    reviewed_count = len(progress_map)
    reviewed_rate = f"{round((reviewed_count / len(notes)) * 100)}%" if notes else "0%"

    return [
        {"label": "阅读书籍", "value": len(books), "hint": "已接入书库总量"},
        {"label": "高亮笔记", "value": len(notes), "hint": "来自微信读书摘录"},
        {"label": "偏好方向", "value": favorite_category, "hint": "按书籍分类统计"},
        {"label": "复习覆盖率", "value": reviewed_rate, "hint": f"已复习 {reviewed_count} / {len(notes)} 条"},
        {"label": "待复习", "value": review_state["due_count"], "hint": "今天应该回看的卡片"},
        {"label": "连续复习", "value": f"{review_state['streak_days']} 天", "hint": "从今天向前连续统计"},
    ]


def build_category_preferences(
    category_counter: Counter[str],
    category_note_counter: Counter[str],
) -> list[dict[str, Any]]:
    total_books = sum(category_counter.values()) or 1
    return [
        {
            "category": category,
            "book_count": count,
            "note_count": category_note_counter.get(category, 0),
            "share": round((count / total_books) * 100),
        }
        for category, count in category_counter.most_common(8)
    ]


def build_preference_radar(
    category_counter: Counter[str],
    category_note_counter: Counter[str],
) -> list[dict[str, Any]]:
    max_score = max(
        (category_counter[category] * 2 + category_note_counter.get(category, 0) for category in category_counter),
        default=1,
    )
    return [
        {
            "label": category,
            "score": round(((count * 2 + category_note_counter.get(category, 0)) / max_score) * 100),
            "book_count": count,
            "note_count": category_note_counter.get(category, 0),
        }
        for category, count in category_counter.most_common(6)
    ]


def build_reading_time_rank(
    books: list[dict[str, Any]],
    notes: list[dict[str, Any]],
    progress_map: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    note_counter = Counter(note["book_id"] for note in notes)
    review_counter = Counter(
        note["book_id"]
        for note in notes
        if note["id"] in progress_map
    )
    ranked_books = sorted(
        books,
        key=lambda book: (
            parse_reading_time_minutes(book.get("reading_time") or ""),
            note_counter.get(book["id"], 0) * 2 + review_counter.get(book["id"], 0) * 3,
            note_counter.get(book["id"], 0),
        ),
        reverse=True,
    )

    return [
        {
            "id": book["id"],
            "title": book["title"],
            "author": book.get("author") or "",
            "category": book.get("category") or "未分类",
            "note_count": note_counter.get(book["id"], 0),
            "reviewed_count": review_counter.get(book["id"], 0),
            "last_read_date": book.get("last_read_date") or book.get("reading_date") or "未知",
            "reading_time": book.get("reading_time") or "",
            "reading_time_minutes": parse_reading_time_minutes(book.get("reading_time") or ""),
            "cover": book.get("cover") or "",
        }
        for book in ranked_books
    ]


def build_high_value_matrix(
    books: list[dict[str, Any]],
    notes: list[dict[str, Any]],
    progress_map: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    note_counter = Counter(note["book_id"] for note in notes)
    review_counter = Counter(note["book_id"] for note in notes if note["id"] in progress_map)
    max_notes = max(note_counter.values(), default=1)
    max_reviews = max(review_counter.values(), default=1)

    ranked = sorted(
        books,
        key=lambda book: note_counter.get(book["id"], 0) * 2 + review_counter.get(book["id"], 0) * 3,
        reverse=True,
    )
    return [
        {
            "id": book["id"],
            "title": book["title"],
            "category": book.get("category") or "未分类",
            "note_count": note_counter.get(book["id"], 0),
            "reviewed_count": review_counter.get(book["id"], 0),
            "x": round((note_counter.get(book["id"], 0) / max_notes) * 100),
            "y": round((review_counter.get(book["id"], 0) / max_reviews) * 100),
            "value_score": note_counter.get(book["id"], 0) * 2 + review_counter.get(book["id"], 0) * 3,
        }
        for book in ranked[:12]
    ]


def build_topic_counter(notes: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for note in notes:
        for tag in note.get("tags", []):
            normalized = str(tag).strip()
            if normalized:
                counter[normalized] += 1
    return counter


def build_topic_rank(topic_counter: Counter[str]) -> list[dict[str, Any]]:
    total = sum(topic_counter.values()) or 1
    return [
        {
            "topic": topic,
            "count": count,
            "share": round((count / total) * 100),
        }
        for topic, count in topic_counter.most_common(12)
    ]


def build_review_funnel(
    notes: list[dict[str, Any]],
    progress_map: dict[int, dict[str, Any]],
    due_count: int,
) -> list[dict[str, Any]]:
    new_count = len([note for note in notes if note["id"] not in progress_map])
    weak_count = len(
        [
            progress
            for progress in progress_map.values()
            if int(progress.get("mastery_score") or 0) <= 1 or progress.get("last_result") in {"low", "medium"}
        ]
    )
    mastered_count = len(
        [
            progress
            for progress in progress_map.values()
            if int(progress.get("mastery_score") or 0) >= REVIEW_MASTERED_THRESHOLD
        ]
    )

    return [
        {"label": "新卡片", "value": new_count, "hint": "还没有复习记录"},
        {"label": "待巩固", "value": weak_count, "hint": "不会/模糊或掌握度偏低"},
        {"label": "今日到期", "value": due_count, "hint": "今天应该回看"},
        {"label": "已掌握", "value": mastered_count, "hint": "掌握度达到阈值"},
    ]


def build_reading_timeline(books: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = defaultdict(lambda: {"book_count": 0, "books": []})
    for book in books:
        date_text = (book.get("last_read_date") or book.get("reading_date") or "").strip()
        parsed = parse_iso_datetime(date_text)
        bucket = parsed.strftime("%Y-%m") if parsed else date_text[:7] if len(date_text) >= 7 else "未知时间"
        buckets[bucket]["book_count"] += 1
        if len(buckets[bucket]["books"]) < 3:
            buckets[bucket]["books"].append(book["title"])

    return [
        {"period": period, **payload}
        for period, payload in sorted(buckets.items(), key=lambda item: item[0], reverse=True)[:12]
    ]


def build_author_cloud(books: list[dict[str, Any]], notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    note_counter = Counter(note["book_id"] for note in notes)
    author_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"book_count": 0, "note_count": 0})

    for book in books:
        author = normalize_author_name(book.get("author") or "")
        if not author:
            continue
        author_stats[author]["book_count"] += 1
        author_stats[author]["note_count"] += note_counter.get(book["id"], 0)

    max_score = max(
        (stats["book_count"] * 2 + stats["note_count"] for stats in author_stats.values()),
        default=1,
    )
    ranked_authors = sorted(
        author_stats.items(),
        key=lambda item: (item[1]["book_count"] * 2 + item[1]["note_count"], item[1]["note_count"]),
        reverse=True,
    )

    return [
        {
            "author": author,
            "book_count": stats["book_count"],
            "note_count": stats["note_count"],
            "weight": round(((stats["book_count"] * 2 + stats["note_count"]) / max_score) * 100),
        }
        for author, stats in ranked_authors[:16]
    ]


def normalize_author_name(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text if text and text not in {"未知", "佚名", "无"} else ""


def build_activity_heatmap(notes: list[dict[str, Any]], review_logs: list[str]) -> list[dict[str, Any]]:
    today = datetime.now().date()
    counters: Counter[str] = Counter()
    for note in notes:
        parsed = parse_iso_datetime(note.get("timestamp") or "")
        if parsed:
            counters[parsed.date().isoformat()] += 1
    for value in review_logs:
        parsed = parse_iso_datetime(value)
        if parsed:
            counters[parsed.date().isoformat()] += 1

    max_count = max(counters.values(), default=1)
    days = []
    for offset in range(34, -1, -1):
        date = today - timedelta(days=offset)
        count = counters.get(date.isoformat(), 0)
        days.append(
            {
                "date": date.isoformat(),
                "label": date.strftime("%m-%d"),
                "count": count,
                "level": 0 if count == 0 else max(1, min(4, round((count / max_count) * 4))),
            }
        )
    return days


def build_long_term_metrics(
    notes: list[dict[str, Any]],
    progress_map: dict[int, dict[str, Any]],
    review_state: dict[str, Any],
    review_logs: list[str],
) -> list[dict[str, Any]]:
    reviewed_count = len(progress_map)
    total_notes = len(notes)
    mastered_count = len(
        [
            progress
            for progress in progress_map.values()
            if int(progress.get("mastery_score") or 0) >= REVIEW_MASTERED_THRESHOLD
        ]
    )
    active_days = {
        parsed.date().isoformat()
        for value in review_logs
        if (parsed := parse_iso_datetime(value)) is not None
    }
    weak_count = len(
        [
            progress
            for progress in progress_map.values()
            if int(progress.get("mastery_score") or 0) <= 1 or progress.get("last_result") in {"low", "medium"}
        ]
    )
    return [
        {
            "label": "连续复习",
            "value": f"{review_state['streak_days']} 天",
            "score": min(100, int(review_state["streak_days"]) * 10),
            "hint": "持续复习是长期记忆的底座",
        },
        {
            "label": "复习覆盖",
            "value": f"{round((reviewed_count / total_notes) * 100) if total_notes else 0}%",
            "score": round((reviewed_count / total_notes) * 100) if total_notes else 0,
            "hint": f"已触达 {reviewed_count} / {total_notes} 条摘录",
        },
        {
            "label": "掌握沉淀",
            "value": f"{round((mastered_count / reviewed_count) * 100) if reviewed_count else 0}%",
            "score": round((mastered_count / reviewed_count) * 100) if reviewed_count else 0,
            "hint": f"{mastered_count} 条卡片进入较高掌握度",
        },
        {
            "label": "近月活跃",
            "value": f"{len(active_days)} 天",
            "score": min(100, round((len(active_days) / 30) * 100)),
            "hint": "近 30 天有复习记录的天数",
        },
        {
            "label": "待巩固压力",
            "value": f"{weak_count} 条",
            "score": max(0, 100 - min(100, weak_count * 4)),
            "hint": "分数越高代表待巩固压力越低",
        },
    ]


def build_recommendations(
    *,
    reading_time_rank: list[dict[str, Any]],
    high_value_matrix: list[dict[str, Any]],
    topic_rank: list[dict[str, Any]],
    review_funnel: list[dict[str, Any]],
    review_state: dict[str, Any],
    long_term_metrics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    top_value_book = high_value_matrix[0] if high_value_matrix else None
    top_topic = topic_rank[0] if topic_rank else None
    weak_count = next((item["value"] for item in review_funnel if item["label"] == "待巩固"), 0)
    new_count = next((item["value"] for item in review_funnel if item["label"] == "新卡片"), 0)
    coverage_metric = next((item for item in long_term_metrics if item["label"] == "复习覆盖"), None)

    if top_value_book:
        recommendations.append(
            {
                "type": "book",
                "title": f"优先回看《{top_value_book['title']}》",
                "reason": (
                    f"它有 {top_value_book['note_count']} 条笔记、"
                    f"{top_value_book['reviewed_count']} 次复习记录，是当前最值得复盘的高价值书。"
                ),
                "action_label": "打开这本书",
                "path": f"/books/{top_value_book['id']}",
                "priority": "high",
            }
        )
    elif reading_time_rank:
        book = reading_time_rank[0]
        recommendations.append(
            {
                "type": "book",
                "title": f"从《{book['title']}》开始整理",
                "reason": f"它在阅读时长榜靠前，已经投入 {book['reading_time_minutes']} 分钟，适合作为复盘入口。",
                "action_label": "打开这本书",
                "path": f"/books/{book['id']}",
                "priority": "medium",
            }
        )

    if top_topic:
        recommendations.append(
            {
                "type": "topic",
                "title": f"围绕「{top_topic['topic']}」做一次主题整理",
                "reason": f"这个主题出现 {top_topic['count']} 次，占当前主题笔记约 {top_topic['share']}%。",
                "action_label": "追问这个主题",
                "path": f"/qa?preset=我关于「{top_topic['topic']}」的笔记里，最值得回看的观点是什么？",
                "priority": "medium",
            }
        )

    if weak_count:
        recommendations.append(
            {
                "type": "review",
                "title": f"先处理 {min(int(weak_count), 10)} 张待巩固卡片",
                "reason": "这些卡片上次标记为不会或模糊，短时间内再碰一次更容易留下痕迹。",
                "action_label": "练待巩固",
                "path": "/review?queue=weak",
                "priority": "high",
            }
        )
    elif int(review_state.get("due_count") or 0):
        recommendations.append(
            {
                "type": "review",
                "title": "完成今天的一小组复习",
                "reason": f"当前有 {review_state['due_count']} 张到期卡片，不用清空，先完成 5 到 10 张就好。",
                "action_label": "开始复习",
                "path": "/review",
                "priority": "medium",
            }
        )
    elif new_count:
        recommendations.append(
            {
                "type": "review",
                "title": "从新卡片建立第一轮印象",
                "reason": f"还有 {new_count} 条摘录没有复习记录，适合挑一小组先建立初始记忆。",
                "action_label": "练新卡片",
                "path": "/review?queue=new",
                "priority": "medium",
            }
        )

    if coverage_metric and int(coverage_metric.get("score") or 0) < 20:
        recommendations.append(
            {
                "type": "coverage",
                "title": "复习覆盖率还在早期",
                "reason": "现在不适合追求完整清空，建议每天只做一小组，让系统逐步摸到你的高价值摘录。",
                "action_label": "查看复习计划",
                "path": "/review",
                "priority": "low",
            }
        )

    return recommendations[:4]


def parse_reading_time_minutes(value: str) -> int:
    text = str(value or "").strip()
    if not text:
        return 0
    if text.isdigit():
        return int(text)

    hours = 0
    minutes = 0
    hour_match = re.search(r"(\d+(?:\.\d+)?)\s*(小时|时|h|hour)", text, re.I)
    minute_match = re.search(r"(\d+(?:\.\d+)?)\s*(分钟|分|min|minute)", text, re.I)
    if hour_match:
        hours = round(float(hour_match.group(1)) * 60)
    if minute_match:
        minutes = round(float(minute_match.group(1)))
    if hours or minutes:
        return hours + minutes

    number_match = re.search(r"\d+", text)
    return int(number_match.group(0)) if number_match else 0
