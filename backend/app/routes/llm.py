from flask import Blueprint, current_app, jsonify

from ..services.minimax_client import LLMClientError, create_llm_client
from ..services.vault_parser import embedding_service

llm_bp = Blueprint("llm", __name__)


@llm_bp.get("/health")
def llm_health():
    config = current_app.config
    client = create_llm_client(config)
    api_key_loaded = bool(client.api_key)

    payload = {
        "provider": "deepseek",
        "base_url": client.base_url,
        "model": client.model,
        "api_key_loaded": api_key_loaded,
        "connected": False,
        "fallback_mode": True,
        "detail": "",
        "embedding_model": current_app.config.get("EMBEDDING_MODEL", ""),
        "embedding_provider": embedding_service.provider,
        "embedding_status": embedding_service.status,
        "embedding_error": embedding_service.last_error,
    }

    if not api_key_loaded:
        payload["detail"] = "Missing LLM API key"
        return jsonify(payload)

    try:
        reply = client.chat(
            system_prompt="You are a health check assistant. Reply with exactly OK.",
            messages=[{"role": "user", "content": "Reply with OK."}],
            max_completion_tokens=16,
        )
        payload["connected"] = True
        payload["fallback_mode"] = False
        payload["detail"] = reply[:80]
    except LLMClientError as error:
        payload["detail"] = str(error)

    return jsonify(payload)


@llm_bp.post("/embedding/warmup")
def warmup_embedding():
    started = embedding_service.start_warmup()
    return jsonify(
        {
            "started": started,
            "embedding_model": current_app.config.get("EMBEDDING_MODEL", ""),
            "embedding_provider": embedding_service.provider,
            "embedding_status": embedding_service.status,
            "embedding_error": embedding_service.last_error,
        }
    )
