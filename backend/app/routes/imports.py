from itertools import count

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
        result_text = job.get("error_message") or "同步失败"

    return {
        "id": job["id"],
        "file_name": "本地 Obsidian 书籍阅读目录",
        "status": "processing" if job["status"] in {"queued", "processing"} else ("failed" if job["status"] == "failed" else "success"),
        "progress": job.get("progress", 0),
        "result": result_text,
    }


def build_import_meta() -> dict:
    demo_mode = bool(current_app.config.get("DEMO_DATA_ONLY", False))
    return {
        "demo_mode": demo_mode,
        "source_label": "演示数据集（已预置真实阅读缓存）" if demo_mode else "本地 Obsidian 书籍阅读目录",
        "description": (
            "当前演示站使用预置缓存数据，方便完整体验书库、问答、图谱和复习功能。"
            if demo_mode
            else "系统会重新扫描本地 Obsidian 阅读目录，并更新书库缓存。"
        ),
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
            }
        )
    else:
        items.extend(serialize_import_job(job) for job in JOBS)

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
