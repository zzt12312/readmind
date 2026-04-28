from flask import Blueprint, current_app, jsonify, request

from ..services.job_repository import job_repository
from ..services.note_insight_service import build_insight_scope_key
from ..services.task_runner import enqueue_notes_insight
from ..services.vault_parser import build_notes_payload, vault_repository

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
