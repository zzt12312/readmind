from flask import Blueprint, current_app, jsonify, request

from ..services.graph_analysis_service import build_graph_scope_key
from ..services.job_repository import job_repository
from ..services.task_runner import enqueue_graph_analysis

insights_bp = Blueprint("insights", __name__)


@insights_bp.get("/topics")
def topics_graph():
    category = request.args.get("category", "", type=str)
    book_id = request.args.get("book_id", type=int)
    time_scope = request.args.get("time_scope", "all", type=str)
    mode = request.args.get("mode", "category", type=str)
    scope_key = build_graph_scope_key(
        category=category,
        book_id=book_id,
        time_scope=time_scope,
        mode=mode,
    )
    cached = job_repository.get_graph_analysis(scope_key)
    if cached:
        return jsonify(cached)

    job = enqueue_graph_analysis(
        current_app._get_current_object(),
        {
            "category": category,
            "book_id": book_id,
            "time_scope": time_scope,
            "mode": mode,
        },
    )
    return (
        jsonify(
            {
                "overview": None,
                "filters": None,
                "clusters": [],
                "graph": {"nodes": [], "links": []},
                "status": job["status"],
                "job_id": job["id"],
                "message": job["message"],
            }
        ),
        202,
    )
