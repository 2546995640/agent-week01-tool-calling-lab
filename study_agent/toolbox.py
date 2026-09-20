"""The real tools and their validation boundary.

The model may *request* a tool call. Only this module touches local task data.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


class ToolError(ValueError):
    """A rejected tool request that can be returned to the model."""


class StudyStore:
    def __init__(self, path: Path):
        self.path = path

    def _read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("任务文件格式错误：顶层必须是列表")
        return data

    def _write(self, tasks: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Replace atomically so a crash does not leave a half-written JSON file.
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=self.path.parent, suffix=".tmp", delete=False
        ) as stream:
            temp_path = Path(stream.name)
            json.dump(tasks, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        try:
            os.replace(temp_path, self.path)
        finally:
            temp_path.unlink(missing_ok=True)

    def add_task(self, title: str, minutes: int) -> dict[str, Any]:
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 120:
            raise ToolError("title 必须是 1 到 120 个字符")
        if isinstance(minutes, bool) or not isinstance(minutes, int) or not 5 <= minutes <= 480:
            raise ToolError("minutes 必须是 5 到 480 的整数")
        tasks = self._read()
        task = {
            "id": max((task["id"] for task in tasks), default=0) + 1,
            "title": title.strip(),
            "minutes": minutes,
            "done": False,
        }
        tasks.append(task)
        self._write(tasks)
        return task

    def list_tasks(self, status: str) -> list[dict[str, Any]]:
        if status not in {"all", "todo", "done"}:
            raise ToolError("status 只能是 all、todo 或 done")
        tasks = self._read()
        if status == "all":
            return tasks
        return [task for task in tasks if task["done"] is (status == "done")]

    def complete_task(self, task_id: int) -> dict[str, Any]:
        if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id < 1:
            raise ToolError("task_id 必须是正整数")
        tasks = self._read()
        for task in tasks:
            if task["id"] == task_id:
                task["done"] = True
                self._write(tasks)
                return task
        raise ToolError(f"找不到编号为 {task_id} 的任务")


TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "add_task",
        "description": "Add a study task with a title and estimated duration in minutes.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Study task title"},
                "minutes": {"type": "integer", "description": "Estimated minutes, 5 to 480"},
            },
            "required": ["title", "minutes"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "list_tasks",
        "description": "List study tasks by status.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["all", "todo", "done"]}
            },
            "required": ["status"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "complete_task",
        "description": "Mark one study task as done by its numeric id.",
        "parameters": {
            "type": "object",
            "properties": {"task_id": {"type": "integer", "description": "Task id"}},
            "required": ["task_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def dispatch_tool(store: StudyStore, name: str, raw_arguments: str) -> dict[str, Any]:
    """Validate model-provided JSON before calling a real Python function."""
    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        raise ToolError("工具参数不是合法 JSON") from exc
    if not isinstance(arguments, dict):
        raise ToolError("工具参数必须是 JSON 对象")

    expected = {
        "add_task": {"title", "minutes"},
        "list_tasks": {"status"},
        "complete_task": {"task_id"},
    }.get(name)
    if expected is None:
        raise ToolError(f"未授权的工具：{name}")
    if set(arguments) != expected:
        raise ToolError(f"{name} 的参数必须且只能包含：{', '.join(sorted(expected))}")

    if name == "add_task":
        return {"ok": True, "task": store.add_task(**arguments)}
    if name == "list_tasks":
        return {"ok": True, "tasks": store.list_tasks(**arguments)}
    return {"ok": True, "task": store.complete_task(**arguments)}

