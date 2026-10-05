---
status: accepted
date: 2026-10-05
---

# 使用 litellm 统一大模型接入

resume-cli 需要调用大模型完成简历信息提取与 JD 匹配评分，且要求模型可灵活替换。决定通过 litellm 接入所有模型调用，而不是直接使用 openai SDK 或裸 HTTP 请求：litellm 以 `provider/model` 前缀统一路由（本项目默认 `deepseek/deepseek-flash`），更换提供商只需改环境变量 `RESUME_CLI_MODEL` 与对应 key，无需改代码。

## Considered Options

- **openai SDK + 自定义 base_url**：依赖轻，但只能覆盖 OpenAI 兼容端点，接非兼容提供商（如 Anthropic 原生协议）要另写适配层。
- **litellm（选定）**：一个依赖覆盖 100+ 提供商，换取统一调用面与免适配切换；代价是依赖较重、需关闭其自身的冗余 debug 日志。

## Consequences

- 各提供商凭证沿用其官方环境变量约定（如 `DEEPSEEK_API_KEY`），由 litellm 自行读取，本项目不再自定义 key 变量。
- AI 调用收敛到 `ai/base.py` 接口之后，litellm 仅是接口的真实实现细节，Mock 实现与测试不感知它。
