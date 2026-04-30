from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from .job_repository import utc_now
from .vault_parser import DATA_DIR, DB_PATH


class QaDepositRepository:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self._ensure_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_db(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS qa_deposits (
                    id TEXT PRIMARY KEY,
                    deposit_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    question TEXT NOT NULL,
                    content TEXT NOT NULL,
                    references_json TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    book_id INTEGER,
                    note_ids_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_qa_deposits_type_updated ON qa_deposits (deposit_type, updated_at)"
            )
            connection.commit()

    def create_deposit(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = utc_now()
        references = payload.get("references") if isinstance(payload.get("references"), list) else []
        note_ids = payload.get("note_ids") if isinstance(payload.get("note_ids"), list) else []
        if not note_ids:
            note_ids = sorted({reference.get("note_id") for reference in references if reference.get("note_id")})
        deposit_id = f"deposit_{uuid.uuid4().hex[:16]}"
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO qa_deposits (
                    id, deposit_type, title, question, content, references_json,
                    scope, book_id, note_ids_json, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    deposit_id,
                    normalize_deposit_type(payload.get("deposit_type")),
                    str(payload.get("title") or "未命名沉淀"),
                    str(payload.get("question") or ""),
                    str(payload.get("content") or ""),
                    json.dumps(references, ensure_ascii=False),
                    str(payload.get("scope") or "all-books"),
                    payload.get("book_id"),
                    json.dumps(note_ids, ensure_ascii=False),
                    str(payload.get("status") or "active"),
                    now,
                    now,
                ),
            )
            connection.commit()
        return self.get_deposit(deposit_id) or {}

    def list_deposits(self, deposit_type: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        query = "SELECT * FROM qa_deposits"
        values: list[Any] = []
        if deposit_type:
            query += " WHERE deposit_type = ?"
            values.append(normalize_deposit_type(deposit_type))
        query += " ORDER BY updated_at DESC LIMIT ?"
        values.append(max(1, min(limit, 100)))
        with self._connect() as connection:
            rows = connection.execute(query, tuple(values)).fetchall()
        return [self._serialize_row(row) for row in rows]

    def get_deposit(self, deposit_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM qa_deposits WHERE id = ?", (deposit_id,)).fetchone()
        return self._serialize_row(row) if row else None

    def _serialize_row(self, row: sqlite3.Row) -> dict[str, Any]:
        try:
            references = json.loads(row["references_json"] or "[]")
        except json.JSONDecodeError:
            references = []
        try:
            note_ids = json.loads(row["note_ids_json"] or "[]")
        except json.JSONDecodeError:
            note_ids = []
        return {
            "id": row["id"],
            "deposit_type": row["deposit_type"],
            "title": row["title"],
            "question": row["question"],
            "content": row["content"],
            "references": references,
            "scope": row["scope"],
            "book_id": row["book_id"],
            "note_ids": note_ids,
            "status": row["status"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }


def normalize_deposit_type(value: Any) -> str:
    deposit_type = str(value or "insight_card")
    return deposit_type if deposit_type in {"insight_card", "understanding", "review_seed", "question"} else "insight_card"


qa_deposit_repository = QaDepositRepository()
