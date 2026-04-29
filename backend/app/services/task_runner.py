"""Local background job orchestration.

ReadMind is currently a local-first app, so background work runs in a small
in-process `ThreadPoolExecutor` and persists status to SQLite through
`job_repository`. This is intentionally simple for local demos, but it is not a
distributed production queue: queued jobs are not recovered across process
crashes and workers do not run across multiple machines.

If the project later targets server deployment, this module is the seam to
replace with Celery/RQ/Arq or a `TaskQueue` interface.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from flask import Flask

from .graph_analysis_service import build_graph_scope_key, generate_topic_graph_sync
from .job_repository import job_repository
from .llm_client import LLMClientError, create_llm_client
from .note_insight_service import build_insight_scope_key, generate_notes_insight_sync
from .vault_parser import build_book_context, format_book_context, vault_repository

executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="readmind-job")


def build_book_fallback(book: dict[str, Any]) -> str:
    summary_parts = [
        f"《{book['title']}》收录了 {book['notes']} 条高亮。",
        f"分类为 {book['category']}。",
    ]
    if book["tags"]:
        summary_parts.append(f"从当前解析结果看，核心主题包括：{'、'.join(book['tags'])}。")
    if book["reading_notes"]:
        summary_parts.append(f"你在“读书笔记”分区里还留下了这些内容：{book['reading_notes'][:80]}")
    return "".join(summary_parts)


def generate_book_summary_sync(app: Flask, book_id: int) -> str:
    with app.app_context():
        data = vault_repository.load()
        book = next((item for item in data["books"] if item["id"] == book_id), None)
        if book is None:
            raise ValueError("Book not found")

        fallback_summary = build_book_fallback(book)
        context = build_book_context(data, book_id)
        if context is None:
            return fallback_summary

        try:
            client = create_llm_client(app.config)
            return client.chat(
                system_prompt=(
                    "你是一个阅读笔记整理助手。"
                    "请基于用户给出的真实读书摘录，输出一段中文摘要。"
                    "要求：1. 只基于提供内容，不要编造；2. 先概括主题，再提炼 3 到 5 个关键观点；"
                    "3. 语言简洁、适合在知识管理产品中展示。"
                ),
                messages=[{"role": "user", "content": format_book_context(context)}],
                max_completion_tokens=700,
            )
        except LLMClientError:
            return fallback_summary


def enqueue_book_summary(app: Flask, book_id: int, *, force: bool = False) -> dict[str, Any]:
    active_job = None if force else job_repository.find_active_job(
        job_type="book_summary",
        resource_type="book",
        resource_id=str(book_id),
    )
    if active_job:
        return active_job

    job = job_repository.create_job(
        job_type="book_summary",
        resource_type="book",
        resource_id=str(book_id),
        payload={"book_id": book_id, "force": force},
        message="摘要任务已进入队列",
    )

    # 这里把 Flask app 实例显式传入后台线程，避免在 request context 结束后读取不到配置。
    executor.submit(run_book_summary_job, app, job["id"], book_id)
    return job


def run_book_summary_job(app: Flask, job_id: str, book_id: int) -> None:
    try:
        job_repository.mark_processing(job_id, message="正在整理书籍上下文")
        job_repository.mark_progress(job_id, progress=36, message="正在生成摘要")
        summary = generate_book_summary_sync(app, book_id)
        job_repository.mark_progress(job_id, progress=84, message="正在写入摘要缓存")
        vault_repository.save_book_summary(book_id, summary)
        job_repository.mark_success(
            job_id,
            result={"book_id": book_id, "summary": summary},
            message="摘要生成完成",
        )
    except Exception as exc:  # noqa: BLE001 - background task must never crash silently
        job_repository.mark_failed(job_id, error_message=str(exc))


def enqueue_notes_insight(app: Flask, payload: dict[str, Any]) -> dict[str, Any]:
    scope_key = build_insight_scope_key(payload)
    active_job = job_repository.find_active_job(
        job_type="notes_insight",
        resource_type="note_scope",
        resource_id=scope_key,
    )
    if active_job:
        return active_job

    job = job_repository.create_job(
        job_type="notes_insight",
        resource_type="note_scope",
        resource_id=scope_key,
        payload=payload,
        message="洞察任务已进入队列",
    )
    executor.submit(run_notes_insight_job, app, job["id"], payload, scope_key)
    return job


def run_notes_insight_job(app: Flask, job_id: str, payload: dict[str, Any], scope_key: str) -> None:
    try:
        job_repository.mark_processing(job_id, message="正在整理筛选范围")
        job_repository.mark_progress(job_id, progress=34, message="正在生成洞察")
        result = generate_notes_insight_sync(app.config, payload)
        job_repository.mark_progress(job_id, progress=82, message="正在写入洞察缓存")
        job_repository.save_note_insight(scope_key, result)
        job_repository.mark_success(
            job_id,
            result=result,
            message="AI 洞察已生成",
        )
    except Exception as exc:  # noqa: BLE001 - background task must never crash silently
        job_repository.mark_failed(job_id, error_message=str(exc))


def enqueue_vault_sync(app: Flask) -> dict[str, Any]:
    active_job = job_repository.find_active_job(
        job_type="vault_sync",
        resource_type="vault",
        resource_id="local-library",
    )
    if active_job:
        return active_job

    job = job_repository.create_job(
        job_type="vault_sync",
        resource_type="vault",
        resource_id="local-library",
        payload={},
        message="本地书库同步任务已进入队列",
    )
    executor.submit(run_vault_sync_job, job["id"])
    return job


def run_vault_sync_job(job_id: str) -> None:
    try:
        job_repository.mark_processing(job_id, message="正在扫描本地 Obsidian 书库")
        job_repository.mark_progress(job_id, progress=24, message="正在解析 Markdown 内容")
        job_repository.mark_progress(job_id, progress=56, message="正在重建 embedding 索引")
        data = vault_repository.load(force_refresh=True)
        job_repository.mark_progress(job_id, progress=90, message="正在写入本地缓存")
        job_repository.mark_success(
            job_id,
            result={
                "book_count": data["stats"]["book_count"],
                "note_count": data["stats"]["note_count"],
                "category_count": data["stats"]["category_count"],
            },
            message="本地书库同步完成",
        )
    except Exception as exc:  # noqa: BLE001 - background task must never crash silently
        job_repository.mark_failed(job_id, error_message=str(exc))


def enqueue_graph_analysis(app: Flask, payload: dict[str, Any]) -> dict[str, Any]:
    scope_key = build_graph_scope_key(
        category=payload.get("category", ""),
        book_id=payload.get("book_id"),
        time_scope=payload.get("time_scope", "all"),
        mode=payload.get("mode", "category"),
    )
    active_job = job_repository.find_active_job(
        job_type="graph_analysis",
        resource_type="graph_scope",
        resource_id=scope_key,
    )
    if active_job:
        return active_job

    job = job_repository.create_job(
        job_type="graph_analysis",
        resource_type="graph_scope",
        resource_id=scope_key,
        payload=payload,
        message="图谱分析任务已进入队列",
    )
    executor.submit(run_graph_analysis_job, job["id"], payload, scope_key)
    return job


def run_graph_analysis_job(job_id: str, payload: dict[str, Any], scope_key: str) -> None:
    try:
        job_repository.mark_processing(job_id, message="正在整理图谱分析范围")
        job_repository.mark_progress(job_id, progress=28, message="正在聚合主题关系")
        result = generate_topic_graph_sync(
            category=payload.get("category", ""),
            book_id=payload.get("book_id"),
            time_scope=payload.get("time_scope", "all"),
            mode=payload.get("mode", "category"),
        )
        job_repository.mark_progress(job_id, progress=82, message="正在写入图谱缓存")
        job_repository.save_graph_analysis(scope_key, result)
        job_repository.mark_success(
            job_id,
            result=result,
            message="图谱分析完成",
        )
    except Exception as exc:  # noqa: BLE001 - background task must never crash silently
        job_repository.mark_failed(job_id, error_message=str(exc))


def retry_job(app: Flask, job: dict[str, Any]) -> dict[str, Any]:
    job_type = job.get("job_type")
    payload = job.get("payload") or {}

    if job_type == "book_summary":
        book_id = payload.get("book_id") or job.get("resource_id")
        return enqueue_book_summary(app, int(book_id), force=True)
    if job_type == "notes_insight":
        return enqueue_notes_insight(app, payload)
    if job_type == "vault_sync":
        return enqueue_vault_sync(app)
    if job_type == "graph_analysis":
        return enqueue_graph_analysis(app, payload)

    raise ValueError(f"Unsupported job type: {job_type}")
