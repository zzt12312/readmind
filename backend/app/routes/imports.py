from itertools import count

from flask import Blueprint, current_app, jsonify, request

from ..services.job_repository import job_repository
from ..services.task_runner import enqueue_vault_sync

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


@import_bp.get("/jobs")
def jobs():
    async_jobs = job_repository.list_jobs(job_types=["vault_sync"], limit=20)
    items = [serialize_async_import_job(job) for job in async_jobs] + [serialize_import_job(job) for job in JOBS]
    return jsonify({"items": items})


@import_bp.post("/jobs")
def create_job():
    uploaded_files = request.files.getlist("files")

    if not uploaded_files:
        return jsonify({"message": "No files uploaded"}), 400

    created_jobs = []

    for uploaded_file in uploaded_files:
        filename = uploaded_file.filename or f"import-{next(_job_id)}.md"
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

    return jsonify({"items": created_jobs}), 201


@import_bp.post("/sync-local")
def sync_local_vault():
    job = enqueue_vault_sync(current_app._get_current_object())
    return jsonify({"item": serialize_async_import_job(job), "job_id": job["id"]}), 202
