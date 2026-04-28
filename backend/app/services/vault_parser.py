from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import ceil
from pathlib import Path
from typing import Any

from .embedding_service import EmbeddingService, hash_vectorize

VAULT_ROOT = Path("/Users/taozhang/Documents/Obsidian Vault/书籍阅读")
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DATA_DIR / "readmind_cache.db"
SECTION_HIGHLIGHTS = "# 高亮划线"
SECTION_READING_NOTES = "# 读书笔记"
SECTION_BOOK_REVIEW = "# 本书评论"

STOPWORDS = {
    "什么",
    "哪些",
    "内容",
    "这本书",
    "这本",
    "其中",
    "关于",
    "一下",
    "总结",
    "帮我",
    "记录",
    "提到",
    "说了",
    "只看",
    "只检索",
    "笔记",
    "我的",
}

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
QUERY_REWRITE_RULES = {
    "长期主义": {
        "triggers": ["长期主义", "长期", "长远", "复利", "延迟满足"],
        "aliases": ["长期关系", "长期幸福", "长期收益"],
        "concepts": ["复利", "未来收益", "长期关系", "长远决策", "延迟满足"],
    },
    "行动系统": {
        "triggers": ["行动系统", "执行系统", "执行力", "行动力", "自我控制"],
        "aliases": ["执行系统", "自我控制系统", "行动机制", "执行机制"],
        "concepts": ["执行", "行动", "自控", "习惯", "注意力", "执行力", "自我控制"],
    },
    "情绪稳定": {
        "triggers": ["情绪稳定", "情绪管理", "情绪调节", "情绪控制", "稳定情绪"],
        "aliases": ["情绪管理", "情绪调节", "自我调节", "稳定情绪"],
        "concepts": ["控制冲动", "平复情绪", "情绪恢复", "自我安抚", "保持冷静"],
    },
    "注意力管理": {
        "triggers": ["注意力管理", "专注力", "注意力", "专注", "分心"],
        "aliases": ["专注力管理", "注意力控制"],
        "concepts": ["专注", "分心", "努力", "控制", "心流", "注意力"],
    },
}
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
REVIEW_BATCH_SIZE = 12
REVIEW_MASTERED_THRESHOLD = 2
REVIEW_INTERVAL_RULES = {
    "low": [1, 2, 3],
    "medium": [2, 4, 7],
    "high": [4, 10, 21],
}


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
            parse_iso_datetime(value).date()
            for value in date_texts
            if parse_iso_datetime(value) is not None
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


def filter_graph_source(
    data: dict[str, Any],
    category: str = "",
    book_id: int | None = None,
    time_scope: str = "all",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    all_books = data["books"]
    books = all_books

    # 先在“书”的维度完成筛选，再回收对应 note。这样图谱视角更统一，
    # 不会出现一本书被排除、但它的笔记还残留在图里的问题。
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
                parse_book_date(book.get("last_read_date") or "") or parse_book_date(book.get("reading_date") or "")
                for book in books
            ]
            reference_date = max((date for date in available_dates if date is not None), default=datetime.now())
            threshold = reference_date - timedelta(days=days)
            books = [
                book
                for book in books
                if (
                    (parse_book_date(book.get("last_read_date") or "") or parse_book_date(book.get("reading_date") or ""))
                    and (parse_book_date(book.get("last_read_date") or "") or parse_book_date(book.get("reading_date") or "")) >= threshold
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
    for node_name, node_links in adjacency.items():
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
        if (
            kept_pairs[tuple(sorted((str(link["source"]), str(link["target"]))))] >= (2 if require_mutual else 1)
        )
    ]


def extract_query_keywords(query: str) -> list[str]:
    return [
        token.lower()
        for token in re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z]{3,}", query)
        if token not in STOPWORDS
    ]


def dedupe_text_list(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        value = (item or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def rewrite_query(query: str) -> dict[str, Any]:
    normalized = re.sub(r"\s+", "", query)
    variants: list[dict[str, Any]] = [{"text": query.strip(), "weight": 1.0, "kind": "original"}]
    applied_rules: list[str] = []
    expansion_terms: list[str] = []

    # query rewrite 只在抽象概念词上做轻量扩展，避免每个搜索都被“改写过头”。
    # 这里保留原 query 最高权重，再把同义表达和相关概念以较低权重加入召回候选。
    for anchor, config in QUERY_REWRITE_RULES.items():
        trigger_terms = [anchor, *config.get("triggers", []), *config.get("aliases", [])]
        if not any(term and term in normalized for term in trigger_terms):
            continue

        applied_rules.append(anchor)
        for alias in [anchor, *config.get("aliases", [])]:
            if alias and alias not in normalized:
                variants.append({"text": alias, "weight": 0.9, "kind": "alias"})
        for concept in config.get("concepts", []):
            if concept and concept not in normalized:
                variants.append({"text": concept, "weight": 0.72, "kind": "concept"})
                expansion_terms.append(concept)

    deduped_variants: list[dict[str, Any]] = []
    seen_variant_texts: set[str] = set()
    for item in variants:
        text = (item.get("text") or "").strip()
        if not text or text in seen_variant_texts:
            continue
        seen_variant_texts.add(text)
        deduped_variants.append(
            {
                **item,
                "keywords": extract_query_keywords(text),
                "ngrams": build_query_ngrams(text),
                "vector": vectorize_text(text),
            }
        )

    return {
        "original": query.strip(),
        "applied_rules": dedupe_text_list(applied_rules),
        "expansion_terms": dedupe_text_list(expansion_terms),
        "variants": deduped_variants,
    }


def build_query_rewrite_summary(rewrite_info: dict[str, Any] | None) -> dict[str, Any] | None:
    if not rewrite_info or not rewrite_info.get("applied_rules"):
        return None
    return {
        "original": rewrite_info.get("original", ""),
        "applied_rules": rewrite_info.get("applied_rules", []),
        "expansion_terms": rewrite_info.get("expansion_terms", []),
        "variants": [item.get("text", "") for item in rewrite_info.get("variants", [])[:8]],
    }


def build_query_ngrams(query: str) -> set[str]:
    compact = re.sub(r"\s+", "", query.lower())
    if len(compact) < 2:
        return {compact} if compact else set()
    return {compact[index : index + 2] for index in range(len(compact) - 1)}


def build_semantic_text(note: dict[str, Any]) -> str:
    return " ".join(
        [
            note.get("book_title") or "",
            note.get("chapter") or "",
            note.get("excerpt") or "",
            note.get("comment") or "",
            " ".join(note.get("tags", [])),
        ]
    )


def vectorize_text(text: str) -> list[float]:
    return embedding_service.embed_text(text)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(left[index] * right[index] for index in range(len(left)))


def compute_note_match(
    note: dict[str, Any],
    lowered_query: str,
    keywords: list[str],
    query_ngrams: set[str],
) -> tuple[int, int, float]:
    excerpt = (note.get("excerpt") or "").lower()
    comment = (note.get("comment") or "").lower()
    chapter = (note.get("chapter") or "").lower()
    book_title = (note.get("book_title") or "").lower()
    tags = [tag.lower() for tag in note.get("tags", [])]
    haystack = " ".join([book_title, chapter, excerpt, comment, " ".join(tags)])

    exact_score = 0
    for keyword in keywords:
        exact_score += haystack.count(keyword) * 14
        if keyword in book_title:
            exact_score += 8
        if keyword in chapter:
            exact_score += 6
        if any(keyword in tag for tag in tags):
            exact_score += 5

    if lowered_query and lowered_query in haystack:
        exact_score += 10

    note_ngrams = build_query_ngrams("".join([book_title, chapter, excerpt[:240], comment[:120]]))
    fuzzy_score = len(query_ngrams & note_ngrams)

    total_score = exact_score + fuzzy_score + min(len(excerpt) / 80, 4)
    return exact_score, fuzzy_score, total_score


def compute_note_relevance(
    note: dict[str, Any],
    lowered_query: str,
    keywords: list[str],
    query_ngrams: set[str],
) -> float:
    return compute_note_match(note, lowered_query, keywords, query_ngrams)[2]


def compute_semantic_similarity(note: dict[str, Any], query_vector: list[float]) -> float:
    note_vector = note.get("semantic_vector") or []
    return cosine_similarity(query_vector, note_vector)


def rank_notes_for_query(
    notes: list[dict[str, Any]],
    query: str,
    rewrite_info: dict[str, Any] | None = None,
) -> list[tuple[dict[str, Any], float]]:
    rewrite = rewrite_info or rewrite_query(query)

    scored_notes: list[tuple[dict[str, Any], float]] = []
    for note in notes:
        best_score = 0.0
        support_hits = 0

        for variant in rewrite["variants"]:
            text = variant["text"]
            lowered = text.lower()
            keywords = variant["keywords"]
            query_ngrams = variant["ngrams"]
            query_vector = variant["vector"]
            weight = float(variant["weight"])
            kind = str(variant["kind"])
            fuzzy_threshold = max(2, min(4, (len(query_ngrams) // 2) + 1)) if query_ngrams else 0

            exact_score, fuzzy_score, lexical_score = compute_note_match(note, lowered, keywords, query_ngrams)
            semantic_score = compute_semantic_similarity(note, query_vector)
            semantic_threshold = 0.64 if kind == "original" else 0.68
            hybrid_threshold = 0.46 if kind != "concept" else 0.5
            weighted_score = (lexical_score * weight) + (semantic_score * 28 * weight)

            if (
                exact_score > 0
                or fuzzy_score >= fuzzy_threshold
                or (semantic_score >= hybrid_threshold and fuzzy_score >= 1)
                or semantic_score >= semantic_threshold
            ):
                support_hits += 1
                best_score = max(best_score, weighted_score)

        if support_hits:
            scored_notes.append((note, best_score + min(support_hits - 1, 2) * 1.2))

    scored_notes.sort(key=lambda item: (item[1], len(item[0].get("excerpt") or "")), reverse=True)
    if not scored_notes:
        return []

    top_score = scored_notes[0][1]
    floor_score = max(top_score * 0.68, 10.5)

    # 二次裁剪只保留“接近最佳结果”的候选，避免 query 很短时把弱相关结果一股脑带进问答和搜索。
    trimmed_notes = [item for item in scored_notes if item[1] >= floor_score]
    return trimmed_notes[:80]


@dataclass
class VaultRepository:
    root: Path = VAULT_ROOT
    db_path: Path = DB_PATH
    demo_data_only: bool = False
    _signature: tuple[int, int] | None = None
    _data: dict[str, Any] | None = None

    def load(self, force_refresh: bool = False) -> dict[str, Any]:
        signature = self._compute_signature()

        if not force_refresh and self._data is not None and signature == self._signature:
            return self._data

        self._ensure_db()

        cached_signature = self._read_cached_signature()
        if not force_refresh and self.demo_data_only and self._has_cached_books():
            # 演示环境不依赖服务器上的原始 Markdown，只从已同步的 SQLite 缓存启动。
            data = self._load_from_db()
            self._signature = signature
            self._data = data
            return data

        if not force_refresh and cached_signature == signature and self._has_cached_books():
            data = self._load_from_db()
            self._signature = signature
            self._data = data
            return data

        books, notes = self._scan_vault()
        self._write_cache(signature, books, notes)
        data = self._assemble_data(books, notes)
        self._signature = signature
        self._data = data
        return data

    def get_book(self, book_id: int) -> dict[str, Any] | None:
        data = self.load()
        return next((item for item in data["books"] if item["id"] == book_id), None)

    def get_book_notes(self, book_id: int) -> list[dict[str, Any]]:
        data = self.load()
        return [item for item in data["notes"] if item["book_id"] == book_id]

    def get_cached_summary(self, book_id: int) -> str | None:
        self._ensure_db()
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT summary FROM book_summaries WHERE book_id = ?",
                (book_id,),
            ).fetchone()
        return row[0] if row else None

    def save_book_summary(self, book_id: int, summary: str) -> None:
        self._ensure_db()
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO book_summaries (book_id, summary)
                VALUES (?, ?)
                ON CONFLICT(book_id) DO UPDATE SET summary = excluded.summary
                """,
                (book_id, summary),
            )
            connection.commit()

    def get_review_progress_map(self, note_ids: list[int] | None = None) -> dict[int, dict[str, Any]]:
        self._ensure_db()
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            if note_ids:
                placeholders = ",".join("?" for _ in note_ids)
                rows = connection.execute(
                    f"""
                    SELECT note_id, review_count, mastery_score, last_result,
                           last_reviewed_at, next_review_at
                    FROM review_progress
                    WHERE note_id IN ({placeholders})
                    """,
                    tuple(note_ids),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT note_id, review_count, mastery_score, last_result,
                           last_reviewed_at, next_review_at
                    FROM review_progress
                    """
                ).fetchall()
        return {
            int(row["note_id"]): {
                "note_id": int(row["note_id"]),
                "review_count": int(row["review_count"] or 0),
                "mastery_score": int(row["mastery_score"] or 0),
                "last_result": row["last_result"] or "",
                "last_reviewed_at": row["last_reviewed_at"] or "",
                "next_review_at": row["next_review_at"] or "",
            }
            for row in rows
        }

    def get_review_log_dates(self) -> list[str]:
        self._ensure_db()
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(
                "SELECT reviewed_at FROM review_logs ORDER BY reviewed_at DESC"
            ).fetchall()
        return [row[0] for row in rows if row and row[0]]

    def record_review_result(self, note_id: int, level: str) -> dict[str, Any] | None:
        self._ensure_db()
        now = datetime.now()

        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            current = connection.execute(
                """
                SELECT note_id, review_count, mastery_score
                FROM review_progress
                WHERE note_id = ?
                """,
                (note_id,),
            ).fetchone()
            if current is None:
                review_count = 0
                mastery_score = 0
            else:
                review_count = int(current["review_count"] or 0)
                mastery_score = int(current["mastery_score"] or 0)

            # 这里使用一套足够稳定、也足够容易解释的轻量复习调度策略：
            # 不会/模糊/掌握 对应不同间隔，并且会随着复习次数逐步拉长周期。
            if level == "low":
                mastery_score = max(0, mastery_score - 1)
            elif level == "medium":
                mastery_score = min(3, max(mastery_score, 1))
            else:
                mastery_score = min(3, mastery_score + 1)

            next_review_at = now + timedelta(days=get_review_interval_days(level, review_count, mastery_score))
            updated_review_count = review_count + 1

            connection.execute(
                """
                INSERT INTO review_progress (
                    note_id, review_count, mastery_score, last_result,
                    last_reviewed_at, next_review_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(note_id) DO UPDATE SET
                    review_count = excluded.review_count,
                    mastery_score = excluded.mastery_score,
                    last_result = excluded.last_result,
                    last_reviewed_at = excluded.last_reviewed_at,
                    next_review_at = excluded.next_review_at
                """,
                (
                    note_id,
                    updated_review_count,
                    mastery_score,
                    level,
                    serialize_datetime(now),
                    serialize_datetime(next_review_at),
                ),
            )
            connection.execute(
                """
                INSERT INTO review_logs (note_id, level, reviewed_at, next_review_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    note_id,
                    level,
                    serialize_datetime(now),
                    serialize_datetime(next_review_at),
                ),
            )
            connection.commit()

        return {
            "note_id": note_id,
            "review_count": updated_review_count,
            "mastery_score": mastery_score,
            "last_result": level,
            "last_reviewed_at": serialize_datetime(now),
            "next_review_at": serialize_datetime(next_review_at),
        }

    def _scan_vault(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        books: list[dict[str, Any]] = []
        notes: list[dict[str, Any]] = []
        markdown_files = sorted(self.root.rglob("*.md"))

        for index, file_path in enumerate(markdown_files, start=1):
            parsed = parse_markdown_book(file_path, book_id=index)
            books.append(parsed["book"])
            notes.extend(parsed["notes"])

        self._attach_embeddings(notes)
        return books, notes

    def _attach_embeddings(self, notes: list[dict[str, Any]]) -> None:
        if not notes:
            return

        texts = [build_semantic_text(note) for note in notes]
        vectors = embedding_service.embed_texts(texts)
        for note, vector in zip(notes, vectors, strict=False):
            note["semantic_vector"] = vector

    def _assemble_data(self, books: list[dict[str, Any]], notes: list[dict[str, Any]]) -> dict[str, Any]:
        category_counter = Counter(book["category"] for book in books if book["category"])
        chapter_counter = Counter(note["chapter"] for note in notes if note["chapter"])
        return {
            "books": books,
            "notes": notes,
            "stats": {
                "book_count": len(books),
                "note_count": len(notes),
                "category_count": len(category_counter),
                "top_topics": [name for name, _ in chapter_counter.most_common(5)],
            },
        }

    def _compute_signature(self) -> tuple[int, int]:
        if not self.root.exists():
            return (0, 0)
        files = list(self.root.rglob("*.md"))
        latest_mtime = max((int(path.stat().st_mtime) for path in files), default=0)
        return (len(files), latest_mtime)

    def _ensure_db(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    author TEXT,
                    notes INTEGER NOT NULL,
                    tags_json TEXT NOT NULL,
                    category TEXT,
                    source_path TEXT,
                    reading_date TEXT,
                    last_read_date TEXT,
                    progress TEXT,
                    cover TEXT,
                    reading_notes TEXT
                );

                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY,
                    book_id INTEGER NOT NULL,
                    book_title TEXT NOT NULL,
                    category TEXT,
                    chapter TEXT,
                    excerpt TEXT NOT NULL,
                    comment TEXT,
                    tags_json TEXT NOT NULL,
                    embedding_json TEXT NOT NULL DEFAULT '[]',
                    timestamp TEXT,
                    source_path TEXT,
                    FOREIGN KEY(book_id) REFERENCES books(id)
                );

                CREATE TABLE IF NOT EXISTS book_summaries (
                    book_id INTEGER PRIMARY KEY,
                    summary TEXT NOT NULL,
                    FOREIGN KEY(book_id) REFERENCES books(id)
                );

                CREATE TABLE IF NOT EXISTS review_progress (
                    note_id INTEGER PRIMARY KEY,
                    review_count INTEGER NOT NULL DEFAULT 0,
                    mastery_score INTEGER NOT NULL DEFAULT 0,
                    last_result TEXT NOT NULL DEFAULT '',
                    last_reviewed_at TEXT NOT NULL DEFAULT '',
                    next_review_at TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY(note_id) REFERENCES notes(id)
                );

                CREATE TABLE IF NOT EXISTS review_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER NOT NULL,
                    level TEXT NOT NULL,
                    reviewed_at TEXT NOT NULL,
                    next_review_at TEXT NOT NULL,
                    FOREIGN KEY(note_id) REFERENCES notes(id)
                );
                """
            )
            # 老缓存库可能没有 embedding_json 列，这里做一次轻量迁移，避免重建数据库。
            note_columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(notes)").fetchall()
            }
            if "embedding_json" not in note_columns:
                connection.execute(
                    "ALTER TABLE notes ADD COLUMN embedding_json TEXT NOT NULL DEFAULT '[]'"
                )
            connection.commit()

    def _read_cached_signature(self) -> tuple[int, int] | None:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT value FROM metadata WHERE key = 'vault_signature'"
            ).fetchone()
        if not row:
            return None
        try:
            values = json.loads(row[0])
            return int(values[0]), int(values[1])
        except (ValueError, TypeError, json.JSONDecodeError):
            return None

    def _has_cached_books(self) -> bool:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute("SELECT COUNT(*) FROM books").fetchone()
        return bool(row and row[0] > 0)

    def _write_cache(
        self,
        signature: tuple[int, int],
        books: list[dict[str, Any]],
        notes: list[dict[str, Any]],
    ) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("DELETE FROM books")
            connection.execute("DELETE FROM notes")

            connection.executemany(
                """
                INSERT INTO books (
                    id, title, author, notes, tags_json, category, source_path,
                    reading_date, last_read_date, progress, cover, reading_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        book["id"],
                        book["title"],
                        book["author"],
                        book["notes"],
                        json.dumps(book["tags"], ensure_ascii=False),
                        book["category"],
                        book["source_path"],
                        book["reading_date"],
                        book["last_read_date"],
                        book["progress"],
                        book["cover"],
                        book["reading_notes"],
                    )
                    for book in books
                ],
            )

            connection.executemany(
                """
                INSERT INTO notes (
                    id, book_id, book_title, category, chapter, excerpt,
                    comment, tags_json, embedding_json, timestamp, source_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        note["id"],
                        note["book_id"],
                        note["book_title"],
                        note["category"],
                        note["chapter"],
                        note["excerpt"],
                        note["comment"],
                        json.dumps(note["tags"], ensure_ascii=False),
                        json.dumps(note["semantic_vector"], ensure_ascii=False),
                        note["timestamp"],
                        note["source_path"],
                    )
                    for note in notes
                ],
            )

            connection.execute(
                """
                INSERT INTO metadata (key, value)
                VALUES ('vault_signature', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (json.dumps(signature),),
            )
            connection.commit()

    def _load_from_db(self) -> dict[str, Any]:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            book_rows = connection.execute(
                """
                SELECT id, title, author, notes, tags_json, category, source_path,
                       reading_date, last_read_date, progress, cover, reading_notes
                FROM books
                ORDER BY id
                """
            ).fetchall()
            note_rows = connection.execute(
                """
                SELECT id, book_id, book_title, category, chapter, excerpt, comment,
                       tags_json, embedding_json, timestamp, source_path
                FROM notes
                ORDER BY id
                """
            ).fetchall()

        books = [
            {
                "id": row["id"],
                "title": row["title"],
                "author": row["author"] or "",
                "notes": row["notes"],
                "tags": json.loads(row["tags_json"]),
                "category": row["category"] or "",
                "source_path": row["source_path"] or "",
                "reading_date": row["reading_date"] or "",
                "last_read_date": row["last_read_date"] or "",
                "progress": row["progress"] or "",
                "cover": row["cover"] or "",
                "reading_notes": row["reading_notes"] or "",
            }
            for row in book_rows
        ]

        notes = []
        for row in note_rows:
            tags = json.loads(row["tags_json"])
            note = {
                "id": row["id"],
                "book_id": row["book_id"],
                "book_title": row["book_title"],
                "category": row["category"] or "",
                "chapter": row["chapter"] or "",
                "excerpt": row["excerpt"],
                "comment": row["comment"] or "",
                "tags": tags,
                "semantic_vector": json.loads(row["embedding_json"] or "[]"),
                "timestamp": row["timestamp"] or "",
                "source_path": row["source_path"] or "",
            }
            if not note["semantic_vector"]:
                note["semantic_vector"] = vectorize_text(build_semantic_text(note))
            notes.append(note)

        return self._assemble_data(books, notes)


def parse_markdown_book(file_path: Path, book_id: int) -> dict[str, Any]:
    raw_text = file_path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(raw_text)
    metadata = parse_frontmatter(frontmatter)
    sections = body.splitlines()

    title = str(metadata.get("title") or file_path.stem)
    author = str(metadata.get("author") or "")
    category = file_path.parent.name if file_path.parent != file_path else ""
    chapter = ""
    in_highlights = False
    note_id = 1
    notes: list[dict[str, Any]] = []
    reading_notes = extract_reading_notes(body)

    current_highlight_lines: list[str] = []
    current_timestamp = ""

    def flush_highlight() -> None:
        nonlocal note_id, current_highlight_lines, current_timestamp

        if not current_highlight_lines:
            return

        content = " ".join(part.strip() for part in current_highlight_lines if part.strip())
        cleaned = content.replace("📌", "").strip()
        if cleaned:
            notes.append(
                {
                    "id": book_id * 100000 + note_id,
                    "book_id": book_id,
                    "book_title": title,
                    "category": category,
                    "chapter": normalize_heading(chapter),
                    "excerpt": cleaned,
                    "comment": "",
                    "tags": build_tags(category, chapter, cleaned),
                    "semantic_vector": [],
                    "timestamp": current_timestamp,
                    "source_path": str(file_path),
                }
            )
            note_id += 1

        current_highlight_lines = []
        current_timestamp = ""

    for line in sections:
        stripped = line.strip()

        if stripped == SECTION_HIGHLIGHTS:
            in_highlights = True
            continue

        if stripped in {SECTION_READING_NOTES, SECTION_BOOK_REVIEW}:
            flush_highlight()
            in_highlights = False
            continue

        if not in_highlights:
            continue

        if stripped.startswith("## ") or stripped.startswith("### "):
            flush_highlight()
            chapter = stripped.lstrip("# ").strip()
            continue

        if stripped.startswith("> 📌"):
            flush_highlight()
            current_highlight_lines = [stripped.replace("> ", "", 1)]
            continue

        if current_highlight_lines and stripped.startswith("> ⏱"):
            current_timestamp = stripped.replace("> ⏱", "", 1).strip()
            flush_highlight()
            continue

        if current_highlight_lines:
            continuation = stripped
            if continuation.startswith("> "):
                continuation = continuation.replace("> ", "", 1)
            current_highlight_lines.append(continuation)

    flush_highlight()

    book = {
        "id": book_id,
        "title": title,
        "author": author,
        "notes": len(notes),
        "tags": derive_book_tags(category, notes),
        "category": category,
        "source_path": str(file_path),
        "reading_date": metadata.get("readingDate", ""),
        "last_read_date": metadata.get("lastReadDate", ""),
        "progress": metadata.get("progress", ""),
        "cover": metadata.get("cover", ""),
        "reading_notes": reading_notes,
    }

    return {"book": book, "notes": notes}


def split_frontmatter(raw_text: str) -> tuple[str, str]:
    if not raw_text.startswith("---\n"):
        return "", raw_text

    parts = raw_text.split("\n---\n", 1)
    if len(parts) != 2:
        return "", raw_text

    return parts[0].replace("---\n", "", 1), parts[1]


def parse_frontmatter(frontmatter: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def extract_reading_notes(body: str) -> str:
    if SECTION_READING_NOTES not in body:
        return ""

    after = body.split(SECTION_READING_NOTES, 1)[1]
    before_review = after.split(SECTION_BOOK_REVIEW, 1)[0]
    lines = [line.strip() for line in before_review.splitlines() if line.strip()]
    return "\n".join(lines[:8]).strip()


def normalize_heading(heading: str) -> str:
    heading = re.sub(r"^\d+(\.\d+)?\s*", "", heading)
    heading = re.sub(r"^第[一二三四五六七八九十百千0-9]+[章节部分卷篇]\s*", "", heading)
    return heading.strip()


def build_tags(category: str, chapter: str, content: str) -> list[str]:
    tags = [category] if category else []
    chapter_name = normalize_heading(chapter)
    if chapter_name:
        tags.append(chapter_name[:12])

    for keyword in ("长期主义", "系统", "决策", "情绪", "幸福", "习惯", "注意力", "财富", "学习", "行动"):
        if keyword in content and keyword not in tags:
            tags.append(keyword)

    return tags[:4]


def derive_book_tags(category: str, notes: list[dict[str, Any]]) -> list[str]:
    counter = Counter()
    for note in notes:
        for tag in note["tags"]:
            counter[tag] += 1

    ordered = [tag for tag, _ in counter.most_common(4)]
    if category and category not in ordered:
        ordered.insert(0, category)
    return ordered[:4]


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

    # 先按标签收集“主题”统计信息。这个版本以真实笔记中的标签和章节名为基础，
    # 结果可解释性强，也方便后续替换成 embedding 或 LLM 聚类。
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

        # 共现边反映两个主题在同一条笔记中同时出现，可作为图谱关系的第一层依据。
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
    adjacency: dict[str, set[str]] = {topic["topic"]: set() for topic in ranked_topics}
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
        adjacency[source].add(target)
        adjacency[target].add(source)

    # 这里不用整张图的一次性连通分量，而是采用“高频主题作为中心，再吸附最相关邻居”的方式。
    # 对个人知识库场景来说，这样得到的主题簇更小、更可读，也更适合前端卡片化展示。
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
        for book_id in top_book_ids:
            book = book_lookup.get(book_id)
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
            }
        )

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
        "filters": {
            "selected": {
                "category": category,
                "book_id": book_id,
                "time_scope": time_scope,
                "mode": "topic",
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
            "time_scopes": [
                {"label": "全部时间", "value": "all"},
                {"label": "最近 90 天", "value": "recent-90"},
                {"label": "最近 180 天", "value": "recent-180"},
                {"label": "最近 1 年", "value": "recent-365"},
            ],
            "modes": [
                {"label": "领域聚类", "value": "category"},
                {"label": "知识主题", "value": "topic"},
            ],
        },
        "clusters": clusters,
        "graph": {
            "nodes": nodes,
            "links": graph_links,
        },
    }


def build_category_graph_payload(
    data: dict[str, Any],
    category: str = "",
    book_id: int | None = None,
    time_scope: str = "all",
) -> dict[str, Any]:
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

    ranked_categories = sorted(
        category_groups.items(),
        key=lambda item: (len(item[1]["book_ids"]), item[1]["note_count"]),
        reverse=True,
    )

    clusters: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []
    category_tag_sets: dict[str, set[str]] = {}

    # 领域聚类的核心是“先按阅读领域分组，再看每个领域内部最常出现的话题”。
    # 这样更符合用户第一眼的认知，也更容易映射到历史/经济/心理/文学这种心智模型。
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
            top_tags = [
                tag
                for tag, _ in group["topical_tags"].most_common(6)
            ]
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

    links = prune_graph_links(
        links,
        top_k_per_node=2 if book_id is None else 1,
        min_value=2,
        require_mutual=True,
    )

    return {
        "overview": {
            "topic_count": len(nodes),
            "cluster_count": len(clusters),
            "edge_count": len(links),
            "book_count": len(books),
        },
        "filters": {
            "selected": {
                "category": category,
                "book_id": book_id,
                "time_scope": time_scope,
                "mode": "category",
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
            "time_scopes": [
                {"label": "全部时间", "value": "all"},
                {"label": "最近 90 天", "value": "recent-90"},
                {"label": "最近 180 天", "value": "recent-180"},
                {"label": "最近 1 年", "value": "recent-365"},
            ],
            "modes": [
                {"label": "领域聚类", "value": "category"},
                {"label": "知识主题", "value": "topic"},
            ],
        },
        "clusters": clusters,
        "graph": {
            "nodes": nodes,
            "links": links,
        },
    }


def build_dashboard_payload(data: dict[str, Any]) -> dict[str, Any]:
    books = data["books"]
    notes = data["notes"]
    stats = data["stats"]

    review_state = build_review_overview(data)

    recent_books = sorted(
        books,
        key=lambda item: item.get("last_read_date") or item.get("reading_date") or "",
        reverse=True,
    )[:5]

    return {
        "metrics": [
            {"label": "书籍数", "value": stats["book_count"], "hint": "已接入真实 Obsidian 书单"},
            {"label": "笔记数", "value": stats["note_count"], "hint": "来自微信读书高亮划线"},
            {"label": "分类数", "value": stats["category_count"], "hint": "按目录自动归类"},
            {
                "label": "待复习",
                "value": review_state["due_count"],
                "hint": "基于真实复习进度和到期时间计算",
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
    }


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


def build_review_overview(data: dict[str, Any]) -> dict[str, Any]:
    notes = data["notes"]
    now = datetime.now()
    progress_map = vault_repository.get_review_progress_map([note["id"] for note in notes]) if notes else {}
    review_logs = vault_repository.get_review_log_dates()

    due_count = 0
    mastered_count = 0
    for note in notes:
        progress = progress_map.get(note["id"])
        if not progress:
            due_count += 1
            continue
        if progress.get("mastery_score", 0) >= REVIEW_MASTERED_THRESHOLD:
            mastered_count += 1
        next_review_at = parse_iso_datetime(progress.get("next_review_at", ""))
        if next_review_at is None or next_review_at <= now:
            due_count += 1

    reviewed_total = len(progress_map)
    mastery_rate = f"{round((mastered_count / reviewed_total) * 100)}%" if reviewed_total else "0%"

    return {
        "due_count": due_count,
        "streak_days": calculate_review_streak(review_logs),
        "mastery_rate": mastery_rate,
    }


def build_review_payload(data: dict[str, Any]) -> dict[str, Any]:
    notes = data["notes"]
    progress_map = vault_repository.get_review_progress_map([note["id"] for note in notes]) if notes else {}
    overview = build_review_overview(data)
    now = datetime.now()

    scored_notes: list[tuple[tuple[int, float, int], dict[str, Any], dict[str, Any] | None]] = []
    for note in notes:
        progress = progress_map.get(note["id"])
        next_review_at = parse_iso_datetime(progress.get("next_review_at", "")) if progress else None
        is_due = progress is None or next_review_at is None or next_review_at <= now
        if not is_due:
            continue

        # 先把“已经到期”的笔记排在前面；对于从未复习过的笔记，则优先选择信息密度更高的摘录。
        overdue_rank = 0 if progress and next_review_at else 1
        due_timestamp = next_review_at.timestamp() if next_review_at else float("inf")
        richness = len(note.get("excerpt") or "") + len(note.get("comment") or "")
        scored_notes.append(((overdue_rank, due_timestamp, -richness), note, progress))

    scored_notes.sort(key=lambda item: item[0])
    review_notes = scored_notes[:REVIEW_BATCH_SIZE]

    if not review_notes:
        return {
            "summary": [
                {"label": "待复习", "value": "0"},
                {"label": "连续复习", "value": f"{overview['streak_days']} 天"},
                {"label": "掌握率", "value": overview["mastery_rate"]},
            ],
            "card": {
                "id": 0,
                "book_id": 0,
                "note_id": 0,
                "question": "",
                "source": "",
                "answer": "",
                "review_count": 0,
                "mastery_score": 0,
                "last_reviewed_at": "",
                "next_review_at": "",
            },
            "cards": [],
        }

    cards = [
        {
            "id": index + 1,
            "book_id": note["book_id"],
            "note_id": note["id"],
            "question": "这条摘录最值得复述的核心观点是什么？",
            "source": f"{note['book_title']} · {note['chapter'] or '未分章节'}",
            "answer": note["excerpt"],
            "review_count": int((progress or {}).get("review_count") or 0),
            "mastery_score": int((progress or {}).get("mastery_score") or 0),
            "last_reviewed_at": (progress or {}).get("last_reviewed_at", ""),
            "next_review_at": (progress or {}).get("next_review_at", ""),
        }
        for index, (_, note, progress) in enumerate(review_notes)
    ]

    return {
        "summary": [
            {"label": "待复习", "value": str(overview["due_count"])},
            {"label": "连续复习", "value": f"{overview['streak_days']} 天"},
            {"label": "掌握率", "value": overview["mastery_rate"]},
        ],
        "card": cards[0],
        "cards": cards,
    }


def answer_question(
    data: dict[str, Any],
    question: str,
    scope: str = "all-books",
    book_id: int | None = None,
) -> dict[str, Any]:
    books = data["books"]
    notes = data["notes"]
    rewrite_info = rewrite_query(question)
    scoped_book = next((book for book in books if book["id"] == book_id), None) if book_id else None
    target_book = scoped_book or next((book for book in books if book["title"] in question), None)

    if scope == "current-book" and scoped_book:
        candidate_notes = [note for note in notes if note["book_id"] == scoped_book["id"]]
    elif target_book:
        candidate_notes = [note for note in notes if note["book_id"] == target_book["id"]]
    else:
        candidate_notes = notes

    ranked_pairs = rank_notes_for_query(candidate_notes, question, rewrite_info=rewrite_info)
    ranked = [note for note, _ in ranked_pairs]
    top_notes = ranked[:5]

    if not top_notes:
        top_notes = ranked[:5]

    scope_label = f"《{target_book['title']}》" if target_book else "你的阅读笔记库"

    if not top_notes:
        answer = f"目前还没能从{scope_label}里找到可回答这个问题的有效摘录。"
    else:
        bullet_points = "；".join(note["excerpt"][:42] for note in top_notes[:3])
        answer = f"基于{scope_label}中的相关摘录，我找到的重点是：{bullet_points}。"

    references = [
        {
            "book": note["book_title"],
            "book_id": note["book_id"],
            "note_id": note["id"],
            "chapter": note["chapter"] or "未分章节",
            "excerpt": note["excerpt"],
            "source_path": note["source_path"],
        }
        for note in top_notes[:3]
    ]

    return {
        "question": question,
        "answer": answer,
        "references": references,
        "query_rewrite": build_query_rewrite_summary(rewrite_info),
    }


def build_book_context(data: dict[str, Any], book_id: int) -> dict[str, Any] | None:
    book = next((item for item in data["books"] if item["id"] == book_id), None)
    if book is None:
        return None

    notes = [note for note in data["notes"] if note["book_id"] == book_id][:40]
    return {"book": book, "notes": notes}


def format_book_context(context: dict[str, Any]) -> str:
    book = context["book"]
    notes = context["notes"]

    parts = [
        f"书名：{book['title']}",
        f"作者：{book['author']}",
        f"分类：{book['category']}",
        f"高亮数量：{book['notes']}",
    ]
    if book.get("reading_notes"):
        parts.append(f"读书笔记：{book['reading_notes']}")

    for idx, note in enumerate(notes, start=1):
        parts.append(
            f"[摘录{idx}] 章节：{note['chapter'] or '未分章节'}\n内容：{note['excerpt']}"
        )

    return "\n".join(parts)


def format_qa_context(question: str, references: list[dict[str, Any]]) -> str:
    lines = [f"用户问题：{question}", "候选引用："]
    for idx, ref in enumerate(references, start=1):
        lines.append(f"[{idx}] 书名：{ref['book']}\n章节：{ref['chapter']}\n内容：{ref['excerpt']}")
    return "\n".join(lines)


vault_repository = VaultRepository()
