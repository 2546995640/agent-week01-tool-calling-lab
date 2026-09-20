"""Offline, scripted Responses API simulation. No model or API key is used."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from typing import Any

from .runner import run_agent
from .session import SessionStore, run_session_turn
from .toolbox import StudyStore


class ScriptedResponses:
    def __init__(self, responses: list[Any]):
        self._responses = iter(responses)

    def create(self, **kwargs: Any) -> Any:
        return next(self._responses)


def call_response(response_id: str, name: str, arguments: dict[str, Any]) -> Any:
    call = SimpleNamespace(
        type="function_call",
        name=name,
        arguments=json.dumps(arguments, ensure_ascii=False),
        call_id=f"call_{response_id}",
    )
    return SimpleNamespace(id=response_id, output=[call], output_text="")


def text_response(response_id: str, text: str) -> Any:
    return SimpleNamespace(id=response_id, output=[], output_text=text)


def run_demo() -> None:
    """Show the same tool loop with deterministic, prewritten model responses."""
    with TemporaryDirectory() as directory:
        store = StudyStore(Path(directory) / "tasks.json")
        examples = [
            (
                "帮我添加学习任务：阅读工具调用文档，45 分钟",
                call_response("demo_1", "add_task", {"title": "阅读工具调用文档", "minutes": 45}),
                text_response("demo_2", "已添加任务 #1：阅读工具调用文档，预计 45 分钟。"),
            ),
            (
                "查看未完成任务",
                call_response("demo_3", "list_tasks", {"status": "todo"}),
                text_response("demo_4", "未完成任务：#1 阅读工具调用文档（45 分钟）。"),
            ),
            (
                "完成任务 1",
                call_response("demo_5", "complete_task", {"task_id": 1}),
                text_response("demo_6", "任务 #1 已完成。"),
            ),
        ]

        for prompt, first, second in examples:
            client = SimpleNamespace(responses=ScriptedResponses([first, second]))
            result = run_agent(client, prompt, store, model="offline-script")
            print(f"\n用户：{prompt}")
            for event in result.events:
                print(f"工具请求：{event.name}({event.arguments})")
                print(f"工具结果：{json.dumps(event.output, ensure_ascii=False)}")
            print(f"助手：{result.text}")
        print("\n离线演示已结束；任务数据保存在临时目录，不会上传。")


def run_session_demo() -> None:
    """Show how the second user turn resumes the first response."""
    class RecordingResponses(ScriptedResponses):
        def __init__(self, responses: list[Any]):
            super().__init__(responses)
            self.requests: list[dict[str, Any]] = []

        def create(self, **kwargs: Any) -> Any:
            self.requests.append(kwargs)
            return super().create(**kwargs)

    with TemporaryDirectory() as directory:
        root = Path(directory)
        responses = RecordingResponses(
            [text_response("turn_1", "第一轮：你好！"), text_response("turn_2", "第二轮：我们继续。")]
        )
        client = SimpleNamespace(responses=responses)
        sessions = SessionStore(root / "sessions.json")
        tasks = StudyStore(root / "tasks.json")
        first = run_session_turn(client, "learning", "你好", tasks, sessions, model="offline-script")
        second = run_session_turn(client, "learning", "接着说", tasks, sessions, model="offline-script")
        print("第一轮：" + first.text)
        print("本地保存的 response_id：" + first.response_id)
        print("第二轮发送的 previous_response_id：" + responses.requests[1]["previous_response_id"])
        print("第二轮：" + second.text)
