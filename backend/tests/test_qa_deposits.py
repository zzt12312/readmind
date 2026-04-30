from __future__ import annotations

from app.services.qa_deposit_repository import QaDepositRepository


def test_qa_deposit_repository_persists_insight_card(tmp_path) -> None:
    repository = QaDepositRepository(tmp_path / "readmind.db")

    item = repository.create_deposit(
        {
            "deposit_type": "insight_card",
            "title": "洞察：长期主义",
            "question": "长期主义最重要的观点是什么？",
            "content": "把时间投入可积累的事情。",
            "references": [{"book_id": 1, "note_id": 11, "excerpt": "复利来自持续投入。"}],
            "scope": "current-book",
            "book_id": 1,
        }
    )

    assert item["id"].startswith("deposit_")
    assert item["deposit_type"] == "insight_card"
    assert item["note_ids"] == [11]

    items = repository.list_deposits("insight_card")
    assert len(items) == 1
    assert items[0]["title"] == "洞察：长期主义"
