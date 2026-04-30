"""QA prompt, evidence, and streaming helpers.

`routes/qa.py` still handles the HTTP/SSE boundary, while this module owns the
pieces that can be tested without Flask: evidence summaries, LLM message
construction, and deterministic chunking for fallback streaming responses.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
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


def export_qa_session_markdown(
    *,
    export_root: str | Path,
    title: str,
    scope: str,
    book_title: str,
    messages: list[dict[str, Any]],
) -> dict[str, str]:
    qa_dir = Path(export_root).expanduser().resolve() / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    normalized_title = sanitize_export_title(title or first_user_question(messages) or "问答导出")
    filename = f"{now:%Y-%m-%d-%H%M%S}-{normalized_title}.md"
    target = unique_export_path(qa_dir / filename)
    markdown = render_qa_session_markdown(
        title=title or normalized_title,
        scope=scope,
        book_title=book_title,
        messages=messages,
        exported_at=now,
    )
    target.write_text(markdown, encoding="utf-8")

    return {
        "file_name": target.name,
        "relative_path": str(Path("exports") / "qa" / target.name),
        "absolute_path": str(target),
    }


def render_qa_session_markdown(
    *,
    title: str,
    scope: str,
    book_title: str,
    messages: list[dict[str, Any]],
    exported_at: datetime,
) -> str:
    lines = [
        f"# {title.strip() or '问答导出'}",
        "",
        f"- 导出时间：{exported_at:%Y-%m-%d %H:%M:%S}",
        f"- 检索范围：{format_scope(scope, book_title)}",
        f"- 消息数量：{len(messages)}",
        "",
        "## 对话",
        "",
    ]

    for index, message in enumerate(messages, start=1):
        role = "我" if message.get("role") == "user" else "签签"
        content = str(message.get("content") or "").strip()
        lines.extend([f"### {index}. {role}", "", content or "（空）", ""])
        references = message.get("references") or []
        if references:
            lines.extend(["#### 引用来源", ""])
            for ref_index, reference in enumerate(references, start=1):
                book = str(reference.get("book") or "未知书籍")
                chapter = str(reference.get("chapter") or "未知章节")
                excerpt = str(reference.get("excerpt") or "").strip()
                source_path = str(reference.get("source_path") or "").strip()
                lines.extend(
                    [
                        f"{ref_index}. **{book} · {chapter}**",
                        "",
                        f"   > {excerpt}",
                    ]
                )
                if source_path:
                    lines.extend(["", f"   来源：`{source_path}`"])
                lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def sanitize_export_title(title: str) -> str:
    normalized = re.sub(r"\s+", "-", title.strip())
    safe_chars = [char for char in normalized if char.isalnum() or char in {"-", "_"}]
    safe = "".join(safe_chars).strip("-_")
    return (safe or "qa-export")[:60]


def unique_export_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem}-{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError("Unable to allocate export file name")


def first_user_question(messages: list[dict[str, Any]]) -> str:
    for message in messages:
        if message.get("role") == "user" and str(message.get("content") or "").strip():
            return str(message["content"])
    return ""


def format_scope(scope: str, book_title: str) -> str:
    if scope == "current-book":
        return f"单本书：{book_title or '未指定书籍'}"
    return "全部书籍"
