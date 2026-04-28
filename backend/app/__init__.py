from flask import Flask
from flask_cors import CORS

from .config import Config
from .routes import register_blueprints
from .services.vault_parser import embedding_service


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)
    embedding_service.model_name = app.config.get("EMBEDDING_MODEL", embedding_service.model_name)

    register_blueprints(app)

    return app
