from pathlib import Path

from flask import Flask
from flask_cors import CORS

from .config import Config
from .routes import register_blueprints
from .services.vault_parser import embedding_service, vault_repository


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)
    embedding_service.model_name = app.config.get("EMBEDDING_MODEL", embedding_service.model_name)
    vault_repository.root = Path(app.config.get("VAULT_ROOT", vault_repository.root))
    vault_repository.demo_data_only = bool(app.config.get("DEMO_DATA_ONLY", False))

    register_blueprints(app)

    return app
