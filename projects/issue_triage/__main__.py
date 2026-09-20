"""Run the issue triage workflow against fictional local fixtures."""

import argparse
import os
from pathlib import Path

from projects.doc_qa.retrieval import load_sections

from .triage import DraftOutbox, load_issue, triage


def main() -> None:
    root = Path(__file__).parent
    parser = argparse.ArgumentParser(description="Weeks 05–06 Issue 分诊")
    parser.add_argument("number", type=int, help="示例 Issue 编号，如 101")
    parser.add_argument("--use-api", action="store_true")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL"))
    parser.add_argument("--approve", action="store_true", help="人工批准模拟发布到本地 outbox")
    parser.add_argument("--out", type=Path, default=Path("data/issue_triage"))
    args = parser.parse_args()
    client = None
    if args.use_api:
        if not os.getenv("OPENAI_API_KEY") or not args.model:
            parser.error("--use-api 需要 OPENAI_API_KEY 和 OPENAI_MODEL 或 --model")
        from openai import OpenAI

        client = OpenAI()

    issue = load_issue(root / "issues.json", args.number)
    report = triage(issue, load_sections(root / "runbook"), client=client, model=args.model)
    outbox = DraftOutbox(args.out)
    draft_path = outbox.save_draft(report)
    print(f"Issue #{report.issue_number} | {report.category} | {report.priority} | {report.mode}")
    print("证据：" + ("、".join(report.evidence) if report.evidence else "无"))
    print("\n回复草稿：\n" + report.draft)
    print(f"\n草稿保存在：{draft_path}")
    if args.approve:
        print(f"人工批准后模拟发布到：{outbox.publish_simulated(args.number, approved=True)}")
    else:
        print("尚未批准发布；只生成了本地草稿。")


if __name__ == "__main__":
    main()
