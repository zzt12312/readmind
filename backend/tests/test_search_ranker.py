from __future__ import annotations

from app.services.search.ranker import (
    build_query_ngrams,
    build_query_rewrite_summary,
    compute_note_match,
    dedupe_text_list,
    extract_query_keywords,
)


def test_extract_query_keywords_filters_stopwords() -> None:
    assert extract_query_keywords("帮我总结长期主义和attention") == ["长期主义", "attention"]


def test_build_query_ngrams_handles_chinese_and_empty_text() -> None:
    assert build_query_ngrams("") == set()
    assert build_query_ngrams("系统") == {"系统"}
    assert build_query_ngrams("系统思维") == {"系统", "统思", "思维"}


def test_compute_note_match_rewards_book_chapter_tags_and_excerpt_hits() -> None:
    note = {
        "book_title": "长期主义",
        "chapter": "复利与行动",
        "excerpt": "长期主义不是口号，而是系统行动。",
        "comment": "",
        "tags": ["长期主义", "行动"],
    }

    match = compute_note_match(
        note,
        lowered_query="长期主义",
        keywords=["长期主义", "行动"],
        query_ngrams=build_query_ngrams("长期主义"),
    )

    assert match["exact_score"] > 0
    assert match["keyword_hits"] == 2
    assert match["field_hits"] >= 2
    assert match["lexical_score"] > match["fuzzy_score"]


def test_build_query_rewrite_summary_only_returns_applied_rules() -> None:
    assert build_query_rewrite_summary(None) is None
    assert build_query_rewrite_summary({"applied_rules": []}) is None

    summary = build_query_rewrite_summary(
        {
            "original": "长期主义",
            "applied_rules": ["长期主义"],
            "expansion_terms": ["复利"],
            "variants": [{"text": "长期主义"}, {"text": "复利"}],
        }
    )

    assert summary == {
        "original": "长期主义",
        "applied_rules": ["长期主义"],
        "expansion_terms": ["复利"],
        "variants": ["长期主义", "复利"],
    }


def test_dedupe_text_list_strips_empty_and_duplicate_values() -> None:
    assert dedupe_text_list(["长期主义", "", " 长期主义 ", "复利"]) == ["长期主义", "复利"]

