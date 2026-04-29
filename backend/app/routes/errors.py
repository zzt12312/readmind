from __future__ import annotations

from flask import jsonify


def error_response(code: str, message: str, status: int = 400, detail: str = ""):
    return jsonify({"error": {"code": code, "message": message, "detail": detail}}), status

