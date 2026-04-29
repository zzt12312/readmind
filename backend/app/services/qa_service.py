"""QA prompt, evidence, and streaming helpers.

`routes/qa.py` still handles the HTTP/SSE boundary, while this module owns the
pieces that can be tested without Flask: evidence summaries, LLM message
construction, and deterministic chunking for fallback streaming responses.
"""

from __future__ import annotations

from typing import Any

from .vault_parser import format_qa_context

SYSTEM_PROMPT = (
    "你是一个基于个人读书笔记回答问题的中文助手。"
    "只能依据提供的摘录作答，不要凭空补充书外事实。"
    "回答要求：1. 先直接回答问题；2. 再用 2 到 4 点归纳关键结论；"
    "3. 如果证据不足，要明确说明；4. 不要输出<think>；"
    "5. 若当前检索范围限定为单本书，不要引用其他书。"
)


def build_evidence_summary(references: list[dict[str, Any]]) -> dict[str, Any]:
    reference_count = len(references)
    suggested_points = min(3, reference_count) if reference_count else 0
    sufficient = reference_count >= 3
    if reference_count == 0:
        message = "当前没有命中可引用的笔记，回答只能基于回退逻辑生成。"
    elif sufficient:
        message = f"当前命中 {reference_count} 条引用，足以支撑一轮较完整的回答。"
    else:
        message = f"当前仅命中 {reference_count} 条引用，更适合回答 {suggested_points} 个重点。"
    return {
        "reference_count": reference_count,
        "suggested_points": suggested_points,
        "sufficient": sufficient,
        "message": message,
    }


def build_llm_messages(
    history: list[dict[str, Any]],
    question: str,
    references: list[dict[str, Any]],
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for item in history[-8:]:
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    # The final user message carries retrieval context so the model stays grounded in notes.
    messages.append({"role": "user", "content": format_qa_context(question, references)})
    return messages


def split_stream_chunks(text: str, step: int = 24) -> list[str]:
    return [text[index : index + step] for index in range(0, len(text), step)] or [text]
