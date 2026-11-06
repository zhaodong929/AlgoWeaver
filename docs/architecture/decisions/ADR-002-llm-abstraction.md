# ADR-002：模型调用通过 ChatModel 解耦

- 状态：Accepted
- 日期：2026-11-06

LiteLLM 负责多 Provider 适配，应用服务只依赖 `ChatModel` 协议；Mock 模型用于离线测试。模型输出必须先解析为 Pydantic 草稿，密钥只来自环境变量。
