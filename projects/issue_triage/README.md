# Weeks 05–06 · Issue 分诊与人工批准

示例 Issue 和运维手册全部是虚构数据。程序先读取 Issue、检索手册、产出分类与回复草稿，再由人决定是否模拟发布。**本项目不会向 GitHub 发送评论。**

```powershell
python -m projects.issue_triage 101
python -m projects.issue_triage 102 --approve
python -m projects.issue_triage.eval
```

默认草稿写入 `data/issue_triage/drafts/`；只有传入 `--approve` 才会复制到本地 `outbox/`。这个门槛说明发布动作应如何被隔离，不能用命令行参数代替真实产品中的身份与权限系统。

如果设置 `OPENAI_API_KEY` 和 `OPENAI_MODEL`，可加 `--use-api`，让模型生成结构化的分类和草稿；它仍只写本地草稿。离线模式使用显式规则作为可复现的基线，便于比较模型带来的收益和错误。

## 阅读顺序

1. `issues.json` 与 `runbook/`：输入数据和依据。
2. `triage.py`：检索、离线规则、模型结构化输出、批准边界。
3. `__main__.py`：命令行如何阻止未经批准的模拟发布。
4. `cases.json` 与 `eval.py`：小型标注集和基线评测。

## 后续练习

- 把分类错误的 Issue 加入评测集，比较规则与模型。
- 加入日志：记录 Issue 编号、检索来源、分类、人工决定与耗时，避免记录密码或令牌。
- 设计 GitHub 只读适配器读取公开 Issue；写入适配器应另行要求人工批准，并验证仓库、Issue 编号和草稿内容。
- 加入幂等键，防止网络重试导致同一条评论重复发布。

项目中的 `offline_baseline_accuracy` 只针对 3 条虚构样例，不代表真实 Issue 的效果。投递前请收集更大、合法使用的数据集并重新评估。

延伸阅读：[OpenAI Agent 的校验与人工批准](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)。
