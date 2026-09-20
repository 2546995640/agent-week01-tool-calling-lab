"""Run `python -m study_agent demo` or `python -m study_agent ask ...`."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from .demo import run_demo, run_session_demo
from .runner import AgentLoopLimit, run_agent
from .session import SessionStore, run_session_turn
from .toolbox import StudyStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Week 01 学习任务 Agent")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo", help="无需 API Key 的脚本化工具调用演示")
    commands.add_parser("demo-session", help="无需 API Key 的两轮会话演示")
    ask = commands.add_parser("ask", help="使用真实 OpenAI Responses API")
    ask.add_argument("question", help="例如：添加任务：阅读文档，45 分钟")
    ask.add_argument("--model", default=os.getenv("OPENAI_MODEL"))
    ask.add_argument("--data", type=Path, default=Path("data/tasks.json"))
    ask.add_argument("--trace", action="store_true", help="打印工具请求与结果")
    chat = commands.add_parser("chat", help="第 2 周：跨命令保持会话")
    chat.add_argument("question", help="当前轮的问题")
    chat.add_argument("--session", default="default", help="本地会话名称")
    chat.add_argument("--model", default=os.getenv("OPENAI_MODEL"))
    chat.add_argument("--data", type=Path, default=Path("data/tasks.json"))
    chat.add_argument("--sessions", type=Path, default=Path("data/sessions.json"))
    chat.add_argument("--reset", action="store_true", help="本轮前清除旧会话")
    chat.add_argument("--trace", action="store_true")
    args = parser.parse_args()

    if args.command == "demo":
        run_demo()
        return
    if args.command == "demo-session":
        run_session_demo()
        return

    if not os.getenv("OPENAI_API_KEY"):
        parser.error("请先设置 OPENAI_API_KEY；无需密钥可运行 demo")
    if not args.model:
        parser.error("请用 --model 或 OPENAI_MODEL 指定你账户可用的模型")

    from openai import OpenAI

    try:
        client = OpenAI(max_retries=2, timeout=30)
        if args.command == "chat":
            sessions = SessionStore(args.sessions)
            if args.reset:
                sessions.reset(args.session)
            result = run_session_turn(
                client, args.session, args.question, StudyStore(args.data), sessions, model=args.model
            )
        else:
            result = run_agent(client, args.question, StudyStore(args.data), model=args.model)
    except AgentLoopLimit as exc:
        parser.exit(2, f"工具调用停止：{exc}\n")
    if args.trace:
        for event in result.events:
            print(f"[tool] {event.name} {event.arguments} -> {event.output}")
    print(result.text)


if __name__ == "__main__":
    main()
