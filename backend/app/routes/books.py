from flask import Blueprint, current_app, jsonify

from ..services.task_runner import enqueue_book_summary
from ..services.vault_parser import vault_repository

books_bp = Blueprint("books", __name__)


@books_bp.get("")
def list_books():
    data = vault_repository.load()
    return jsonify({"items": data["books"]})


@books_bp.get("/<int:book_id>")
def book_detail(book_id: int):
    book = vault_repository.get_book(book_id)
    if book is None:
        return jsonify({"message": "Book not found"}), 404

    summary = vault_repository.get_cached_summary(book_id)
    return jsonify({"book": book, "summary": summary or ""})


@books_bp.get("/<int:book_id>/summary")
def book_summary(book_id: int):
    data = vault_repository.load()
    book = next((item for item in data["books"] if item["id"] == book_id), None)

    if book is None:
        return jsonify({"message": "Book not found"}), 404

    cached_summary = vault_repository.get_cached_summary(book_id)
    if cached_summary:
        return jsonify({"book_id": book_id, "summary": cached_summary, "cached": True, "status": "success"})

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
        return jsonify({"message": "Book not found"}), 404

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
