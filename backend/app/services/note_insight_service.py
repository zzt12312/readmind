from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from .minimax_client import LLMClientError, create_llm_client
from .vault_parser import build_notes_payload, format_qa_context, vault_repository


def build_insight_scope_key(payload: dict[str, Any]) -> str:
    normalized = {
        "book_id": payload.get("book_id"),
        "q": (payload.get("q") or "").strip(),
        "category": (payload.get("category") or "").strip(),
        "tag": (payload.get("tag") or "").strip(),
        "chapter": (payload.get("chapter") or "").strip(),
        "sort": payload.get("sort") or "relevance",
        "prompt": (payload.get("prompt") or "").strip(),
    }
    raw = json.dumps(normalized, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def build_structured_fallback(
    notes: list[dict[str, Any]],
    note_payload: dict[str, Any],
) -> dict[str, Any]:
    insight = note_payload["insight"]
    related_topics = insight["related_topics"][:4]
    primary_topic = related_topics[0] if related_topics else "当前筛选主题"
    return {
        "core_conclusion": insight["summary"],
        "key_themes": related_topics,
        "review_questions": [
            f"为什么“{primary_topic}”会反复出现在这些笔记里？",
            "如果只保留一条最值得复习的观点，它会是什么？",
            "这些摘录之间有没有互相补充或互相冲突的地方？",
        ],
        "action_suggestions": [
            "从引用依据里挑一条最有触动的摘录，补一条自己的解释。",
            "把当前主题整理成 3 句话，作为下一次复习入口。",
            "优先回看当前范围内最常出现的主题标签和对应章节。",
        ],
        "reasoning": f"本次洞察主要依据当前筛选结果中的 {len(notes)} 条摘录，以及高频主题 {('、'.join(related_topics) if related_topics else '当前范围关键词')} 得出。",
    }


def parse_structured_insight(raw_text: str, fallback: dict[str, Any]) -> dict[str, Any]:
    candidates = [raw_text.strip()]
    fenced_match = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, flags=re.DOTALL)
    if fenced_match:
        candidates.insert(0, fenced_match.group(1))
    brace_match = re.search(r"(\{.*\})", raw_text, flags=re.DOTALL)
    if brace_match:
        candidates.append(brace_match.group(1))

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue

        if not isinstance(parsed, dict):
            continue

        return {
            "core_conclusion": str(parsed.get("core_conclusion") or fallback["core_conclusion"]),
            "key_themes": [str(item) for item in parsed.get("key_themes", [])][:6] or fallback["key_themes"],
            "review_questions": [str(item) for item in parsed.get("review_questions", [])][:4] or fallback["review_questions"],
            "action_suggestions": [str(item) for item in parsed.get("action_suggestions", [])][:4] or fallback["action_suggestions"],
            "reasoning": str(parsed.get("reasoning") or fallback["reasoning"]),
        }

    return fallback


def generate_notes_insight_sync(config: Any, payload: dict[str, Any]) -> dict[str, Any]:
    data = vault_repository.load()
    note_payload = build_notes_payload(
        data,
        book_id=payload.get("book_id"),
        query=payload.get("q", ""),
        category=payload.get("category", ""),
        tag=payload.get("tag", ""),
        chapter=payload.get("chapter", ""),
        sort=payload.get("sort", "relevance"),
        page=1,
        per_page=40,
    )
    notes = note_payload["items"]
    fallback = note_payload["insight"]["summary"]

    if not notes:
        structured_fallback = build_structured_fallback(notes, note_payload)
        return {"summary": fallback, "references": [], "sections": structured_fallback}

    references = [
        {
            "book": note.get("book_title", ""),
            "chapter": note.get("chapter", ""),
            "excerpt": note.get("excerpt", ""),
        }
        for note in notes[:12]
    ]

    prompt = payload.get("prompt") or "请基于当前筛选结果，总结这些笔记的共性主题和最值得回看的观点。"
    structured_fallback = build_structured_fallback(notes, note_payload)

    try:
        client = create_llm_client(config)
        raw_response = client.chat(
            system_prompt=(
                "你是一个读书笔记整理助手。"
                "请基于用户当前筛选出来的摘录，输出结构化洞察。"
                "请严格返回 JSON，不要输出 markdown，不要补充额外解释。"
                "JSON 字段必须包括：core_conclusion, key_themes, review_questions, action_suggestions, reasoning。"
                "要求：1. 只基于提供的摘录；2. 每个列表最多 4 条；3. key_themes 应该简短明确。"
            ),
            messages=[{"role": "user", "content": format_qa_context(prompt, references)}],
            max_completion_tokens=900,
        )
        sections = parse_structured_insight(raw_response, structured_fallback)
        summary = sections["core_conclusion"]
    except LLMClientError:
        sections = structured_fallback
        summary = fallback

    return {"summary": summary, "references": references[:3], "sections": sections}
