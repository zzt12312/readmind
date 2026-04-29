from flask import Blueprint, current_app, jsonify, request

from ..services.job_repository import job_repository
from ..services.task_runner import retry_job
from .errors import error_response

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.get("")
def job_list():
    status = request.args.get("status", "", type=str)
    job_type = request.args.get("job_type", "", type=str)
    limit = request.args.get("limit", 50, type=int)
    items = job_repository.list_jobs(limit=max(1, min(limit, 100)))
    if status:
        items = [item for item in items if item["status"] == status]
    if job_type:
        items = [item for item in items if item["job_type"] == job_type]
    return jsonify({"items": items})


@jobs_bp.get("/<job_id>")
def job_detail(job_id: str):
    job = job_repository.get_job(job_id)
    if job is None:
        return error_response("JOB_NOT_FOUND", "Job not found", 404)
    return jsonify(job)


@jobs_bp.post("/<job_id>/retry")
def retry_job_by_id(job_id: str):
    job = job_repository.get_job(job_id)
    if job is None:
        return error_response("JOB_NOT_FOUND", "Job not found", 404)
    retried = retry_job(current_app._get_current_object(), job)
    return jsonify(retried), 202
