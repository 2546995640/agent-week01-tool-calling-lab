"""A small, explicit Responses API tool loop for learning."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .toolbox import TOOL_SCHEMAS, StudyStore, ToolError, dispatch_tool


INSTRUCTIONS = (
    "你是学习任务助手。仅用提供的工具管理任务；不要声称执行了未调用的工具。"
    "新增任务若用户未给时长，可先询问时长或合理估计并说明。"
    "完成任务时必须知道任务编号；若不知道，先调用 list_tasks。"
    "工具返回错误时解释原因，不要假装成功。请用简洁中文回复。"
)


class AgentLoopLimit(RuntimeError):
    """The model requested too many consecutive tool rounds."""


@dataclass(frozen=True)
class ToolEvent:
    name: str
    arguments: str
    output: dict[str, Any]


@dataclass(frozen=True)
class AgentResult:
    text: str
    events: list[ToolEvent]
    response_id: str


def run_agent(
    client: Any,
    user_text: str,
    store: StudyStore,
    *,
    model: str,
    max_tool_rounds: int = 4,
    previous_response_id: str | None = None,
) -> AgentResult:
    """Ask a model, execute its requested tools, then return tool results to it.

    `client` is injected so tests can simulate Responses API calls without a key.
    """
    if not user_text.strip():
        raise ValueError("问题不能为空")
    if max_tool_rounds < 0:
        raise ValueError("max_tool_rounds 不能小于 0")

    events: list[ToolEvent] = []
    first_request: dict[str, Any] = {
        "model": model,
        "instructions": INSTRUCTIONS,
        "input": user_text,
        "tools": TOOL_SCHEMAS,
    }
    if previous_response_id:
        first_request["previous_response_id"] = previous_response_id
    response = client.responses.create(**first_request)

    for round_index in range(max_tool_rounds + 1):
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            final_text = response.output_text
            if not final_text:
                raise RuntimeError("模型没有给出文本回复，也没有请求工具")
            return AgentResult(text=final_text, events=events, response_id=response.id)
        if round_index == max_tool_rounds:
            raise AgentLoopLimit(f"已达到 {max_tool_rounds} 轮工具调用上限")

        tool_outputs = []
        for call in calls:
            try:
                output = dispatch_tool(store, call.name, call.arguments)
            except ToolError as exc:
                output = {"ok": False, "error": str(exc)}
            events.append(ToolEvent(call.name, call.arguments, output))
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(output, ensure_ascii=False),
                }
            )

        # Instructions must be sent again with previous_response_id.
        response = client.responses.create(
            model=model,
            instructions=INSTRUCTIONS,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=TOOL_SCHEMAS,
        )

    raise AssertionError("unreachable")
