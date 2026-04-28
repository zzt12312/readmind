from flask import Blueprint, jsonify

from ..services.vault_parser import build_dashboard_payload, vault_repository

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/overview")
def overview():
    data = vault_repository.load()
    return jsonify(build_dashboard_payload(data))
