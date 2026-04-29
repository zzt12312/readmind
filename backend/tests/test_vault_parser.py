from __future__ import annotations

from pathlib import Path

from app.services.vault.parser import (
    build_tags,
    derive_book_tags,
    extract_reading_notes,
    normalize_heading,
    parse_frontmatter,
    parse_markdown_book,
    split_frontmatter,
)


def test_split_frontmatter_and_parse_frontmatter() -> None:
    raw_text = "---\ntitle: 系统之美\nauthor: Donella Meadows\n---\n# 高亮划线\n"

    frontmatter, body = split_frontmatter(raw_text)

    assert parse_frontmatter(frontmatter) == {"title": "系统之美", "author": "Donella Meadows"}
    assert body == "# 高亮划线\n"


def test_parse_markdown_book_extracts_book_and_highlights(tmp_path: Path) -> None:
    category_dir = tmp_path / "系统思维"
    category_dir.mkdir()
    file_path = category_dir / "系统之美.md"
    file_path.write_text(
        """---
title: 系统之美
author: Donella Meadows
readingDate: 2026-04-01
lastReadDate: 2026-04-20
readingTime: 2小时30分钟
progress: 100%
cover: https://example.com/cover.jpg
---
# 高亮划线
## 第1章 系统
> 📌 系统不是元素的简单集合，而是连接关系形成的整体。
> ⏱ 2026-04-20 10:00

> 📌 长期主义需要关注反馈回路。
> 这是一条跨行摘录。
> ⏱ 2026-04-20 10:05

# 读书笔记
第一条读书笔记
第二条读书笔记
""",
        encoding="utf-8",
    )

    result = parse_markdown_book(file_path, book_id=7)

    assert result["book"]["id"] == 7
    assert result["book"]["title"] == "系统之美"
    assert result["book"]["category"] == "系统思维"
    assert result["book"]["notes"] == 2
    assert result["book"]["reading_time"] == "2小时30分钟"
    assert result["book"]["reading_notes"] == "第一条读书笔记\n第二条读书笔记"
    assert result["notes"][0]["id"] == 700001
    assert result["notes"][0]["chapter"] == "系统"
    assert result["notes"][0]["timestamp"] == "2026-04-20 10:00"
    assert "系统" in result["notes"][0]["tags"]
    assert "长期主义需要关注反馈回路。 这是一条跨行摘录。" == result["notes"][1]["excerpt"]


def test_tag_helpers_normalize_chapters_and_prioritize_category() -> None:
    assert normalize_heading("第1章 系统") == "系统"
    assert build_tags("商业", "第2章 长期主义", "财富和长期主义") == ["商业", "长期主义", "财富"]

    tags = derive_book_tags(
        "商业",
        [
            {"tags": ["长期主义", "商业"]},
            {"tags": ["长期主义", "财富"]},
        ],
    )

    assert tags[0] == "商业"
    assert "长期主义" in tags


def test_extract_reading_notes_stops_before_book_review() -> None:
    body = "# 读书笔记\nA\n\nB\n# 本书评论\n不应该出现"

    assert extract_reading_notes(body) == "A\nB"
