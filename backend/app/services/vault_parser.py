"""Vault repository and compatibility helpers.

This module is the backend entry point for reading the user's Obsidian vault.
It owns the local SQLite cache, file signature checks, review-progress writes,
and a few compatibility helpers still imported by routes/services.

What intentionally lives elsewhere:
- Markdown parsing: `services/vault/parser.py`
- Search/ranking: `services/search/ranker.py`
- Review scheduling/payloads: `services/review/*`
- Notes/dashboard payloads: `services/payloads/*`

The long-term direction is to split `VaultRepository` itself into scanner,
cache repository, and review repository modules. For now this file remains the
stateful boundary around local files and SQLite.
"""

from __future__ import annotations

import json
import os
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .review.scheduler import (
    calculate_next_review_at,
    serialize_datetime,
    update_mastery_score,
)
from .search.ranker import (
    build_query_rewrite_summary,
    build_semantic_text,
    embedding_service,
    rank_notes_for_query,
    rewrite_query,
    vectorize_text,
)
from .vault.parser import parse_markdown_book

VAULT_ROOT = Path(os.getenv("VAULT_ROOT", str(Path.home() / "Documents/Obsidian Vault/书籍阅读"))).expanduser()
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DATA_DIR / "readmind_cache.db"


@dataclass
class VaultRepository:
    root: Path = VAULT_ROOT
    db_path: Path = DB_PATH
    demo_data_only: bool = False
    _signature: tuple[int, int] | None = None
    _data: dict[str, Any] | None = None

    def load(self, force_refresh: bool = False) -> dict[str, Any]:
        """Load books/notes from memory, SQLite cache, or the Markdown vault.

        The cache key is a simple file-count + modified-time signature. This is
        cheap enough for a local-first app and avoids re-parsing the vault on
        every request. `force_refresh=True` bypasses both memory and SQLite
        signature checks and re-scans Markdown files.
        """
        signature = self._compute_signature()

        if not force_refresh and self._data is not None and signature == self._signature:
            return self._data

        self._ensure_db()

        cached_signature = self._read_cached_signature()
        if self.demo_data_only and self._has_cached_books():
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
            mastery_score = update_mastery_score(level, mastery_score)
            next_review_at = calculate_next_review_at(level, review_count, mastery_score, now)
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
                    reading_time TEXT,
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
            book_columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(books)").fetchall()
            }
            if "reading_time" not in book_columns:
                connection.execute("ALTER TABLE books ADD COLUMN reading_time TEXT DEFAULT ''")
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
                    reading_date, last_read_date, reading_time, progress, cover, reading_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        book.get("reading_time", ""),
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
                       reading_date, last_read_date, reading_time, progress, cover, reading_notes
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
                "reading_time": row["reading_time"] or "",
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
