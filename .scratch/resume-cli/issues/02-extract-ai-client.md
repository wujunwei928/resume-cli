# 02: extract 命令 + AI 客户端抽象

**What to build:** `extract` 子命令全链路：建立 AI 客户端接口抽象，其下两个实现——litellm 真实实现（按 ADR-0001，默认 `deepseek/deepseek-flash`，`RESUME_CLI_MODEL` 可切换）与 MockClient（`--mock` 时启用，按简历关键词启发式返回预置画像，输出附 `"mock": true`）。定义简历画像契约（pydantic：name / phone / email / city / education 列表 / skills 列表，education 含 school / major / degree / graduation_time）。集中管理 extract prompt。配置集中读取（模型、超时、提供商官方 key 变量），缺 Key 时给指引性错误。JSON 解析先用简版（围栏剥离 + 直接反序列化），完整防线在 04 强化。

**Blocked by:** 01（工程脚手架 + parse）

**Status:** ready-for-agent

- [x] 配置 DEEPSEEK_API_KEY 后 `resume-cli extract examples/resume.pdf` 输出符合题目英文键名的画像 JSON（缩进 2），退出码 0
- [x] `--mock` 下同样命令零网络调用成功，输出含 `"mock": true` 字段
- [x] 未配置任何 Key 且未加 --mock 时，错误信息同时指引「配置 Key」与「使用 --mock」两条出路
- [x] AI 调用失败（网络错误 / 鉴权失败 / 超时）错误信息区分原因，退出码 1
- [x] 画像契约单测：缺必填字段、类型错误的 AI 返回被 pydantic 拦截报错
- [x] `--mock` 端到端 CLI 测试（CliRunner）全绿
- [x] CLI 编排层只依赖 AI 客户端接口，不感知 litellm / Mock 具体实现
