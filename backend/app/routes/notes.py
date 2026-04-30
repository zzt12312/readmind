from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_from_directory

from ..services.job_repository import job_repository
from ..services.note_insight_service import build_insight_scope_key, export_note_insight_markdown, generate_notes_insight_sync
from ..services.payloads.notes import build_notes_payload
from ..services.task_runner import enqueue_notes_insight
from ..services.vault_parser import vault_repository

notes_bp = Blueprint("notes", __name__)


@notes_bp.get("")
def list_notes():
    book_id = request.args.get("book_id", type=int)
    note_id = request.args.get("note_id", type=int)
    query = request.args.get("q", "", type=str)
    category = request.args.get("category", "", type=str)
    tag = request.args.get("tag", "", type=str)
    chapter = request.args.get("chapter", "", type=str)
    sort = request.args.get("sort", "relevance", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 120, type=int)
    data = vault_repository.load()
    return jsonify(
        build_notes_payload(
            data,
            book_id=book_id,
            query=query,
            note_id=note_id,
            category=category,
            tag=tag,
            chapter=chapter,
            sort=sort,
            page=page,
            per_page=per_page,
        )
    )


@notes_bp.post("/summarize")
def summarize_notes():
    payload = request.get_json(silent=True) or {}
    scope_key = build_insight_scope_key(payload)
    cached = job_repository.get_note_insight(scope_key)
    if cached:
        return jsonify(cached)

    if current_app.config.get("DEMO_DATA_ONLY", False):
        # 演示模式直接返回本地结构化洞察，让页面始终可体验，不依赖异步任务和外部模型。
        result = generate_notes_insight_sync(current_app.config, payload)
        job_repository.save_note_insight(scope_key, result)
        return jsonify(result)

    job = enqueue_notes_insight(current_app._get_current_object(), payload)
    return (
        jsonify(
            {
                "summary": "",
                "references": [],
                "sections": None,
                "status": job["status"],
                "job_id": job["id"],
                "message": job["message"],
            }
        ),
        202,
    )


@notes_bp.post("/export-insight")
def export_insight():
    payload = request.get_json(silent=True) or {}
    summary = str(payload.get("summary") or "").strip()
    sections = payload.get("sections") if isinstance(payload.get("sections"), dict) else None
    if not summary and not sections:
        return jsonify({"error": {"code": "NOTE_INSIGHT_EXPORT_EMPTY", "message": "没有可导出的洞察内容", "detail": ""}}), 400

    result = export_note_insight_markdown(
        export_root=current_app.config["EXPORT_ROOT"],
        title=str(payload.get("title") or "笔记洞察"),
        scope=payload.get("scope") if isinstance(payload.get("scope"), dict) else {},
        summary=summary,
        sections=sections,
        references=payload.get("references") if isinstance(payload.get("references"), list) else [],
    )
    return jsonify(
        {
            **result,
            "download_url": f"/api/notes/exports/insights/{result['file_name']}",
            "message": "笔记洞察已导出为 Markdown",
        }
    )


@notes_bp.get("/exports/insights/<path:file_name>")
def download_insight_export(file_name: str):
    if Path(file_name).name != file_name or not file_name.endswith(".md"):
        return jsonify({"error": {"code": "NOTE_INSIGHT_EXPORT_NOT_FOUND", "message": "导出文件不存在", "detail": ""}}), 404
    export_dir = Path(current_app.config["EXPORT_ROOT"]).expanduser().resolve() / "insights"
    return send_from_directory(export_dir, file_name, as_attachment=True)
