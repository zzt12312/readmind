from flask import Blueprint, jsonify, request

from ..services.review.payloads import build_review_overview, build_review_payload_with_scope
from ..services.vault_parser import vault_repository
from .errors import error_response

review_bp = Blueprint("review", __name__)


@review_bp.get("/today")
def today():
    data = vault_repository.load()
    tag = request.args.get("tag", "", type=str)
    book_id = request.args.get("book_id", type=int)
    daily_goal = request.args.get("daily_goal", type=int)
    queue = request.args.get("queue", "due", type=str)
    return jsonify(
        build_review_payload_with_scope(
            data,
            vault_repository,
            tag=tag,
            book_id=book_id,
            daily_goal=daily_goal,
            queue=queue,
        )
    )


@review_bp.post("/rate")
def rate_review():
    payload = request.get_json(silent=True) or {}
    note_id = payload.get("note_id")
    level = str(payload.get("level") or "").strip()

    if not isinstance(note_id, int) or level not in {"low", "medium", "high"}:
        return error_response("INVALID_REVIEW_RATING", "note_id 和 level 参数不合法", 400)

    progress = vault_repository.record_review_result(note_id, level)
    data = vault_repository.load()
    overview = build_review_overview(data, vault_repository)

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
