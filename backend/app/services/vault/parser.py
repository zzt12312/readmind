from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

SECTION_HIGHLIGHTS = "# 高亮划线"
SECTION_READING_NOTES = "# 读书笔记"
SECTION_BOOK_REVIEW = "# 本书评论"


def parse_markdown_book(file_path: Path, book_id: int) -> dict[str, Any]:
    raw_text = file_path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(raw_text)
    metadata = parse_frontmatter(frontmatter)
    sections = body.splitlines()

    title = str(metadata.get("title") or file_path.stem)
    author = str(metadata.get("author") or "")
    category = file_path.parent.name if file_path.parent != file_path else ""
    chapter = ""
    in_highlights = False
    note_id = 1
    notes: list[dict[str, Any]] = []
    reading_notes = extract_reading_notes(body)

    current_highlight_lines: list[str] = []
    current_timestamp = ""

    def flush_highlight() -> None:
        nonlocal note_id, current_highlight_lines, current_timestamp

        if not current_highlight_lines:
            return

        content = " ".join(part.strip() for part in current_highlight_lines if part.strip())
        cleaned = content.replace("📌", "").strip()
        if cleaned:
            notes.append(
                {
                    "id": book_id * 100000 + note_id,
                    "book_id": book_id,
                    "book_title": title,
                    "category": category,
                    "chapter": normalize_heading(chapter),
                    "excerpt": cleaned,
                    "comment": "",
                    "tags": build_tags(category, chapter, cleaned),
                    "semantic_vector": [],
                    "timestamp": current_timestamp,
                    "source_path": str(file_path),
                }
            )
            note_id += 1

        current_highlight_lines = []
        current_timestamp = ""

    for line in sections:
        stripped = line.strip()

        if stripped == SECTION_HIGHLIGHTS:
            in_highlights = True
            continue

        if stripped in {SECTION_READING_NOTES, SECTION_BOOK_REVIEW}:
            flush_highlight()
            in_highlights = False
            continue

        if not in_highlights:
            continue

        if stripped.startswith("## ") or stripped.startswith("### "):
            flush_highlight()
            chapter = stripped.lstrip("# ").strip()
            continue

        if stripped.startswith("> 📌"):
            flush_highlight()
            current_highlight_lines = [stripped.replace("> ", "", 1)]
            continue

        if current_highlight_lines and stripped.startswith("> ⏱"):
            current_timestamp = stripped.replace("> ⏱", "", 1).strip()
            flush_highlight()
            continue

        if current_highlight_lines:
            continuation = stripped
            if continuation.startswith("> "):
                continuation = continuation.replace("> ", "", 1)
            current_highlight_lines.append(continuation)

    flush_highlight()

    book = {
        "id": book_id,
        "title": title,
        "author": author,
        "notes": len(notes),
        "tags": derive_book_tags(category, notes),
        "category": category,
        "source_path": str(file_path),
        "reading_date": metadata.get("readingDate", ""),
        "last_read_date": metadata.get("lastReadDate", ""),
        "reading_time": metadata.get("readingTime", ""),
        "progress": metadata.get("progress", ""),
        "cover": metadata.get("cover", ""),
        "reading_notes": reading_notes,
    }

    return {"book": book, "notes": notes}


def split_frontmatter(raw_text: str) -> tuple[str, str]:
    if not raw_text.startswith("---\n"):
        return "", raw_text

    parts = raw_text.split("\n---\n", 1)
    if len(parts) != 2:
        return "", raw_text

    return parts[0].replace("---\n", "", 1), parts[1]


def parse_frontmatter(frontmatter: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def extract_reading_notes(body: str) -> str:
    if SECTION_READING_NOTES not in body:
        return ""

    after = body.split(SECTION_READING_NOTES, 1)[1]
    before_review = after.split(SECTION_BOOK_REVIEW, 1)[0]
    lines = [line.strip() for line in before_review.splitlines() if line.strip()]
    return "\n".join(lines[:8]).strip()


def normalize_heading(heading: str) -> str:
    heading = re.sub(r"^\d+(\.\d+)?\s*", "", heading)
    heading = re.sub(r"^第[一二三四五六七八九十百千0-9]+[章节部分卷篇]\s*", "", heading)
    return heading.strip()


def build_tags(category: str, chapter: str, content: str) -> list[str]:
    tags = [category] if category else []
    chapter_name = normalize_heading(chapter)
    if chapter_name:
        tags.append(chapter_name[:12])

    for keyword in ("长期主义", "系统", "决策", "情绪", "幸福", "习惯", "注意力", "财富", "学习", "行动"):
        if keyword in content and keyword not in tags:
            tags.append(keyword)

    return tags[:4]


def derive_book_tags(category: str, notes: list[dict[str, Any]]) -> list[str]:
    counter = Counter()
    for note in notes:
        for tag in note["tags"]:
            counter[tag] += 1

    ordered = [tag for tag, _ in counter.most_common(4)]
    if category:
        ordered = [tag for tag in ordered if tag != category]
        ordered.insert(0, category)
    return ordered[:4]
