# 01: 工程脚手架 + parse 命令（tracer bullet 第一发）

**What to build:** 从零建起可运行的 Python 工程：uv 管理依赖、src layout、console script 入口 `resume-cli`。`parse` 子命令端到端可用——读取本地 PDF 简历，提取文本打印到 stdout。四类文件异常（文件不存在 / 非 PDF / 无法读取 / 文本为空）各自给出区分性的中文错误提示与对应退出码（业务错 1、用法错 2）。附带合成中文示例简历（虚构人物，无隐私数据），pytest 测试设施同步就位。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] `uv sync` 后 `resume-cli --help` 与 `resume-cli parse --help` 正常显示用法
- [ ] `resume-cli parse examples/resume.pdf` 输出完整中文简历文本，退出码 0
- [ ] 文件不存在、非 PDF（魔数校验）、损坏或加密、文本为空四种情况输出区分性中文错误，退出码 1
- [ ] 缺少必要参数等用法错误退出码 2
- [ ] pytest 全绿：parse 正常路径 + 四类异常（CliRunner 从 CLI 边界断言）+ --help 存在性
- [ ] examples/ 含合成中文简历 PDF（虚构人物），供演示与测试共用
