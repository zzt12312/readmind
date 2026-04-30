from __future__ import annotations

from app.services.note_insight_service import export_note_insight_markdown


def test_export_note_insight_markdown_writes_sections_and_references(tmp_path) -> None:
    result = export_note_insight_markdown(
        export_root=tmp_path,
        title="长期主义洞察",
        scope={"tag": "长期主义", "q": "行动"},
        summary="长期主义需要落到可执行系统。",
        sections={
            "reasoning": "多条摘录都指向持续行动。",
            "key_themes": ["长期主义", "行动"],
            "review_questions": ["为什么行动系统重要？"],
            "action_suggestions": ["挑一条摘录写自己的解释。"],
        },
        references=[
            {
                "book": "测试书",
                "chapter": "第一章",
                "excerpt": "长期价值来自持续行动。",
            }
        ],
    )

    exported = tmp_path / "insights" / result["file_name"]

    assert exported.exists()
    assert result["relative_path"].startswith("exports/insights/")
    content = exported.read_text(encoding="utf-8")
    assert "# 长期主义洞察" in content
    assert "筛选范围：关键词：行动；标签：长期主义" in content
    assert "## 可执行建议" in content
    assert "长期价值来自持续行动。" in content
