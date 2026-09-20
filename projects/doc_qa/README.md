# Weeks 03–04 · 带来源的文档问答

这是一个刻意保持透明的检索增强生成（RAG）样例。示例知识库是本仓库编写的虚构学习平台手册。离线模式只返回相关段落，**不会伪装成模型生成的答案**；有 API Key 时可以把检索内容交给模型生成带引用的回复。

```powershell
python -m projects.doc_qa "忘记密码怎么重置？"
python -m projects.doc_qa "明天上海天气如何？"
python -m projects.doc_qa.eval
```

真实模型模式需要 `OPENAI_API_KEY` 与 `OPENAI_MODEL`：

```powershell
python -m projects.doc_qa "任务可以导出成什么格式？" --use-api
```

## 数据流

`sample_docs/*.md` → 按二级标题切成 Section → 中英文字词切分 → BM25 风格排序 → 选前 3 段 → 离线展示或调用模型 → 返回来源编号。

重点读 `retrieval.py` 的 `load_sections` 和 `search`，再读 `answer.py`。`cases.json` 是人工标注的小型问题集；`eval.py` 只测 **检索 Hit@3** 和**无依据问题的拒答**，不代表模型回答准确率。样例数据很小，分数只用于检查流程，不能写进简历当作真实业务效果。

## 自己动手

1. 加入你有权使用的真实文档，并记录来源、更新时间和可见范围。
2. 比较按标题切分与固定字数切分的检索结果。
3. 扩充到至少 30 条问题，其中包括找不到答案、含糊提问和多文档问题。
4. 人工检查回答是否真正被引用段落支持；记录失败类型。
5. 再尝试向量检索或混合检索，保留当前离线版本作为对照。

此项目尚未实现用户权限过滤、文档更新同步或生产级检索。把这些列为后续改进项，比在展示时暗示已有这些能力更可信。

延伸阅读：[OpenAI 检索指南](https://developers.openai.com/api/docs/guides/retrieval)。
