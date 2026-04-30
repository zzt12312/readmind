from __future__ import annotations

from app.services.qa_service import export_qa_session_markdown


def test_export_qa_session_markdown_writes_file(tmp_path) -> None:
    result = export_qa_session_markdown(
        export_root=tmp_path,
        title="长期主义里的复利",
        scope="current-book",
        book_title="长期主义",
        messages=[
            {
                "role": "user",
                "content": "这本书最值得回看的观点是什么？",
            },
            {
                "role": "assistant",
                "content": "最值得回看的是把时间投入可积累的事情。",
                "references": [
                    {
                        "book": "长期主义",
                        "chapter": "第一章",
                        "excerpt": "真正的复利来自持续投入。",
                        "source_path": "/vault/长期主义.md",
                    }
                ],
            },
        ],
    )

    exported = tmp_path / "qa" / result["file_name"]

    assert exported.exists()
    assert result["relative_path"].startswith("exports/qa/")
    content = exported.read_text(encoding="utf-8")
    assert "# 长期主义里的复利" in content
    assert "检索范围：单本书：长期主义" in content
    assert "## 对话" in content
    assert "真正的复利来自持续投入。" in content
