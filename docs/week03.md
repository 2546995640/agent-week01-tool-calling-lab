# Week 03 · 检索基础（20 小时）

本周目标：理解“找到正确资料”和“生成正确答案”是两个不同的问题。

| 时间 | 学习与动手 |
| ---: | --- |
| 4h | 阅读 [`projects/doc_qa/README.md`](../projects/doc_qa/README.md) 和检索代码，画出数据流 |
| 5h | 改写 `sample_docs`，加入一份你熟悉领域的 Markdown 文档 |
| 5h | 扩充 `cases.json`，手工标注预期来源；加入至少 5 条无答案问题 |
| 4h | 比较词匹配失败案例，尝试同义词、标题加权或向量检索 |
| 2h | 写一页检索错误分析，列出下一周要修的问题 |

运行：`python -m projects.doc_qa "忘记密码怎么重置？"` 和 `python -m projects.doc_qa.eval`。

完成标准：你能说清楚切分粒度、召回、排序、拒答阈值对结果的影响，并拿出自己的失败案例。

