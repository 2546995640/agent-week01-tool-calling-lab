# 分阶段开源项目索引

这些是**参考项目与源码入口**，不是本仓库的依赖，也没有复制它们的代码。选择依据是项目公开、持续维护、拥有大量使用者，并有能对应当前阶段的示例。仓库热度会变化；以下链接和许可证信息核对于 **2026-09-20**，使用前仍应查看原仓库最新说明。

| 阶段 | 项目与入口 | 建议怎么学 |
| --- | --- | --- |
| Week 01 | [OpenAI Cookbook](https://github.com/openai/openai-cookbook) | 当作 API 示例索引；先完成本仓库的小循环，再对照官方示例的输入、输出和异常处理 |
| Week 02 | [OpenAI Agents SDK：工具示例](https://github.com/openai/openai-agents-python/blob/main/examples/basic/tools.py) 与 [续接示例](https://github.com/openai/openai-agents-python/blob/main/examples/basic/previous_response_id.py) | 用 SDK 重写 Week 01 的一个工具；比较自己管理循环与 SDK 管理循环 |
| Week 03–04 | [LangGraph RAG 示例](https://github.com/langchain-ai/langgraph/tree/main/examples/rag) | 先跑本仓库透明的 BM25 基线，再看图式工作流如何组合检索、判断和生成；不要直接照搬复杂架构 |
| Week 05–06 | [LangGraph 人工介入示例](https://github.com/langchain-ai/langgraph/tree/main/examples/human_in_the_loop) 与 [MCP Python SDK 简单工具](https://github.com/modelcontextprotocol/python-sdk/tree/main/examples/servers/simple-tool) | 对照本仓库的批准边界；尝试把一个只读工具封装为 MCP 服务 |
| Week 07 | [Promptfoo RAG 评测示例](https://github.com/promptfoo/promptfoo/tree/main/examples/eval-rag) | 把自己的案例集转为声明式评测，比较提示词或检索策略；检查指标定义是否一致 |

以上原仓库在核对时均标示为 MIT 许可证。请在原仓库查看最新许可证、依赖和运行条件；若以后复制代码，应保留许可证及署名。当前仓库只保存链接、学习建议和我们自己编写的代码。

## 使用顺序

1. 先完成对应周次的本仓库练习，留下自己的基线和疑问。
2. 只阅读外部项目中与疑问直接相关的一个示例。
3. 用自己的话写出两种实现的差异，再做一个小改动。
4. 不以“运行过热门框架示例”替代独立完成项目。

