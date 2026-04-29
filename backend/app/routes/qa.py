import json

from flask import Blueprint, Response, current_app, jsonify, request, stream_with_context

from ..services.llm_client import LLMClientError, create_llm_client
from ..services.qa_service import (
    SYSTEM_PROMPT,
    build_evidence_summary,
    build_llm_messages,
    split_stream_chunks,
)
from ..services.vault_parser import answer_question, vault_repository

qa_bp = Blueprint("qa", __name__)


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
    fallback["evidence"] = build_evidence_summary(fallback["references"])
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
    evidence = build_evidence_summary(fallback["references"])

    def generate():
        retrieval_mode = fallback.get("retrieval_mode") or "hybrid"
        yield sse_event(
            "meta",
            {
                "question": fallback["question"],
                "references": fallback["references"],
                "retrieval_mode": retrieval_mode,
                "query_rewrite": fallback.get("query_rewrite"),
                "evidence": evidence,
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
                "evidence": evidence,
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
