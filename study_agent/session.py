"""Week 02: persist a continuation ID across separate CLI invocations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .runner import AgentResult, run_agent
from .toolbox import StudyStore


class SessionStore:
    """Small local checkpoint store; one CLI process should write at a time."""

    def __init__(self, path: Path):
        self.path = path

    def _read(self) -> dict[str, str]:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in data.items()
        ):
            raise ValueError("会话文件格式错误")
        return data

    def get(self, session_id: str) -> str | None:
        return self._read().get(session_id)

    def save(self, session_id: str, response_id: str) -> None:
        if not session_id or not response_id:
            raise ValueError("会话 ID 和响应 ID 不能为空")
        data = self._read()
        data[session_id] = response_id
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def reset(self, session_id: str) -> None:
        data = self._read()
        data.pop(session_id, None)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_session_turn(
    client: Any,
    session_id: str,
    user_text: str,
    tasks: StudyStore,
    sessions: SessionStore,
    *,
    model: str,
) -> AgentResult:
    """Checkpoint only after the model has returned a final answer.

    Do not retry this whole function after an uncertain failure: a tool may
    already have run. Retry only a failed API request after inspecting state.
    """
    if not session_id.strip():
        raise ValueError("session_id 不能为空")
    result = run_agent(
        client,
        user_text,
        tasks,
        model=model,
        previous_response_id=sessions.get(session_id),
    )
    sessions.save(session_id, result.response_id)
    return result
