"""Offline baseline classification agreement with a small labelled fixture."""

import json
from pathlib import Path

from projects.doc_qa.retrieval import load_sections

from .triage import load_issue, triage


def evaluate() -> dict[str, float | int]:
    root = Path(__file__).parent
    cases = json.loads((root / "cases.json").read_text(encoding="utf-8"))
    runbook = load_sections(root / "runbook")
    correct = 0
    for case in cases:
        report = triage(load_issue(root / "issues.json", case["number"]), runbook)
        correct += report.category == case["category"] and report.priority == case["priority"]
    return {"cases": len(cases), "offline_baseline_accuracy": correct / len(cases)}


if __name__ == "__main__":
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))
