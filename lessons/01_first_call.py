"""Lesson 1: make one model call. Requires OPENAI_API_KEY and OPENAI_MODEL."""

import os

from openai import OpenAI


model = os.getenv("OPENAI_MODEL")
if not model:
    raise SystemExit("请先设置 OPENAI_MODEL 为你账户可用的模型名")

response = OpenAI().responses.create(
    model=model,
    input="用一句中文解释什么是 Agent 的工具调用。",
)
print(response.output_text)
