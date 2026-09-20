"""Offline retrieval Hit@3 and no-evidence abstention checks."""

import json
from pathlib import Path

from .retrieval import load_sections, search


def evaluate() -> dict[str, float | int]:
    root = Path(__file__).parent
    cases = json.loads((root / "cases.json").read_text(encoding="utf-8"))
    sections = load_sections(root / "sample_docs")
    answerable = [case for case in cases if case["expected"]]
    unsupported = [case for case in cases if not case["expected"]]
    hit = sum(
        case["expected"] in [item.section.citation for item in search(case["question"], sections)]
        for case in answerable
    )
    abstained = sum(not search(case["question"], sections) for case in unsupported)
    return {
        "answerable_cases": len(answerable),
        "retrieval_hit_at_3": hit / len(answerable) if answerable else 0.0,
        "unsupported_cases": len(unsupported),
        "retrieval_abstention": abstained / len(unsupported) if unsupported else 0.0,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))
