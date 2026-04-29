from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from .vault_parser import DATA_DIR, DB_PATH


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


class JobRepository:
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
                CREATE TABLE IF NOT EXISTS async_jobs (
                    id TEXT PRIMARY KEY,
                    job_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    result_json TEXT,
                    error_message TEXT,
                    progress INTEGER NOT NULL DEFAULT 0,
                    message TEXT,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS note_insights (
                    scope_key TEXT PRIMARY KEY,
                    summary TEXT NOT NULL,
                    references_json TEXT NOT NULL,
                    sections_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS graph_analyses (
                    scope_key TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def create_job(
        self,
        *,
        job_type: str,
        resource_type: str,
        resource_id: str,
        payload: dict[str, Any] | None = None,
        message: str = "任务已创建",
    ) -> dict[str, Any]:
        job_id = f"job_{uuid.uuid4().hex[:16]}"
        now = utc_now()
        payload_json = json.dumps(payload or {}, ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO async_jobs (
                    id, job_type, status, resource_type, resource_id,
                    payload_json, progress, message, created_at
                )
                VALUES (?, ?, 'queued', ?, ?, ?, 0, ?, ?)
                """,
                (job_id, job_type, resource_type, resource_id, payload_json, message, now),
            )
            connection.commit()
        return self.get_job(job_id) or {}

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM async_jobs WHERE id = ?",
                (job_id,),
            ).fetchone()
        return self._serialize_row(row)

    def find_active_job(self, *, job_type: str, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM async_jobs
                WHERE job_type = ?
                  AND resource_type = ?
                  AND resource_id = ?
                  AND status IN ('queued', 'processing')
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (job_type, resource_type, resource_id),
            ).fetchone()
        return self._serialize_row(row)

    def list_jobs(self, *, job_types: list[str] | None = None, limit: int = 50) -> list[dict[str, Any]]:
        query = "SELECT * FROM async_jobs"
        values: list[Any] = []
        if job_types:
            placeholders = ", ".join("?" for _ in job_types)
            query += f" WHERE job_type IN ({placeholders})"
            values.extend(job_types)
        query += " ORDER BY created_at DESC LIMIT ?"
        values.append(limit)
        with self._connect() as connection:
            rows = connection.execute(query, tuple(values)).fetchall()
        return [item for row in rows if (item := self._serialize_row(row)) is not None]

    def update_job(
        self,
        job_id: str,
        *,
        status: str | None = None,
        progress: int | None = None,
        message: str | None = None,
        result: dict[str, Any] | None = None,
        error_message: str | None = None,
        started_at: str | None = None,
        finished_at: str | None = None,
    ) -> dict[str, Any] | None:
        updates: list[str] = []
        values: list[Any] = []

        if status is not None:
            updates.append("status = ?")
            values.append(status)
        if progress is not None:
            updates.append("progress = ?")
            values.append(progress)
        if message is not None:
            updates.append("message = ?")
            values.append(message)
        if result is not None:
            updates.append("result_json = ?")
            values.append(json.dumps(result, ensure_ascii=False))
        if error_message is not None:
            updates.append("error_message = ?")
            values.append(error_message)
        if started_at is not None:
            updates.append("started_at = ?")
            values.append(started_at)
        if finished_at is not None:
            updates.append("finished_at = ?")
            values.append(finished_at)

        if not updates:
            return self.get_job(job_id)

        values.append(job_id)
        with self._connect() as connection:
            connection.execute(
                f"UPDATE async_jobs SET {', '.join(updates)} WHERE id = ?",
                tuple(values),
            )
            connection.commit()
        return self.get_job(job_id)

    def mark_processing(self, job_id: str, *, message: str = "任务处理中") -> dict[str, Any] | None:
        return self.update_job(
            job_id,
            status="processing",
            progress=12,
            message=message,
            started_at=utc_now(),
        )

    def mark_progress(self, job_id: str, *, progress: int, message: str) -> dict[str, Any] | None:
        return self.update_job(job_id, progress=progress, message=message)

    def mark_success(
        self,
        job_id: str,
        *,
        result: dict[str, Any],
        message: str = "任务已完成",
    ) -> dict[str, Any] | None:
        return self.update_job(
            job_id,
            status="success",
            progress=100,
            message=message,
            result=result,
            finished_at=utc_now(),
        )

    def mark_failed(self, job_id: str, *, error_message: str) -> dict[str, Any] | None:
        return self.update_job(
            job_id,
            status="failed",
            progress=100,
            message="任务执行失败",
            error_message=error_message,
            finished_at=utc_now(),
        )

    def get_note_insight(self, scope_key: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM note_insights WHERE scope_key = ?",
                (scope_key,),
            ).fetchone()
        if row is None:
            return None
        try:
            references = json.loads(row["references_json"] or "[]")
        except json.JSONDecodeError:
            references = []
        try:
            sections = json.loads(row["sections_json"] or "{}")
        except json.JSONDecodeError:
            sections = {}
        return {
            "summary": row["summary"],
            "references": references,
            "sections": sections,
            "created_at": row["created_at"],
        }

    def save_note_insight(self, scope_key: str, result: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO note_insights (scope_key, summary, references_json, sections_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(scope_key) DO UPDATE SET
                    summary = excluded.summary,
                    references_json = excluded.references_json,
                    sections_json = excluded.sections_json,
                    created_at = excluded.created_at
                """,
                (
                    scope_key,
                    result.get("summary", ""),
                    json.dumps(result.get("references", []), ensure_ascii=False),
                    json.dumps(result.get("sections", {}), ensure_ascii=False),
                    utc_now(),
                ),
            )
            connection.commit()

    def get_graph_analysis(self, scope_key: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM graph_analyses WHERE scope_key = ?",
                (scope_key,),
            ).fetchone()
        if row is None:
            return None
        try:
            payload = json.loads(row["payload_json"] or "{}")
        except json.JSONDecodeError:
            payload = {}
        return payload if isinstance(payload, dict) else None

    def save_graph_analysis(self, scope_key: str, payload: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO graph_analyses (scope_key, payload_json, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(scope_key) DO UPDATE SET
                    payload_json = excluded.payload_json,
                    created_at = excluded.created_at
                """,
                (
                    scope_key,
                    json.dumps(payload, ensure_ascii=False),
                    utc_now(),
                ),
            )
            connection.commit()

    def _serialize_row(self, row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None

        payload = {}
        result = None
        try:
            payload = json.loads(row["payload_json"] or "{}")
        except json.JSONDecodeError:
            payload = {}
        try:
            result = json.loads(row["result_json"]) if row["result_json"] else None
        except json.JSONDecodeError:
            result = None

        return {
            "id": row["id"],
            "job_type": row["job_type"],
            "status": row["status"],
            "resource_type": row["resource_type"],
            "resource_id": row["resource_id"],
            "payload": payload,
            "result": result,
            "error_message": row["error_message"] or "",
            "progress": int(row["progress"] or 0),
            "message": row["message"] or "",
            "created_at": row["created_at"],
            "started_at": row["started_at"] or "",
            "finished_at": row["finished_at"] or "",
        }


job_repository = JobRepository()
