from flask import Blueprint, current_app, jsonify

from ..services.task_runner import enqueue_book_summary, generate_book_summary_sync
from ..services.vault_parser import vault_repository
from .errors import error_response

books_bp = Blueprint("books", __name__)


@books_bp.get("")
def list_books():
    data = vault_repository.load()
    return jsonify({"items": data["books"]})


@books_bp.get("/<int:book_id>")
def book_detail(book_id: int):
    book = vault_repository.get_book(book_id)
    if book is None:
        return error_response("BOOK_NOT_FOUND", "Book not found", 404)

    summary = vault_repository.get_cached_summary(book_id)
    return jsonify({"book": book, "summary": summary or ""})


@books_bp.get("/<int:book_id>/summary")
def book_summary(book_id: int):
    data = vault_repository.load()
    book = next((item for item in data["books"] if item["id"] == book_id), None)

    if book is None:
        return error_response("BOOK_NOT_FOUND", "Book not found", 404)

    cached_summary = vault_repository.get_cached_summary(book_id)
    if cached_summary:
        return jsonify({"book_id": book_id, "summary": cached_summary, "cached": True, "status": "success"})

    if current_app.config.get("DEMO_DATA_ONLY", False):
        # 演示站里优先返回同步 fallback，避免用户还要等待后台任务，也避免触发外部模型调用。
        summary = generate_book_summary_sync(current_app._get_current_object(), book_id)
        vault_repository.save_book_summary(book_id, summary)
        return jsonify(
            {"book_id": book_id, "summary": summary, "cached": False, "status": "success", "mode": "fallback"}
        )

    job = enqueue_book_summary(current_app._get_current_object(), book_id)
    return (
        jsonify(
            {
                "book_id": book_id,
                "summary": "",
                "cached": False,
                "status": job["status"],
                "job_id": job["id"],
                "message": job["message"],
            }
        ),
        202,
    )


@books_bp.post("/<int:book_id>/summary/regenerate")
def regenerate_book_summary(book_id: int):
    data = vault_repository.load()
    book = next((item for item in data["books"] if item["id"] == book_id), None)

    if book is None:
        return error_response("BOOK_NOT_FOUND", "Book not found", 404)

    if current_app.config.get("DEMO_DATA_ONLY", False):
        summary = generate_book_summary_sync(current_app._get_current_object(), book_id)
        vault_repository.save_book_summary(book_id, summary)
        return jsonify(
            {"book_id": book_id, "summary": summary, "regenerated": True, "status": "success", "mode": "fallback"}
        )

    job = enqueue_book_summary(current_app._get_current_object(), book_id, force=True)
    return (
        jsonify(
            {
                "book_id": book_id,
                "summary": "",
                "regenerated": True,
                "status": job["status"],
                "job_id": job["id"],
                "message": "正在重新生成摘要",
            }
        ),
        202,
    )
