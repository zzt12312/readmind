import json

from flask import Blueprint, Response, current_app, jsonify, request, stream_with_context

from ..services.minimax_client import LLMClientError, create_llm_client
from ..services.vault_parser import answer_question, vault_repository
from ..services.vault_parser import format_qa_context

qa_bp = Blueprint("qa", __name__)


SYSTEM_PROMPT = (
    "你是一个基于个人读书笔记回答问题的中文助手。"
    "只能依据提供的摘录作答，不要凭空补充书外事实。"
    "回答要求：1. 先直接回答问题；2. 再用 2 到 4 点归纳关键结论；"
    "3. 如果证据不足，要明确说明；4. 不要输出<think>；"
    "5. 若当前检索范围限定为单本书，不要引用其他书。"
)


def build_llm_messages(history: list[dict], question: str, references: list[dict]) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for item in history[-8:]:
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    # 最后一条 user message 会附带当前问题和检索到的引用，确保模型回答严格围绕笔记上下文展开。
    messages.append({"role": "user", "content": format_qa_context(question, references)})
    return messages


def sse_event(event: str, payload: dict) -> str:
    # 前端流式问答依赖标准 SSE 格式解析 meta / delta / done 三类事件。
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@qa_bp.post("/ask")
def ask():
    payload = request.get_json(silent=True) or {}
    question = payload.get("question", "")
    scope = payload.get("scope", "all-books")
    book_id = payload.get("book_id")
    history = payload.get("history", [])
    data = vault_repository.load()
    fallback = answer_question(data, question, scope=scope, book_id=book_id)
    fallback["generation_mode"] = "fallback"
    fallback["retrieval_mode"] = fallback.get("retrieval_mode") or "hybrid"
    fallback["fallback_reason"] = ""

    if not question.strip():
        return jsonify(fallback)

    try:
        client = create_llm_client(current_app.config)
        llm_answer = client.chat(
            system_prompt=SYSTEM_PROMPT,
            messages=build_llm_messages(history, question, fallback["references"]),
            max_completion_tokens=900,
        )
        fallback["answer"] = llm_answer
        fallback["generation_mode"] = "llm"
    except LLMClientError as error:
        fallback["fallback_reason"] = str(error)

    return jsonify(fallback)


@qa_bp.post("/stream")
def ask_stream():
    payload = request.get_json(silent=True) or {}
    question = payload.get("question", "")
    scope = payload.get("scope", "all-books")
    book_id = payload.get("book_id")
    history = payload.get("history", [])
    data = vault_repository.load()
    fallback = answer_question(data, question, scope=scope, book_id=book_id)

    def generate():
        retrieval_mode = fallback.get("retrieval_mode") or "hybrid"
        yield sse_event(
            "meta",
            {
                "question": fallback["question"],
                "references": fallback["references"],
                "retrieval_mode": retrieval_mode,
                "query_rewrite": fallback.get("query_rewrite"),
            },
        )
        yield sse_event(
            "status",
            {
                "phase": "retrieving",
                "label": "已完成笔记检索",
                "detail": f"当前共命中 {len(fallback['references'])} 条引用，正在准备回答。",
            },
        )

        if not question.strip():
            yield sse_event(
                "done",
                {
                    **fallback,
                    "generation_mode": "fallback",
                    "retrieval_mode": retrieval_mode,
                    "fallback_reason": "",
                },
            )
            return

        answer_parts: list[str] = []
        generation_mode = "llm"
        fallback_reason = ""
        try:
            client = create_llm_client(current_app.config)
            yield sse_event(
                "status",
                {
                    "phase": "generating",
                    "label": "正在生成回答",
                    "detail": "模型正在结合当前引用整理答案。",
                },
            )
            for chunk in client.stream_chat(
                system_prompt=SYSTEM_PROMPT,
                messages=build_llm_messages(history, question, fallback["references"]),
                max_completion_tokens=900,
            ):
                if not chunk:
                    continue
                answer_parts.append(chunk)
                yield sse_event("delta", {"content": chunk})
        except LLMClientError as error:
            generation_mode = "fallback"
            fallback_reason = str(error)
            yield sse_event(
                "status",
                {
                    "phase": "fallback",
                    "label": "已切换到本地回退回答",
                    "detail": "模型暂时不可用，本轮答案将基于检索结果直接生成。",
                },
            )
            for chunk in split_stream_chunks(fallback["answer"]):
                answer_parts.append(chunk)
                yield sse_event("delta", {"content": chunk})

        answer = "".join(answer_parts).strip() or fallback["answer"]
        yield sse_event(
            "done",
            {
                "question": fallback["question"],
                "answer": answer,
                "references": fallback["references"],
                "generation_mode": generation_mode,
                "retrieval_mode": retrieval_mode,
                "fallback_reason": fallback_reason,
                "query_rewrite": fallback.get("query_rewrite"),
            },
        )

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def split_stream_chunks(text: str, step: int = 24) -> list[str]:
    return [text[index : index + step] for index in range(0, len(text), step)] or [text]
