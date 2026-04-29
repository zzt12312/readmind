from flask import Blueprint, current_app, jsonify, request

from ..services.import_service import (
    build_demo_import_item,
    build_demo_upload_import_jobs,
    build_import_jobs_payload,
    build_import_meta,
    serialize_async_import_job,
)
from ..services.job_repository import job_repository
from ..services.task_runner import enqueue_vault_sync
from ..services.vault_parser import vault_repository
from .errors import error_response

import_bp = Blueprint("import", __name__)


@import_bp.get("/jobs")
def jobs():
    return jsonify(
        build_import_jobs_payload(
            config=current_app.config,
            repository=vault_repository,
            job_repository=job_repository,
        )
    )


@import_bp.post("/jobs")
def create_job():
    uploaded_files = request.files.getlist("files")

    if not uploaded_files:
        return error_response("NO_FILES_UPLOADED", "No files uploaded", 400)

    if not current_app.config.get("DEMO_DATA_ONLY", False):
        return error_response(
            "UPLOAD_IMPORT_UNAVAILABLE",
            "当前版本暂不支持直接上传文件导入，请使用本地 Obsidian 目录同步。",
            501,
        )

    created_jobs = build_demo_upload_import_jobs(uploaded_files)
    return jsonify({"items": created_jobs, "meta": build_import_meta(current_app.config)}), 201


@import_bp.post("/sync-local")
def sync_local_vault():
    if current_app.config.get("DEMO_DATA_ONLY", False):
        data = vault_repository.load()
        item = build_demo_import_item(data, item_id="demo-sync")
        return jsonify(
            {
                "item": item,
                "message": "演示数据已就绪，无需重新同步",
                "meta": build_import_meta(current_app.config),
            }
        )

    job = enqueue_vault_sync(current_app._get_current_object())
    return (
        jsonify(
            {
                "item": serialize_async_import_job(job),
                "job_id": job["id"],
                "meta": build_import_meta(current_app.config),
            }
        ),
        202,
    )
