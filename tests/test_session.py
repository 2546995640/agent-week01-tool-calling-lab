from types import SimpleNamespace

from study_agent.demo import ScriptedResponses, text_response
from study_agent.session import SessionStore, run_session_turn
from study_agent.toolbox import StudyStore


class RecordingResponses(ScriptedResponses):
    def __init__(self, responses):
        super().__init__(responses)
        self.requests = []

    def create(self, **kwargs):
        self.requests.append(kwargs)
        return super().create(**kwargs)


def test_session_continues_across_turns_and_can_reset(tmp_path):
    responses = RecordingResponses([text_response("r1", "第一轮"), text_response("r2", "第二轮")])
    client = SimpleNamespace(responses=responses)
    sessions = SessionStore(tmp_path / "sessions.json")
    tasks = StudyStore(tmp_path / "tasks.json")
    run_session_turn(client, "study", "你好", tasks, sessions, model="test")
    run_session_turn(client, "study", "接着说", tasks, sessions, model="test")
    assert responses.requests[1]["previous_response_id"] == "r1"
    assert sessions.get("study") == "r2"
    sessions.reset("study")
    assert sessions.get("study") is None
