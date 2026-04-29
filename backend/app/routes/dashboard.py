from flask import Blueprint, jsonify

from ..services.payloads.dashboard import build_dashboard_payload
from ..services.review.payloads import build_review_overview
from ..services.vault_parser import vault_repository

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/overview")
def overview():
    data = vault_repository.load()
    review_state = build_review_overview(data, vault_repository)
    return jsonify(build_dashboard_payload(data, review_state))
