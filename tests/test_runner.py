import json
from types import SimpleNamespace

import pytest

from study_agent.demo import ScriptedResponses, call_response, text_response
from study_agent.runner import AgentLoopLimit, INSTRUCTIONS, run_agent
from study_agent.toolbox import StudyStore


class RecordingResponses(ScriptedResponses):
    def __init__(self, responses):
        super().__init__(responses)
        self.requests = []

    def create(self, **kwargs):
        self.requests.append(kwargs)
        return super().create(**kwargs)


def test_tool_call_result_is_returned_to_model(tmp_path):
    responses = RecordingResponses(
        [
            call_response("r1", "add_task", {"title": "读文档", "minutes": 45}),
            text_response("r2", "已添加。"),
        ]
    )
    result = run_agent(
        SimpleNamespace(responses=responses),
        "添加学习任务",
        StudyStore(tmp_path / "tasks.json"),
        model="test-model",
    )
    assert result.text == "已添加。"
    assert result.events[0].output["task"]["title"] == "读文档"
    assert responses.requests[1]["previous_response_id"] == "r1"
    assert responses.requests[1]["instructions"] == INSTRUCTIONS
    tool_output = responses.requests[1]["input"][0]
    assert tool_output["call_id"] == "call_r1"
    assert json.loads(tool_output["output"])["ok"] is True


def test_invalid_tool_call_returns_error_to_model(tmp_path):
    responses = RecordingResponses(
        [
            call_response("r1", "complete_task", {"task_id": 999}),
            text_response("r2", "找不到该任务。"),
        ]
    )
    result = run_agent(
        SimpleNamespace(responses=responses),
        "完成任务 999",
        StudyStore(tmp_path / "tasks.json"),
        model="test-model",
    )
    assert result.events[0].output["ok"] is False
    assert json.loads(responses.requests[1]["input"][0]["output"])["ok"] is False


def test_loop_limit_prevents_extra_tool_execution(tmp_path):
    store = StudyStore(tmp_path / "tasks.json")
    responses = RecordingResponses(
        [call_response("r1", "add_task", {"title": "不应添加", "minutes": 30})]
    )
    with pytest.raises(AgentLoopLimit):
        run_agent(
            SimpleNamespace(responses=responses),
            "重复调用",
            store,
            model="test-model",
            max_tool_rounds=0,
        )
    assert store.list_tasks("all") == []
