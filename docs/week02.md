# Week 02 · 会话状态与错误恢复（20 小时）

这一周在 Week 01 的学习任务 Agent 上继续开发。重点是**两次独立运行如何保持上下文**，以及失败后怎样避免重复执行有副作用的工具。

## 无需 API Key 的入口

```powershell
python -m study_agent demo-session
python -m pytest tests/test_session.py -q
```

阅读顺序：`study_agent/session.py` → `study_agent/runner.py` → `study_agent/__main__.py`。离线演示会显示第二轮请求中的 `previous_response_id`。这只是脚本化响应，尚不验证真实模型的记忆质量。

## 本周安排

| 阶段 | 时间 | 任务 |
| --- | ---: | --- |
| 理解状态 | 4h | 画出用户轮次、工具轮次、`response_id` 三者关系 |
| 阅读代码 | 4h | 理解会话文件何时保存、何时清除，以及指令为何每轮重新发送 |
| 错误恢复 | 4h | 模拟 API 超时、工具报错、达到循环上限；写下哪些请求可安全重试 |
| 动手改造 | 5h | 为会话文件加原子写入；为任务添加请求 ID 并防止重复新增 |
| 复盘 | 3h | 更新测试，录制两轮对话的讲解视频或写一页技术笔记 |

## 关键练习

`OpenAI(max_retries=2)` 只让 SDK 重试失败的 API 请求。**不要在不确定工具是否已执行时重试整个 Agent 轮次**：一次 `add_task` 可能被执行两次。你可以为写操作增加幂等键，并在测试中模拟“工具已成功、模型回复前断线”。

真实模式示例：

```powershell
python -m study_agent chat "添加任务：读文档 45 分钟" --session week02 --trace
python -m study_agent chat "我刚才添加了什么？" --session week02 --trace
python -m study_agent chat "重新开始" --session week02 --reset
```

API 的服务端续接状态可能失效；`--reset` 用于开始新会话。密钥和模型名设置方法见根目录 README。

**完成标准：**你能解释为什么只在最终回复成功后保存新的会话 ID，并能写出防重复提交的测试。

延伸阅读：[OpenAI Agents SDK 快速开始](https://developers.openai.com/api/docs/guides/agents/quickstart)。先比较自己的循环，再决定是否引入框架。
