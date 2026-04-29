"""Import-center business helpers.

Routes should only read HTTP input and return JSON. This module owns the
import-center rules that are not HTTP-specific: vault health checks, demo-mode
payloads, and async job serialization. Real-mode imports intentionally only use
the local Obsidian sync path so new users never mistake fake upload jobs for a
completed production feature.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def scan_vault_health(config: dict[str, Any]) -> dict[str, Any]:
    vault_root = Path(config.get("VAULT_ROOT", "")).expanduser()
    if config.get("DEMO_DATA_ONLY", False):
        return {
            "vault_root": str(vault_root),
            "vault_status": "ready",
            "vault_message": "演示模式使用预置缓存数据，不会扫描你的本地阅读目录。",
            "markdown_count": 0,
        }

    if not vault_root.exists():
        return {
            "vault_root": str(vault_root),
            "vault_status": "missing",
            "vault_message": "当前路径不存在，请检查 .env 中的 VAULT_ROOT。",
            "markdown_count": 0,
        }

    if not vault_root.is_dir():
        return {
            "vault_root": str(vault_root),
            "vault_status": "invalid",
            "vault_message": "当前路径不是文件夹，请确认 VAULT_ROOT 指向 Obsidian 阅读目录。",
            "markdown_count": 0,
        }

    markdown_count = sum(1 for _ in vault_root.rglob("*.md"))
    if markdown_count == 0:
        return {
            "vault_root": str(vault_root),
            "vault_status": "empty",
            "vault_message": "目录存在，但暂未发现 Markdown 笔记文件。",
            "markdown_count": 0,
        }

    return {
        "vault_root": str(vault_root),
        "vault_status": "ready",
        "vault_message": f"当前目录可用，已发现 {markdown_count} 个 Markdown 文件。",
        "markdown_count": markdown_count,
    }


def humanize_job_error(error_message: str) -> str:
    if not error_message:
        return "同步失败"
    if "directory_count" in error_message:
        return "同步统计字段缺失，请重新同步或清理缓存后重试。"
    return error_message


def serialize_async_import_job(job: dict[str, Any]) -> dict[str, Any]:
    result = job.get("result") or {}
    result_text = job.get("message") or ""
    if job["status"] == "success" and result:
        result_text = f"{result.get('book_count', 0)} 本 / {result.get('note_count', 0)} 条"
    elif job["status"] == "failed":
        result_text = humanize_job_error(job.get("error_message") or "")

    return {
        "id": job["id"],
        "file_name": "本地 Obsidian 书籍阅读目录",
        "status": normalize_job_status(job["status"]),
        "progress": job.get("progress", 0),
        "result": result_text,
        "source": "sync-local",
        "created_at": job.get("created_at", ""),
        "finished_at": job.get("finished_at", ""),
    }


def normalize_job_status(status: str) -> str:
    if status in {"queued", "processing"}:
        return "processing"
    if status == "failed":
        return "failed"
    return "success"


def build_import_meta(config: dict[str, Any]) -> dict[str, Any]:
    demo_mode = bool(config.get("DEMO_DATA_ONLY", False))
    vault_health = scan_vault_health(config)
    return {
        "demo_mode": demo_mode,
        "source_label": "演示数据集（已预置真实阅读缓存）" if demo_mode else "本地 Obsidian 书籍阅读目录",
        "description": (
            "当前演示站使用预置缓存数据，方便完整体验书库、问答、图谱和复习功能。"
            if demo_mode
            else "系统会重新扫描本地 Obsidian 阅读目录，并更新书库缓存。"
        ),
        **vault_health,
    }


def build_demo_import_item(data: dict[str, Any], *, item_id: str = "demo-import") -> dict[str, Any]:
    return {
        "id": item_id,
        "file_name": "演示数据集（静态缓存）",
        "status": "success",
        "progress": 100,
        "result": f"{data['stats']['book_count']} 本 / {data['stats']['note_count']} 条",
        "source": "demo-cache",
        "created_at": "",
        "finished_at": "",
    }


def build_import_jobs_payload(
    *,
    config: dict[str, Any],
    repository: Any,
    job_repository: Any,
) -> dict[str, Any]:
    demo_mode = bool(config.get("DEMO_DATA_ONLY", False))
    async_jobs = [] if demo_mode else job_repository.list_jobs(job_types=["vault_sync"], limit=20)
    items = [serialize_async_import_job(job) for job in async_jobs]

    if demo_mode:
        items.append(build_demo_import_item(repository.load()))

    return {"items": items, "meta": build_import_meta(config)}


def build_demo_upload_import_jobs(uploaded_files: list[Any]) -> list[dict[str, Any]]:
    """Return stateless demo-only upload rows for the import center.

    The open-source version currently supports real imports through local vault
    sync. Upload rows are kept only so the demo site can show how a future upload
    flow would look, without persisting misleading jobs in real deployments.
    """

    created_jobs = []
    for index, uploaded_file in enumerate(uploaded_files, start=1):
        filename = uploaded_file.filename or f"demo-import-{index}.md"
        created_jobs.append(
            {
                "id": f"demo-upload-{index}",
                "file_name": filename,
                "status": "success",
                "progress": 100,
                "result": "演示模式：已模拟导入",
                "source": "demo-upload",
                "created_at": "",
                "finished_at": "",
            }
        )

    return created_jobs
