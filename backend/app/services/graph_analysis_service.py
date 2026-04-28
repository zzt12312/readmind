from __future__ import annotations

import hashlib
import json
from typing import Any

from .vault_parser import (
    build_category_graph_payload,
    build_filtered_topic_graph_payload,
    vault_repository,
)


def build_graph_scope_key(
    *,
    category: str = "",
    book_id: int | None = None,
    time_scope: str = "all",
    mode: str = "category",
) -> str:
    payload = {
        "category": category.strip(),
        "book_id": book_id,
        "time_scope": time_scope,
        "mode": mode,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def generate_topic_graph_sync(
    *,
    category: str = "",
    book_id: int | None = None,
    time_scope: str = "all",
    mode: str = "category",
) -> dict[str, Any]:
    data = vault_repository.load()
    if mode == "topic":
        return build_filtered_topic_graph_payload(
            data,
            category=category,
            book_id=book_id,
            time_scope=time_scope,
        )
    return build_category_graph_payload(
        data,
        category=category,
        book_id=book_id,
        time_scope=time_scope,
    )
