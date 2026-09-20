import json

import pytest

from study_agent.toolbox import StudyStore, ToolError, dispatch_tool


def test_tasks_are_persisted_and_filtered(tmp_path):
    path = tmp_path / "tasks.json"
    store = StudyStore(path)
    first = store.add_task("阅读文档", 45)
    second = store.add_task("写练习", 30)
    assert (first["id"], second["id"]) == (1, 2)
    store.complete_task(1)

    reopened = StudyStore(path)
    assert [task["id"] for task in reopened.list_tasks("done")] == [1]
    assert [task["id"] for task in reopened.list_tasks("todo")] == [2]
    assert json.loads(path.read_text(encoding="utf-8"))[0]["done"] is True


@pytest.mark.parametrize(
    ("name", "raw"),
    [
        ("add_task", '{"title":"X","minutes":true}'),
        ("add_task", '{"title":"X","minutes":1}'),
        ("complete_task", '{"task_id":-1}'),
        ("list_tasks", '{"status":"secret"}'),
        ("delete_everything", "{}"),
        ("add_task", '{"title":"X","minutes":30,"extra":1}'),
        ("add_task", "not json"),
    ],
)
def test_untrusted_tool_arguments_are_rejected(tmp_path, name, raw):
    store = StudyStore(tmp_path / "tasks.json")
    with pytest.raises(ToolError):
        dispatch_tool(store, name, raw)
    assert store.list_tasks("all") == []
