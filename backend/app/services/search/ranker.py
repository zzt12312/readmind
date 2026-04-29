"""Hybrid note retrieval for QA and note workbench search.

The ranker combines three signals:
- lexical keyword hits across title/chapter/excerpt/comment/tags;
- fuzzy ngram overlap for short Chinese queries;
- semantic similarity from an embedding vector when available.

Query rewrite expands abstract reading concepts such as "长期主义" into nearby
aliases/concepts. This improves recall, but every expanded variant has a lower
weight so the original query still dominates ranking.
"""

from __future__ import annotations

import re
from typing import Any

from ..embedding_service import EmbeddingService

STOPWORDS = {
    "什么",
    "哪些",
    "内容",
    "这本书",
    "这本",
    "其中",
    "关于",
    "一下",
    "总结",
    "帮我",
    "记录",
    "提到",
    "说了",
    "只看",
    "只检索",
    "笔记",
    "我的",
    "和",
    "与",
    "的",
}

QUERY_REWRITE_RULES = {
    "长期主义": {
        "triggers": ["长期主义", "长期", "长远", "复利", "延迟满足"],
        "aliases": ["长期收益", "长期积累", "长期幸福"],
        "concepts": ["复利", "未来收益", "长期积累", "长远决策", "延迟满足", "推迟满足"],
    },
    "行动系统": {
        "triggers": ["行动系统", "执行系统", "执行力", "行动力", "自我控制"],
        "aliases": ["执行系统", "自我控制系统", "行动机制", "执行机制"],
        "concepts": ["执行", "行动", "自控", "习惯", "注意力", "执行力", "自我控制"],
    },
    "情绪稳定": {
        "triggers": ["情绪稳定", "情绪管理", "情绪调节", "情绪控制", "稳定情绪"],
        "aliases": ["情绪管理", "情绪调节", "自我调节", "稳定情绪"],
        "concepts": ["控制冲动", "平复情绪", "情绪恢复", "自我安抚", "保持冷静"],
    },
    "注意力管理": {
        "triggers": ["注意力管理", "专注力", "注意力", "专注", "分心"],
        "aliases": ["专注力管理", "注意力控制"],
        "concepts": ["专注", "分心", "努力", "控制", "心流", "注意力"],
    },
    "财富": {
        "triggers": ["财富", "财务自由", "赚钱", "资产", "复利"],
        "aliases": ["财务自由", "资产积累", "长期收益"],
        "concepts": ["资产", "杠杆", "复利", "现金流", "资本", "长期收益"],
    },
    "决策": {
        "triggers": ["决策", "判断", "选择", "思考", "权衡"],
        "aliases": ["判断力", "做选择", "决断"],
        "concepts": ["权衡", "偏差", "启发式", "风险", "概率", "选择"],
    },
}

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)


def extract_query_keywords(query: str) -> list[str]:
    keywords: list[str] = []
    for token in re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z]{3,}", query):
        normalized = token.lower()
        for stopword in STOPWORDS:
            normalized = normalized.replace(stopword, "")
        if normalized:
            keywords.append(normalized)
    return keywords


def dedupe_text_list(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        value = (item or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def rewrite_query(query: str) -> dict[str, Any]:
    normalized = re.sub(r"\s+", "", query)
    variants: list[dict[str, Any]] = [{"text": query.strip(), "weight": 1.0, "kind": "original"}]
    applied_rules: list[str] = []
    expansion_terms: list[str] = []

    # Query rewrite only expands abstract concepts so short searches do not drift too far.
    for anchor, config in QUERY_REWRITE_RULES.items():
        trigger_terms = [anchor, *config.get("triggers", []), *config.get("aliases", [])]
        if not any(term and term in normalized for term in trigger_terms):
            continue

        applied_rules.append(anchor)
        for alias in [anchor, *config.get("aliases", [])]:
            if alias and alias not in normalized:
                variants.append({"text": alias, "weight": 0.9, "kind": "alias"})
        for concept in config.get("concepts", []):
            if concept and concept not in normalized:
                variants.append({"text": concept, "weight": 0.72, "kind": "concept"})
                expansion_terms.append(concept)

    deduped_variants: list[dict[str, Any]] = []
    seen_variant_texts: set[str] = set()
    for item in variants:
        text = (item.get("text") or "").strip()
        if not text or text in seen_variant_texts:
            continue
        seen_variant_texts.add(text)
        deduped_variants.append(
            {
                **item,
                "keywords": extract_query_keywords(text),
                "ngrams": build_query_ngrams(text),
                "vector": vectorize_text(text),
            }
        )

    return {
        "original": query.strip(),
        "applied_rules": dedupe_text_list(applied_rules),
        "expansion_terms": dedupe_text_list(expansion_terms),
        "variants": deduped_variants,
    }


def build_query_rewrite_summary(rewrite_info: dict[str, Any] | None) -> dict[str, Any] | None:
    if not rewrite_info or not rewrite_info.get("applied_rules"):
        return None
    return {
        "original": rewrite_info.get("original", ""),
        "applied_rules": rewrite_info.get("applied_rules", []),
        "expansion_terms": rewrite_info.get("expansion_terms", []),
        "variants": [item.get("text", "") for item in rewrite_info.get("variants", [])[:8]],
    }


def build_query_ngrams(query: str) -> set[str]:
    compact = re.sub(r"\s+", "", query.lower())
    if len(compact) < 2:
        return {compact} if compact else set()
    return {compact[index : index + 2] for index in range(len(compact) - 1)}


def build_semantic_text(note: dict[str, Any]) -> str:
    return " ".join(
        [
            note.get("book_title") or "",
            note.get("chapter") or "",
            note.get("excerpt") or "",
            note.get("comment") or "",
            " ".join(note.get("tags", [])),
        ]
    )


def vectorize_text(text: str) -> list[float]:
    return embedding_service.embed_text(text)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(left[index] * right[index] for index in range(len(left)))


def compute_note_match(
    note: dict[str, Any],
    lowered_query: str,
    keywords: list[str],
    query_ngrams: set[str],
) -> dict[str, float]:
    excerpt = (note.get("excerpt") or "").lower()
    comment = (note.get("comment") or "").lower()
    chapter = (note.get("chapter") or "").lower()
    book_title = (note.get("book_title") or "").lower()
    tags = [tag.lower() for tag in note.get("tags", [])]
    haystack = " ".join([book_title, chapter, excerpt, comment, " ".join(tags)])

    exact_score = 0
    keyword_hits = 0
    field_hits = 0
    for keyword in keywords:
        hit_count = haystack.count(keyword)
        exact_score += hit_count * 14
        if hit_count > 0:
            keyword_hits += 1
        if keyword in book_title:
            exact_score += 8
            field_hits += 1
        if keyword in chapter:
            exact_score += 6
            field_hits += 1
        if any(keyword in tag for tag in tags):
            exact_score += 5
            field_hits += 1
        if keyword in excerpt:
            field_hits += 0.8
        if keyword in comment:
            field_hits += 0.6

    if lowered_query and lowered_query in haystack:
        exact_score += 10

    note_ngrams = build_query_ngrams("".join([book_title, chapter, excerpt[:240], comment[:120]]))
    fuzzy_score = len(query_ngrams & note_ngrams)

    total_score = exact_score + fuzzy_score + min(len(excerpt) / 80, 4)
    return {
        "exact_score": float(exact_score),
        "fuzzy_score": float(fuzzy_score),
        "lexical_score": float(total_score),
        "keyword_hits": float(keyword_hits),
        "field_hits": float(field_hits),
    }


def compute_note_relevance(
    note: dict[str, Any],
    lowered_query: str,
    keywords: list[str],
    query_ngrams: set[str],
) -> float:
    return compute_note_match(note, lowered_query, keywords, query_ngrams)["lexical_score"]


def compute_semantic_similarity(note: dict[str, Any], query_vector: list[float]) -> float:
    note_vector = note.get("semantic_vector") or []
    return cosine_similarity(query_vector, note_vector)


def rank_notes_for_query(
    notes: list[dict[str, Any]],
    query: str,
    rewrite_info: dict[str, Any] | None = None,
) -> list[tuple[dict[str, Any], float]]:
    """Return notes ranked by explicit textual evidence plus semantic support.

    A note must have at least one support signal before it is included. The
    final rerank score favors direct keyword/field hits over pure semantic
    matches, because QA answers should be easy to trace back to real excerpts.
    """
    rewrite = rewrite_info or rewrite_query(query)

    scored_notes: list[tuple[dict[str, Any], float]] = []
    for note in notes:
        best_score = 0.0
        support_hits = 0
        best_semantic_score = 0.0
        best_exact_score = 0.0
        keyword_coverage = 0.0
        field_coverage = 0.0
        semantic_only_support = 0

        for variant in rewrite["variants"]:
            text = variant["text"]
            lowered = text.lower()
            keywords = variant["keywords"]
            query_ngrams = variant["ngrams"]
            query_vector = variant["vector"]
            weight = float(variant["weight"])
            kind = str(variant["kind"])
            fuzzy_threshold = max(2, min(4, (len(query_ngrams) // 2) + 1)) if query_ngrams else 0

            match = compute_note_match(note, lowered, keywords, query_ngrams)
            exact_score = match["exact_score"]
            fuzzy_score = match["fuzzy_score"]
            lexical_score = match["lexical_score"]
            semantic_score = compute_semantic_similarity(note, query_vector)
            semantic_threshold = 0.64 if kind == "original" else 0.68
            hybrid_threshold = 0.46 if kind != "concept" else 0.5
            weighted_score = (lexical_score * weight) + (semantic_score * 28 * weight)

            if (
                exact_score > 0
                or fuzzy_score >= fuzzy_threshold
                or (semantic_score >= hybrid_threshold and fuzzy_score >= 1)
                or semantic_score >= semantic_threshold
            ):
                support_hits += 1
                best_score = max(best_score, weighted_score)
                best_semantic_score = max(best_semantic_score, semantic_score)
                best_exact_score = max(best_exact_score, exact_score)
                keyword_coverage = max(keyword_coverage, match["keyword_hits"])
                field_coverage = max(field_coverage, match["field_hits"])
                if exact_score == 0 and fuzzy_score == 0 and semantic_score >= semantic_threshold:
                    semantic_only_support += 1

        if support_hits:
            # Rerank by explicit evidence and field coverage, not semantic score alone.
            rerank_score = (
                best_score
                + min(support_hits - 1, 3) * 1.4
                + min(keyword_coverage, 4) * 1.8
                + min(field_coverage, 5) * 0.9
                + min(best_exact_score / 18, 4)
                + (best_semantic_score * 6.5)
                - (semantic_only_support * 0.9)
            )
            scored_notes.append((note, rerank_score))

    scored_notes.sort(key=lambda item: (item[1], len(item[0].get("excerpt") or "")), reverse=True)
    if not scored_notes:
        return []

    top_score = scored_notes[0][1]
    floor_score = max(top_score * 0.72, 11.2)
    trimmed_notes = [item for item in scored_notes if item[1] >= floor_score]

    seen_excerpt_signatures: set[str] = set()
    deduped_notes: list[tuple[dict[str, Any], float]] = []
    for note, score in trimmed_notes:
        signature = re.sub(r"\s+", "", (note.get("excerpt") or ""))[:96]
        if signature and signature in seen_excerpt_signatures:
            continue
        if signature:
            seen_excerpt_signatures.add(signature)
        deduped_notes.append((note, score))
    return deduped_notes[:80]
