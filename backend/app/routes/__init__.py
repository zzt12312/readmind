from flask import Flask

from .analytics import analytics_bp
from .books import books_bp
from .dashboard import dashboard_bp
from .health import health_bp
from .imports import import_bp
from .insights import insights_bp
from .jobs import jobs_bp
from .llm import llm_bp
from .notes import notes_bp
from .qa import qa_bp
from .review import review_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(llm_bp, url_prefix="/api/llm")
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(import_bp, url_prefix="/api/import")
    app.register_blueprint(insights_bp, url_prefix="/api/insights")
    app.register_blueprint(books_bp, url_prefix="/api/books")
    app.register_blueprint(notes_bp, url_prefix="/api/notes")
    app.register_blueprint(qa_bp, url_prefix="/api/qa")
    app.register_blueprint(review_bp, url_prefix="/api/review")
