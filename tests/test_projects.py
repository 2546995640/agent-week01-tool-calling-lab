from pathlib import Path

import pytest

from projects.doc_qa.answer import answer_question
from projects.doc_qa.retrieval import load_sections
from projects.issue_triage.triage import ApprovalRequired, DraftOutbox, load_issue, triage


def test_document_answer_has_real_source_and_abstains(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "guide.md").write_text(
        "# Guide\n\n## 重置密码\n忘记密码时点击重置密码。\n", encoding="utf-8"
    )
    sections = load_sections(folder)
    answer = answer_question("忘记密码怎么办？", sections)
    assert answer.citations == ["guide.md#重置密码"]
    assert answer_question("股票价格是多少？", sections).mode == "abstain"


def test_issue_publication_requires_approval(tmp_path):
    root = Path(__file__).parents[1] / "projects" / "issue_triage"
    report = triage(load_issue(root / "issues.json", 101), load_sections(root / "runbook"))
    outbox = DraftOutbox(tmp_path)
    outbox.save_draft(report)
    with pytest.raises(ApprovalRequired):
        outbox.publish_simulated(101, approved=False)
    assert not (tmp_path / "outbox" / "issue-101.md").exists()
    assert outbox.publish_simulated(101, approved=True).exists()
