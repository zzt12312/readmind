from itertools import count
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from ..services.job_repository import job_repository
from ..services.task_runner import enqueue_vault_sync
from ..services.vault_parser import vault_repository

import_bp = Blueprint("import", __name__)

_job_id = count(start=3)
JOBS = [
    {
        "id": 1,
        "file_name": "wechat-reading-2026.zip",
        "status": "processing",
        "progress": 68,
        "result": "120 / 3",
    },
    {
        "id": 2,
        "file_name": "cognition-awakening.md",
        "status": "success",
        "progress": 100,
        "result": "32 / 0",
    },
]


def _scan_vault_health() -> dict:
    vault_root = Path(current_app.config.get("VAULT_ROOT", "")).expanduser()
    if current_app.config.get("DEMO_DATA_ONLY", False):
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


def _humanize_job_error(error_message: str) -> str:
    if not error_message:
        return "同步失败"
    if "directory_count" in error_message:
        return "同步统计字段缺失，请重新同步或清理缓存后重试。"
    return error_message


def serialize_import_job(item: dict) -> dict:
    return {
        "id": item["id"],
        "file_name": item["file_name"],
        "status": item["status"],
        "progress": item["progress"],
        "result": item["result"],
    }


def serialize_async_import_job(job: dict) -> dict:
    result = job.get("result") or {}
    result_text = job.get("message") or ""
    if job["status"] == "success" and result:
        result_text = f"{result.get('book_count', 0)} 本 / {result.get('note_count', 0)} 条"
    elif job["status"] == "failed":
        result_text = _humanize_job_error(job.get("error_message") or "")

    return {
        "id": job["id"],
        "file_name": "本地 Obsidian 书籍阅读目录",
        "status": "processing" if job["status"] in {"queued", "processing"} else ("failed" if job["status"] == "failed" else "success"),
        "progress": job.get("progress", 0),
        "result": result_text,
        "source": "sync-local",
        "created_at": job.get("created_at", ""),
        "finished_at": job.get("finished_at", ""),
    }


def build_import_meta() -> dict:
    demo_mode = bool(current_app.config.get("DEMO_DATA_ONLY", False))
    vault_health = _scan_vault_health()
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


@import_bp.get("/jobs")
def jobs():
    demo_mode = bool(current_app.config.get("DEMO_DATA_ONLY", False))
    async_jobs = [] if demo_mode else job_repository.list_jobs(job_types=["vault_sync"], limit=20)
    items = [serialize_async_import_job(job) for job in async_jobs]

    if demo_mode:
        data = vault_repository.load()
        items.append(
            {
                "id": "demo-import",
                "file_name": "演示数据集（静态缓存）",
                "status": "success",
                "progress": 100,
                "result": f"{data['stats']['book_count']} 本 / {data['stats']['note_count']} 条",
                "source": "demo-cache",
                "created_at": "",
                "finished_at": "",
            }
        )

    return jsonify({"items": items, "meta": build_import_meta()})


@import_bp.post("/jobs")
def create_job():
    uploaded_files = request.files.getlist("files")

    if not uploaded_files:
        return jsonify({"message": "No files uploaded"}), 400

    created_jobs = []

    for uploaded_file in uploaded_files:
        filename = uploaded_file.filename or f"import-{next(_job_id)}.md"
        if current_app.config.get("DEMO_DATA_ONLY", False):
            created_jobs.append(
                {
                    "id": next(_job_id),
                    "file_name": filename,
                    "status": "success",
                    "progress": 100,
                    "result": "演示模式：已模拟导入",
                }
            )
            continue
        status = "success" if filename.endswith((".md", ".markdown", ".zip")) else "failed"
        created_jobs.append(
            {
                "id": next(_job_id),
                "file_name": filename,
                "status": status,
                "progress": 100 if status == "success" else 0,
                "result": "1 / 0" if status == "success" else "0 / 1",
            }
        )

    JOBS[:0] = created_jobs

    return jsonify({"items": created_jobs, "meta": build_import_meta()}), 201


@import_bp.post("/sync-local")
def sync_local_vault():
    if current_app.config.get("DEMO_DATA_ONLY", False):
        data = vault_repository.load()
        item = {
            "id": "demo-sync",
            "file_name": "演示数据集（静态缓存）",
            "status": "success",
            "progress": 100,
            "result": f"{data['stats']['book_count']} 本 / {data['stats']['note_count']} 条",
        }
        return jsonify({"item": item, "message": "演示数据已就绪，无需重新同步", "meta": build_import_meta()})

    job = enqueue_vault_sync(current_app._get_current_object())
    return jsonify({"item": serialize_async_import_job(job), "job_id": job["id"], "meta": build_import_meta()}), 202
