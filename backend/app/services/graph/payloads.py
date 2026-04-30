"""Knowledge graph payload builders.

The frontend supports two graph modes:
- category mode: group books by reading category and connect categories through
  shared topical tags;
- topic mode: promote recurring note tags/chapters to topic nodes and connect
  topics through co-occurrence and shared books.

This module returns presentation-ready payloads. It does not read the vault or
schedule jobs; `graph_analysis_service.py` handles orchestration.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import quote

TOPIC_STOPWORDS = {
    "",
    "未分章节",
    "微信读书",
    "书籍阅读",
    "前言",
    "后记",
    "自序",
    "序言",
    "中文版序",
    "小结",
    "结论",
}

CORE_TOPIC_KEYWORDS = {
    "长期主义",
    "系统",
    "决策",
    "情绪",
    "幸福",
    "习惯",
    "注意力",
    "财富",
    "学习",
    "行动",
}

TIME_SCOPE_OPTIONS = [
    {"label": "全部时间", "value": "all"},
    {"label": "最近 90 天", "value": "recent-90"},
    {"label": "最近 180 天", "value": "recent-180"},
    {"label": "最近 1 年", "value": "recent-365"},
]

GRAPH_MODE_OPTIONS = [
    {"label": "领域聚类", "value": "category"},
    {"label": "知识主题", "value": "topic"},
]


def parse_book_date(value: str) -> datetime | None:
    text = (value or "").strip()
    if not text or text == "1970-01-01":
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def filter_graph_source(
    data: dict[str, Any],
    category: str = "",
    book_id: int | None = None,
    time_scope: str = "all",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    all_books = data["books"]
    books = all_books

    # Filter at book level first so the graph never keeps notes from excluded books.
    if category:
        books = [book for book in books if book.get("category") == category]

    if book_id is not None:
        books = [book for book in books if book.get("id") == book_id]

    if time_scope != "all":
        days_map = {
            "recent-90": 90,
            "recent-180": 180,
            "recent-365": 365,
        }
        days = days_map.get(time_scope)
        if days:
            available_dates = [
                parse_book_date(book.get("last_read_date") or "")
                or parse_book_date(book.get("reading_date") or "")
                for book in books
            ]
            reference_date = max((date for date in available_dates if date is not None), default=datetime.now())
            threshold = reference_date - timedelta(days=days)
            books = [
                book
                for book in books
                if (
                    (
                        parse_book_date(book.get("last_read_date") or "")
                        or parse_book_date(book.get("reading_date") or "")
                    )
                    and (
                        parse_book_date(book.get("last_read_date") or "")
                        or parse_book_date(book.get("reading_date") or "")
                    )
                    >= threshold
                )
            ]

    selected_book_ids = {book["id"] for book in books}
    notes = [note for note in data["notes"] if note["book_id"] in selected_book_ids]
    return all_books, books, notes


def prune_graph_links(
    links: list[dict[str, Any]],
    *,
    top_k_per_node: int = 2,
    min_value: int = 1,
    require_mutual: bool = False,
) -> list[dict[str, Any]]:
    if not links:
        return []

    filtered_links = [link for link in links if int(link.get("value", 0)) >= min_value]
    adjacency: dict[str, list[dict[str, Any]]] = {}
    for link in filtered_links:
        adjacency.setdefault(str(link["source"]), []).append(link)
        adjacency.setdefault(str(link["target"]), []).append(link)

    kept_pairs: Counter[tuple[str, str]] = Counter()
    for node_links in adjacency.values():
        ranked_links = sorted(
            node_links,
            key=lambda item: (
                int(item.get("value", 0)),
                int(item.get("co_occurrence", 0)),
                int(item.get("shared_books", 0)),
            ),
            reverse=True,
        )
        for link in ranked_links[:top_k_per_node]:
            pair = tuple(sorted((str(link["source"]), str(link["target"]))))
            kept_pairs[pair] += 1

    return [
        link
        for link in filtered_links
        if kept_pairs[tuple(sorted((str(link["source"]), str(link["target"]))))]
        >= (2 if require_mutual else 1)
    ]


def is_topic_candidate(tag: str) -> bool:
    normalized = (tag or "").strip()
    if not normalized or normalized in TOPIC_STOPWORDS:
        return False
    if len(normalized) < 2:
        return False
    return True


def build_topic_graph_payload(data: dict[str, Any]) -> dict[str, Any]:
    return build_filtered_topic_graph_payload(data)


def build_filtered_topic_graph_payload(
    data: dict[str, Any],
    category: str = "",
    book_id: int | None = None,
    time_scope: str = "all",
) -> dict[str, Any]:
    """Build a tag/chapter-based topic graph for the selected reading scope."""
    all_books, books, notes = filter_graph_source(
        data,
        category=category,
        book_id=book_id,
        time_scope=time_scope,
    )
    book_lookup = {book["id"]: book for book in books}
    category_names = {book["category"] for book in books if book.get("category")}
    topic_stats: dict[str, dict[str, Any]] = {}
    edge_weights: Counter[tuple[str, str]] = Counter()

    for note in notes:
        candidate_topics: list[str] = []
        for tag in note.get("tags", []):
            normalized = (tag or "").strip()
            if normalized == note.get("category") or normalized in category_names:
                continue
            if is_topic_candidate(normalized) and normalized not in candidate_topics:
                candidate_topics.append(normalized)

        chapter = (note.get("chapter") or "").strip()
        if is_topic_candidate(chapter) and chapter not in candidate_topics:
            candidate_topics.append(chapter)

        if not candidate_topics:
            continue

        for topic in candidate_topics:
            stats = topic_stats.setdefault(
                topic,
                {
                    "topic": topic,
                    "note_ids": set(),
                    "book_ids": set(),
                    "books": Counter(),
                    "chapters": Counter(),
                    "samples": [],
                },
            )
            stats["note_ids"].add(note["id"])
            stats["book_ids"].add(note["book_id"])
            stats["books"][note["book_id"]] += 1
            if note.get("chapter"):
                stats["chapters"][note["chapter"]] += 1
            if len(stats["samples"]) < 4:
                stats["samples"].append(
                    {
                        "note_id": note["id"],
                        "book_id": note["book_id"],
                        "book_title": note["book_title"],
                        "excerpt": note["excerpt"][:120],
                    }
                )

        for index, source in enumerate(candidate_topics):
            for target in candidate_topics[index + 1 :]:
                key = tuple(sorted((source, target)))
                edge_weights[key] += 1

    minimum_books = 1 if book_id is not None else 2
    filtered_topics = [
        item
        for item in topic_stats.values()
        if item["topic"] in CORE_TOPIC_KEYWORDS or len(item["book_ids"]) >= minimum_books
        if len(item["book_ids"]) <= max(12, int(len(books) * 0.35) if books else 12)
    ]
    ranked_topics = sorted(
        filtered_topics,
        key=lambda item: (len(item["note_ids"]), len(item["book_ids"])),
        reverse=True,
    )[:18]
    selected_topic_names = {item["topic"] for item in ranked_topics}

    graph_links: list[dict[str, Any]] = []
    for (source, target), weight in edge_weights.items():
        if source not in selected_topic_names or target not in selected_topic_names:
            continue

        shared_books = len(topic_stats[source]["book_ids"] & topic_stats[target]["book_ids"])
        if weight < 2 and shared_books < 2:
            continue

        graph_links.append(
            {
                "source": source,
                "target": target,
                "value": weight + shared_books,
                "co_occurrence": weight,
                "shared_books": shared_books,
            }
        )

    clusters, topic_to_cluster = build_topic_clusters(ranked_topics, topic_stats, graph_links, book_lookup)
    nodes = [
        {
            "id": topic["topic"],
            "name": topic["topic"],
            "value": len(topic["note_ids"]),
            "note_count": len(topic["note_ids"]),
            "book_count": len(topic["book_ids"]),
            "cluster_id": topic_to_cluster.get(topic["topic"], -1),
        }
        for topic in ranked_topics
    ]

    graph_links = prune_graph_links(
        graph_links,
        top_k_per_node=2 if book_id is None else 1,
        min_value=8 if book_id is None else 1,
        require_mutual=False,
    )

    return {
        "overview": {
            "topic_count": len(nodes),
            "cluster_count": len(clusters),
            "edge_count": len(graph_links),
            "book_count": len({book_id for topic in ranked_topics for book_id in topic["book_ids"]}),
        },
        "filters": build_graph_filters(
            all_books,
            category=category,
            book_id=book_id,
            time_scope=time_scope,
            mode="topic",
        ),
        "clusters": clusters,
        "graph": {
            "nodes": nodes,
            "links": graph_links,
        },
    }


def build_topic_clusters(
    ranked_topics: list[dict[str, Any]],
    topic_stats: dict[str, dict[str, Any]],
    graph_links: list[dict[str, Any]],
    book_lookup: dict[int, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    assigned_topics: set[str] = set()
    clusters: list[dict[str, Any]] = []
    topic_to_cluster: dict[str, int] = {}

    link_lookup: dict[str, list[dict[str, Any]]] = {topic["topic"]: [] for topic in ranked_topics}
    for link in graph_links:
        link_lookup[link["source"]].append(link)
        link_lookup[link["target"]].append(link)

    for topic in ranked_topics:
        topic_name = topic["topic"]
        if topic_name in assigned_topics:
            continue

        related_topics = []
        for link in sorted(link_lookup.get(topic_name, []), key=lambda item: item["value"], reverse=True):
            neighbor = link["target"] if link["source"] == topic_name else link["source"]
            if neighbor in assigned_topics or neighbor == topic_name:
                continue
            related_topics.append(neighbor)
            if len(related_topics) >= 4:
                break

        ranked_component = [topic_name, *related_topics]
        cluster_index = len(clusters)
        for name in ranked_component:
            assigned_topics.add(name)
            topic_to_cluster[name] = cluster_index

        cluster_book_ids: set[int] = set()
        note_count = 0
        sample_books: list[dict[str, Any]] = []
        samples: list[dict[str, Any]] = []
        for name in ranked_component:
            stats = topic_stats[name]
            cluster_book_ids.update(stats["book_ids"])
            note_count += len(stats["note_ids"])
            for sample in stats["samples"]:
                if len(samples) < 4:
                    samples.append(sample)

        top_book_ids = [
            book_id
            for book_id, _ in sum((topic_stats[name]["books"] for name in ranked_component), Counter()).most_common(4)
        ]
        for candidate_book_id in top_book_ids:
            book = book_lookup.get(candidate_book_id)
            if not book:
                continue
            sample_books.append(
                {
                    "id": book["id"],
                    "title": book["title"],
                    "cover": book.get("cover") or "",
                    "notes": book["notes"],
                }
            )

        clusters.append(
            {
                "id": cluster_index,
                "name": ranked_component[0],
                "topics": ranked_component,
                "note_count": note_count,
                "book_count": len(cluster_book_ids),
                "sample_books": sample_books,
                "sample_excerpts": samples,
                "actions": build_cluster_actions(
                    ranked_component[0],
                    ranked_component,
                    mode="topic",
                ),
            }
        )

    return clusters, topic_to_cluster


def build_category_graph_payload(
    data: dict[str, Any],
    category: str = "",
    book_id: int | None = None,
    time_scope: str = "all",
) -> dict[str, Any]:
    """Build a category-first graph that is easier to read at library scale."""
    all_books, books, notes = filter_graph_source(
        data,
        category=category,
        book_id=book_id,
        time_scope=time_scope,
    )

    category_groups: dict[str, dict[str, Any]] = {}
    for book in books:
        category_name = (book.get("category") or "未分类").strip()
        group = category_groups.setdefault(
            category_name,
            {
                "books": [],
                "book_ids": set(),
                "topical_tags": Counter(),
                "tag_books": {},
                "samples": [],
                "note_count": 0,
            },
        )
        group["books"].append(book)
        group["book_ids"].add(book["id"])

    for note in notes:
        category_name = (note.get("category") or "未分类").strip()
        group = category_groups.get(category_name)
        if not group:
            continue
        group["note_count"] += 1
        for tag in note.get("tags", []):
            normalized = (tag or "").strip()
            if not is_topic_candidate(normalized):
                continue
            if normalized == category_name:
                continue
            group["topical_tags"][normalized] += 1
            tag_books = group["tag_books"].setdefault(normalized, set())
            tag_books.add(note["book_id"])
        if len(group["samples"]) < 4:
            group["samples"].append(
                {
                    "note_id": note["id"],
                    "book_id": note["book_id"],
                    "book_title": note["book_title"],
                    "excerpt": note["excerpt"][:120],
                }
            )

    clusters, nodes, category_tag_sets = build_category_clusters(category_groups)
    links = build_category_links(clusters, category_tag_sets, book_id=book_id)

    return {
        "overview": {
            "topic_count": len(nodes),
            "cluster_count": len(clusters),
            "edge_count": len(links),
            "book_count": len(books),
        },
        "filters": build_graph_filters(
            all_books,
            category=category,
            book_id=book_id,
            time_scope=time_scope,
            mode="category",
        ),
        "clusters": clusters,
        "graph": {
            "nodes": nodes,
            "links": links,
        },
    }


def build_category_clusters(
    category_groups: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, set[str]]]:
    ranked_categories = sorted(
        category_groups.items(),
        key=lambda item: (len(item[1]["book_ids"]), item[1]["note_count"]),
        reverse=True,
    )

    clusters: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []
    category_tag_sets: dict[str, set[str]] = {}

    for index, (category_name, group) in enumerate(ranked_categories):
        top_books = sorted(
            group["books"],
            key=lambda book: (book.get("last_read_date") or book.get("reading_date") or "", book["notes"]),
            reverse=True,
        )[:4]
        top_tags = [
            tag
            for tag, _ in group["topical_tags"].most_common()
            if tag in CORE_TOPIC_KEYWORDS or len(group["tag_books"].get(tag, set())) >= 2
        ][:6]
        if not top_tags:
            top_tags = [tag for tag, _ in group["topical_tags"].most_common(6)]
        category_tag_sets[category_name] = set(top_tags)

        clusters.append(
            {
                "id": index,
                "name": category_name,
                "topics": top_tags,
                "note_count": group["note_count"],
                "book_count": len(group["book_ids"]),
                "sample_books": [
                    {
                        "id": book["id"],
                        "title": book["title"],
                        "cover": book.get("cover") or "",
                        "notes": book["notes"],
                    }
                    for book in top_books
                ],
                "sample_excerpts": group["samples"],
                "actions": build_cluster_actions(
                    category_name,
                    top_tags,
                    mode="category",
                ),
            }
        )
        nodes.append(
            {
                "id": category_name,
                "name": category_name,
                "value": max(1, len(group["book_ids"])),
                "note_count": group["note_count"],
                "book_count": len(group["book_ids"]),
                "cluster_id": index,
            }
        )

    return clusters, nodes, category_tag_sets


def build_category_links(
    clusters: list[dict[str, Any]],
    category_tag_sets: dict[str, set[str]],
    *,
    book_id: int | None = None,
) -> list[dict[str, Any]]:
    links: list[dict[str, Any]] = []
    for left_index, left_cluster in enumerate(clusters):
        for right_cluster in clusters[left_index + 1 :]:
            left_tags = category_tag_sets.get(left_cluster["name"], set())
            right_tags = category_tag_sets.get(right_cluster["name"], set())
            shared_tags = sorted(left_tags & right_tags)
            if len(shared_tags) < 2:
                continue
            links.append(
                {
                    "source": left_cluster["name"],
                    "target": right_cluster["name"],
                    "value": len(shared_tags),
                    "co_occurrence": len(shared_tags),
                    "shared_books": 0,
                }
            )

    return prune_graph_links(
        links,
        top_k_per_node=2 if book_id is None else 1,
        min_value=2,
        require_mutual=True,
    )


def build_graph_filters(
    all_books: list[dict[str, Any]],
    *,
    category: str,
    book_id: int | None,
    time_scope: str,
    mode: str,
) -> dict[str, Any]:
    return {
        "selected": {
            "category": category,
            "book_id": book_id,
            "time_scope": time_scope,
            "mode": mode,
        },
        "categories": sorted({book["category"] for book in all_books if book.get("category")}),
        "books": [
            {
                "id": book["id"],
                "title": book["title"],
                "category": book.get("category") or "",
            }
            for book in all_books
        ],
        "time_scopes": TIME_SCOPE_OPTIONS,
        "modes": GRAPH_MODE_OPTIONS,
    }


def build_cluster_actions(name: str, topics: list[str], *, mode: str) -> list[dict[str, str]]:
    focus_topic = topics[0] if topics else name
    encoded_name = quote(name)
    encoded_topic = quote(focus_topic)
    question = (
        f"我关于「{focus_topic}」的笔记里，最值得回看的观点是什么？"
        if mode == "topic"
        else f"我在「{name}」这个阅读领域里，最值得继续整理的问题是什么？"
    )

    actions = [
        {
            "label": "追问这个主题",
            "description": "带着当前主题去问答页，让 AI 基于原始摘录整理回答。",
            "path": f"/qa?preset={quote(question)}",
            "type": "qa",
        },
        {
            "label": "查看相关笔记",
            "description": "回到笔记工作台，直接筛选这个主题下的原始摘录。",
            "path": f"/notes?tag={encoded_topic}" if mode == "topic" else f"/notes?category={encoded_name}",
            "type": "notes",
        },
    ]
    if focus_topic:
        actions.append(
            {
                "label": "围绕主题复习",
                "description": "把这个主题变成一组可完成的复习卡片。",
                "path": f"/review?tag={encoded_topic}",
                "type": "review",
            }
        )

    return actions
