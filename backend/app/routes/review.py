from flask import Blueprint, jsonify, request

from ..services.vault_parser import build_review_overview, build_review_payload_with_scope, vault_repository

review_bp = Blueprint("review", __name__)


@review_bp.get("/today")
def today():
    data = vault_repository.load()
    tag = request.args.get("tag", "", type=str)
    book_id = request.args.get("book_id", type=int)
    return jsonify(build_review_payload_with_scope(data, tag=tag, book_id=book_id))


@review_bp.post("/rate")
def rate_review():
    payload = request.get_json(silent=True) or {}
    note_id = payload.get("note_id")
    level = str(payload.get("level") or "").strip()

    if not isinstance(note_id, int) or level not in {"low", "medium", "high"}:
        return jsonify({"message": "note_id 和 level 参数不合法"}), 400

    progress = vault_repository.record_review_result(note_id, level)
    data = vault_repository.load()
    overview = build_review_overview(data)

    return jsonify(
        {
            "progress": progress,
            "summary": [
                {"label": "待复习", "value": str(overview["due_count"])},
                {"label": "连续复习", "value": f"{overview['streak_days']} 天"},
                {"label": "掌握率", "value": overview["mastery_rate"]},
            ],
        }
    )
