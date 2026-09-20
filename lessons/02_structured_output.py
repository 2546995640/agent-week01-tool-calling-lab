"""Lesson 2: parse a model answer into a validated Python object."""

import os

from openai import OpenAI
from pydantic import BaseModel, Field


class StudyTask(BaseModel):
    title: str = Field(description="学习任务标题")
    minutes: int = Field(description="预计时长，单位：分钟")


model = os.getenv("OPENAI_MODEL")
if not model:
    raise SystemExit("请先设置 OPENAI_MODEL 为你账户可用的模型名")

response = OpenAI().responses.parse(
    model=model,
    input="从这句话提取学习任务：今晚用 45 分钟阅读工具调用文档。",
    text_format=StudyTask,
)
print(response.output_parsed)
