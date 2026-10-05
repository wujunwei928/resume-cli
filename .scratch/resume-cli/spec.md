# resume-cli 实现规格（AI 简历解析 CLI Demo）

Status: ready-for-agent

## Problem Statement

招聘流程中，快速理解候选人简历并判断其与岗位的匹配程度是常见但耗时的工作。候选人（笔试应考人）需要在有限时间内交付一个可运行、可演示、结构清晰的 CLI 工具，读取本地 PDF 简历，调用大模型提取关键信息，并根据岗位描述（JD）进行匹配评分。交付物将按以下权重被面试官评估：CLI 功能完整性 25%、AI 集成能力 25%（Prompt 设计 / JSON 输出 / 错误处理 / 字段校验）、全栈工程质量 25%（项目结构 / 配置管理 / 代码可读性 / 异常处理）、PDF 与文件处理 15%、README 与演示 10%。

## Solution

一个名为 `resume-cli` 的 Python 命令行工具，提供三个子命令：

- `resume-cli parse <pdf>` — 提取 PDF 文本并打印；
- `resume-cli extract <pdf>` — 调用大模型提取结构化简历画像（Profile），输出 JSON；
- `resume-cli score <pdf> --jd <jd.txt>` — 将简历与 JD 交给大模型匹配评分，输出四项 0-100 分、评语与建议面试问题的 JSON。

支持 `--mock`（无 API Key 演示与测试）、`--output <file>`（结果落盘）、`--verbose`（调试日志）。提供 README、Dockerfile、Makefile、pytest 测试与示例数据，使面试官 clone 后数分钟内可运行并复现演示。

## User Stories

### 简历解析（parse）

1. 作为招聘人员，我希望执行 `resume-cli parse ./resume.pdf` 就能在终端看到简历全文，以便快速浏览候选人履历。
2. 作为招聘人员，我希望解析含中文的简历 PDF 时文本完整可读、不乱码，以便处理国内候选人的简历。
3. 作为用户，当我传入不存在的文件路径时，我希望看到一条清晰的中文错误提示而非堆栈崩溃，以便立即纠正路径。
4. 作为用户，当我传入的文件不是 PDF（如 .docx 或 .txt 改名）时，我希望工具明确提示「文件不是 PDF」，以便区分问题类型。
5. 作为用户，当 PDF 文件损坏或加密无法读取时，我希望得到「无法读取」的错误提示，以便判断文件本身的问题。
6. 作为用户，当 PDF 能打开但提取不出任何文本（如纯扫描图）时，我希望得到「文本为空」的提示，以便知道需要 OCR 而非误以为工具坏了。
7. 作为用户，我希望所有错误都有非零退出码，以便在脚本中串联使用时能检测失败。

### 结构化提取（extract）

8. 作为招聘人员，我希望 `resume-cli extract ./resume.pdf` 输出包含姓名、电话、邮箱、城市、教育经历列表、技能列表的 JSON，以便导入下游系统。
9. 作为招聘人员，我希望教育经历包含学校、专业、学历、毕业时间四个字段，以便按学历维度筛选。
10. 作为用户，我希望 AI 返回的 JSON 经过字段校验后才输出，以便拿到的数据一定是契约规定的形状。
11. 作为用户，当 AI 调用失败（网络错误、Key 无效、限流）时，我希望看到区分原因的清晰错误提示，以便知道该换 Key 还是该重试。
12. 作为用户，当 AI 返回夹在 markdown 围栏或带尾逗号的「脏 JSON」时，我希望工具自动修复后仍给出结果，以便一次调用就成功。
13. 作为用户，当 AI 返回内容经修复仍无法通过校验时，我希望工具带着校验错误自动重试一次，以便提高无人工介入的成功率。

### JD 匹配评分（score）

14. 作为招聘人员，我希望 `resume-cli score ./resume.pdf --jd ./jd.txt` 输出总分、技能分、经验分、学历分（均为 0-100 整数）、一句评语和若干建议面试问题，以便快速决定是否进入面试。
15. 作为用户，当 JD 文件不存在或内容为空时，我希望得到明确错误提示，以便修正输入。
16. 作为用户，我希望评语简明扼要指出匹配点与缺口（如「缺少大模型应用经验」），以便直接用于面试准备。

### Mock 演示与测试

17. 作为候选人，我希望加 `--mock` 后无需 API Key 也能完整演示 extract 和 score，以便录制演示视频时不依赖网络与配额。
18. 作为候选人，我希望 `--mock` 下 PDF 解析仍然真实执行，以便演示同时证明 parse 能力是真的。
19. 作为用户，我希望 mock 输出中带有明确的 mock 标记，以便不会把演示数据误当真实结果。
20. 作为开发者，我希望 MockClient 与真实客户端实现同一接口，以便测试与生产代码共用同一抽象。

### 输出与日志

21. 作为用户，我希望 `--output result.json` 把结果保存为格式化 JSON 文件，以便留档与对比。
22. 作为用户，我希望日志（进度、页数、耗时）走 stderr、结果 JSON 走 stdout，以便 `resume-cli extract a.pdf > out.json` 管道重定向不污染结果。
23. 作为开发者，我希望 `--verbose` 能看到模型名、prompt 摘要等调试信息，以便排查提取质量问题。

### 模型切换与配置

24. 作为用户，我希望通过环境变量更换模型提供商（智谱 / DeepSeek / OpenAI / 本地模型），以便用手里有的 Key 和最便宜合适的模型。
25. 作为用户，我希望未配置 API Key 时得到「如何配置」的指引性错误，以便第一次使用就能自助解决。

### 工程与交付（面向面试官）

26. 作为面试官，我希望 clone 后按 README 一两条命令完成安装并跑通示例，以便把时间花在评估代码而非配环境。
27. 作为面试官，我希望 `resume-cli --help` 与各子命令 help 清晰完整，以便不看文档也能上手。
28. 作为面试官，我希望仓库包含示例简历与 JD，以便零准备复现演示视频。
29. 作为面试官，我希望 `make test` 一键跑全部测试，以便验证工程质量声明属实。
30. 作为面试官，我希望提供 Dockerfile 以便容器化运行，Makefile 以便一键复现演示。
31. 作为面试官，我希望 README 包含项目简介、技术选型、环境变量、安装、命令说明、示例输入输出、已实现功能、已知问题，以便按笔试要求逐项核对。
32. 作为维护者，我希望项目遵循 src layout 且模块职责单一，以便后续扩展（如 DOCX 支持）不动老代码。

## Implementation Decisions

### 模块划分

- **cli**：typer 应用与三个子命令、全局选项（--mock / --verbose / --output）、退出码、输出流分配。仅做编排，不含业务逻辑。
- **pdf_parser**：pdfplumber 封装。职责：读文件 → 校验存在性 / PDF 魔数 → 提取文本 → 空文本检测。四类异常各对应独立异常类型。
- **ai**：模型调用子包，含四个成员——接口（定义 complete 契约）、litellm 实现、mock 实现、prompt 模板（extract 与 score 的 system/user prompt，是评分核心资产，集中管理）。
- **models**：pydantic v2 模型。画像契约（Education 子模型含 school/major/degree/graduation_time；skills 为字符串列表）与评分契约（四项整数分 0-100、comment 字符串、interview_questions 字符串列表）。
- **json_utils**：脏 JSON 修复（围栏剥离 → 首尾花括号截取 → json-repair 库兜底）。
- **config**：环境变量集中读取（RESUME_CLI_MODEL 等），缺配置时给出指引性错误。
- **output**：终端人类可读渲染（分数条、字段对齐）与 --output 落盘。

### AI 接入（ADR-0001）

经 litellm 统一接入，默认模型 `deepseek/deepseek-flash`，`RESUME_CLI_MODEL` 切换（如 `zhipu/glm-4.6`），凭证用各提供商官方环境变量（DEEPSEEK_API_KEY / ZHIPUAI_API_KEY / OPENAI_API_KEY 等），由 litellm 自行读取。AI 调用收敛在接口之后，litellm 仅为真实实现细节。

### JSON 三层防线

1. Prompt 强约束「只输出 JSON」+ 尽力透传结构化输出参数（模型不支持时静默降级，不硬依赖）；
2. 解析层修复：剥 markdown 围栏 → 定位首 `{` 至末 `}` 截取 → json-repair 修尾逗号 / 单引号 / 注释；
3. 校验层：pydantic 校验失败时，将校验错误拼入重试 prompt 再调一次；仍失败则报错退出并在错误信息中保留 AI 原始响应摘要。

### Mock 行为

`--mock` 下 PDF 解析照常执行；AI 调用替换为 MockClient：按简历文本的关键词启发式（是否含「本科/硕士」「Python」等）生成画像与评分结果，输出 JSON 附 `"mock": true` 字段。MockClient 为生产代码（非测试专用），测试直接复用。

### CLI 契约

- 退出码：0 成功；2 用法错误（参数缺失等）；1 业务错误（四类 PDF 异常、JD 异常、AI 失败、校验失败）。
- stdout 只放结果（parse 为纯文本，extract/score 为缩进 2 的中文键 JSON 或按题目字段名原文——**按题目英文键名输出**，如 name/overall_score，保证与题目示例逐字段一致）。
- stderr 放日志与人类可读错误（错误同时含一句话原因与下一步建议）。

### 配置与日志

- 环境变量：RESUME_CLI_MODEL（默认 deepseek/deepseek-flash）、RESUME_CLI_TIMEOUT（默认 60s）；API Key 沿用提供商官方变量名。
- 日志：标准库 logging，INFO 级输出关键节点（文件路径、页数、字符数、模型名、耗时、mock 标记），--verbose 升 DEBUG；关闭 litellm 自身的冗余 debug 输出。

### 打包与工程化

- Python ≥ 3.10；uv 管理依赖，pyproject.toml 声明 console script 入口 `resume-cli`；pip 安装同样兼容。
- Dockerfile：python:3.12-slim 基础镜像，安装项目并设 entrypoint。
- Makefile：install / test / demo-parse / demo-extract / demo-score / build 目标，其中 demo-* 直接调用 examples/ 数据。
- examples/ 放合成的示例简历 PDF（虚构人物，避免隐私）与 jd.txt；测试与演示共用。

## Testing Decisions

- 好的测试只断言外部可观察行为（退出码、stdout/stderr 内容、--output 产物），不断言内部实现细节。
- **主接缝：CLI 入口**。全部功能测试经 typer 的 CliRunner 从命令行边界进入。覆盖：parse 四类文件异常（不存在 / 非 PDF / 损坏 / 空文本，空文本用程序生成的无文本层 PDF 夹具）、JD 不存在与为空、--mock 下 extract / score 端到端（含 --output 落盘断言）、--help 存在性、错误退出码。
- **AI 客户端接口**：不测 litellm 真实网络调用；MockClient 即该接缝的测试替身，其行为通过 CLI 层间接验证。
- **json_utils 纯函数单测**：围栏剥离、花括号截取、尾逗号 / 单引号修复、彻底非法输入报错。
- **models 校验单测**：缺必填字段、分数越界（<0 / >100 / 非整数）、类型错误。
- 本仓库为新工程，无既有测试先例；测试风格以 pytest + tmp_path 夹具为准。

## Out of Scope

- 批量处理、目录扫描、并发解析多个简历。
- DOCX / 图片简历、OCR、PDF 版面还原。
- Web UI、API 服务、数据库存储、简历库管理。
- 真实网络调用与模型输出质量纳入测试；评分的「准确性」调优（prompt 迭代以演示可用为准）。
- 演示视频录制（由候选人另行完成，README 提供复现命令即可）。
- Windows 之外的跨平台兼容性专门适配（开发环境为 Windows + Git Bash，保证此环境全绿；Linux 容器内基本可跑）。

## Further Notes

- 领域术语以根目录 CONTEXT.md 为准（简历 / JD / 简历画像 / 匹配评分 / Mock 模式 / AI 客户端）。
- litellm 选型决策记录见 docs/adr/0001-litellm-unified-model-access.md。
- extract 与 score 的输出字段名严格采用题目原文的英文键（name / phone / email / city / education / skills / overall_score / skill_score / experience_score / education_score / comment / interview_questions），值内容为中文；mock 场景额外附 `mock: true`。
- 实施顺序建议：核心三命令（parse → extract → score）→ mock → JSON 修复 → --output → 日志 → Dockerfile / Makefile → README，与题目「优先跑通核心流程」的备注一致。
