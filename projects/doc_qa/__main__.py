"""Run document retrieval or optional grounded model answers."""

import argparse
import os
from pathlib import Path

from .answer import answer_question
from .retrieval import load_sections


def main() -> None:
    parser = argparse.ArgumentParser(description="Weeks 03–04 文档问答 Agent")
    parser.add_argument("question")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL"))
    parser.add_argument("--use-api", action="store_true", help="调用真实模型生成答案")
    parser.add_argument(
        "--docs", type=Path, default=Path(__file__).parent / "sample_docs", help="Markdown 知识库目录"
    )
    args = parser.parse_args()
    client = None
    if args.use_api:
        if not os.getenv("OPENAI_API_KEY") or not args.model:
            parser.error("--use-api 需要 OPENAI_API_KEY 和 OPENAI_MODEL 或 --model")
        from openai import OpenAI

        client = OpenAI()
    answer = answer_question(
        args.question, load_sections(args.docs), client=client, model=args.model
    )
    print(answer.text)
    print("\n候选来源：" + ("、".join(answer.citations) if answer.citations else "无"))


if __name__ == "__main__":
    main()
