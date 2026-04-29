from flask import Blueprint, jsonify

from ..services.payloads.analytics import build_analytics_payload
from ..services.vault_parser import vault_repository

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/overview")
def overview():
    data = vault_repository.load()
    return jsonify(build_analytics_payload(data, vault_repository))
