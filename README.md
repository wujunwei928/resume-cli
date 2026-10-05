# resume-cli —— AI 简历解析 CLI

读取本地 PDF 简历，调用大模型完成**结构化信息提取**与**岗位匹配评分**的命令行工具。

```text
resume-cli parse  ./resume.pdf                 # 提取 PDF 文本
resume-cli extract ./resume.pdf                # AI 提取画像 JSON（姓名/电话/教育/技能…）
resume-cli score  ./resume.pdf --jd ./jd.txt   # AI 匹配评分（四项 0-100 分 + 评语 + 面试问题）
```

三个命令均支持 `--mock` 本地演示模式（无需 API Key）与 `--output result.json` 结果落盘。

## 项目简介

在招聘流程中，快速理解候选人简历并判断其与岗位的匹配程度是一项常见但耗时的工作。
本工具把这条链路压缩成三条 CLI 命令：PDF 文本提取 → 大模型结构化提取（简历画像）→
简历与 JD 的匹配评分，输出可直接下游使用的 JSON。

- 中文简历友好：PDF 中文文本提取质量稳定，错误提示全部为中文
- 工程化完整：异常分类（退出码 0/1/2）、JSON 三层防线、校验失败自动重试、日志分流
- 可演示：`--mock` 模式零网络依赖，`make demo-*` 一键复现全部效果

## 技术选型

| 依赖 | 用途 | 选择理由 |
| --- | --- | --- |
| [typer](https://typer.tiangolo.com/) | CLI 框架 | 基于类型注解自动生成 `--help`，代码量少，现代 Python 风格 |
| [pdfplumber](https://github.com/jsvine/pdfplumber) | PDF 文本提取 | 中文提取质量好、MIT 许可 |
| [litellm](https://github.com/BerriAI/litellm) | 大模型接入 | 一套代码切换 100+ 提供商（`provider/model` 前缀路由），决策记录见 [docs/adr/0001](docs/adr/0001-litellm-unified-model-access.md) |
| [pydantic](https://docs.pydantic.dev/) v2 | 输出契约校验 | 模型定义 + 字段校验 + 可读错误一步到位 |
| [json-repair](https://github.com/mangiucugna/json_repair) | 脏 JSON 修复 | 兜底修复 AI 返回的尾逗号/单引号/注释等 |

AI 客户端抽象为统一接口，`--mock` 的本地实现与 litellm 真实实现可互换，测试与演示不依赖真实 API。

## 环境变量配置

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `RESUME_CLI_MODEL` | `deepseek/deepseek-flash` | litellm 风格模型标识，`provider/model` 前缀，如 `zhipu/glm-4.6`、`openai/gpt-4o-mini` |
| `RESUME_CLI_TIMEOUT` | `60` | AI 请求超时秒数 |
| `DEEPSEEK_API_KEY` | — | DeepSeek 的 Key（默认模型对应） |
| `ZHIPUAI_API_KEY` / `OPENAI_API_KEY` / `MOONSHOT_API_KEY` / `ANTHROPIC_API_KEY` / `OPENROUTER_API_KEY` | — | 切换对应提供商时设置其官方 Key 变量（由 litellm 自动读取） |

示例（DeepSeek）：

```bash
export DEEPSEEK_API_KEY=sk-xxxxxxxx
export RESUME_CLI_MODEL=deepseek/deepseek-flash   # 可省略，即默认值
```

未配置任何 Key 时会得到指引性错误，也可直接加 `--mock` 体验完整流程。

## 安装方式

**方式一：uv（推荐）**

```bash
uv sync
uv run resume-cli --help
```

**方式二：pip**

```bash
pip install .          # 或 pip install -e . 开发安装
resume-cli --help
```

**方式三：Docker**

```bash
docker build -t resume-cli .
docker run --rm resume-cli extract /app/examples/resume.pdf --mock
```

> 需要真实调用 AI 时，通过 `-e DEEPSEEK_API_KEY=sk-xxx` 传入 Key。

## CLI 命令说明

所有命令支持 `--help` 查看用法。`--verbose` 为全局选项，需放在子命令之前。

### `resume-cli parse <pdf_path>`

读取 PDF 简历并打印文本。四类异常均有中文提示且退出码为 1：
文件不存在 / 文件不是 PDF（魔数校验）/ PDF 无法读取（损坏或加密）/ 文本为空（如纯扫描件）。

### `resume-cli extract <pdf_path> [--mock] [--output result.json]`

调用 AI 提取简历画像，输出 JSON（字段名与题目契约一致）：
`name` / `phone` / `email` / `city` / `education[]`（school、major、degree、graduation_time）/ `skills[]`。
AI 返回经过 JSON 解析与 pydantic 校验双重把关，失败自动带错误重试一次。

### `resume-cli score <pdf_path> --jd <jd_path> [--mock] [--output result.json]`

读取 JD 文本文件，与简历一起交给 AI 匹配评分，输出 JSON：
`overall_score` / `skill_score` / `experience_score` / `education_score`（0-100 整数）、
`comment`（一句话总评）、`interview_questions[]`（建议面试问题）。
JD 文件不存在或内容为空时给出中文错误。

### 通用行为

- 结果 JSON 走 **stdout**，日志与错误走 **stderr**，可安全 `> result.json` 重定向
- `--mock`：本地演示模式，PDF 解析照常执行，AI 调用替换为本地启发式实现，输出附 `"mock": true`
- 退出码：`0` 成功；`1` 业务错误（文件/AI/校验）；`2` 用法错误（如缺少子命令参数；裸执行 `resume-cli` 时直接显示帮助并以 0 退出，属刻意为之的常见 CLI 惯例）

## 示例输入和输出

示例数据在 `examples/`（虚构人物，无隐私），可用 `scripts/make_examples.py` 重新生成。

**parse**

```console
$ resume-cli parse examples/resume.pdf
张伟明
电话：138-0013-8000 | 邮箱：zhangweiming@example.com | 城市：杭州
教育经历
杭州电子科技大学 软件工程 本科 2018 届
技能
Python / JavaScript / TypeScript / React / FastAPI / Docker / MySQL
…
```

**extract --mock**

```json
{
  "name": "张伟明",
  "phone": "138-0013-8000",
  "email": "zhangweiming@example.com",
  "city": "杭州",
  "education": [
    {
      "school": "演示大学",
      "major": "计算机科学与技术",
      "degree": "本科",
      "graduation_time": "2020"
    }
  ],
  "skills": ["Python", "JavaScript", "TypeScript", "React", "FastAPI", "Java", "Docker", "MySQL"],
  "mock": true
}
```

**score --mock**

```json
{
  "overall_score": 84,
  "skill_score": 95,
  "experience_score": 78,
  "education_score": 75,
  "comment": "候选人具备较扎实的全栈开发基础，命中 10 项岗位相关技能，工程经历完整；简历中未明确体现大模型 API 的深度实践，建议面试重点确认。",
  "interview_questions": [
    "请介绍一个你主导过的全栈项目，以及你在其中的角色。",
    "你是否有调用大模型 API 的实际经验？请举例说明。",
    "你如何保证项目的工程质量（测试、CI、文档）？"
  ],
  "mock": true
}
```

> 以上为 `--mock` 输出；配置 API Key 后同一命令即返回真实模型结果（技能/城市/评语由模型依据简历生成）。

## 已实现功能

核心要求：

- [x] `parse`：PDF 文本提取 + 四类异常中文提示
- [x] `extract`：AI 结构化提取，输出契约 JSON，字段校验
- [x] `score`：JD 匹配评分，四项 0-100 分 + 评语 + 面试问题，JD 异常处理
- [x] `--help` 全命令可用，输出适合终端查看，JSON 缩进 2

加分项（全部实现）：

- [x] `--output result.json` 保存结果
- [x] `--mock` 模式：无 API Key 完整演示（PDF 真实解析 + 本地 AI 替身）
- [x] AI 返回 JSON 自动修复（围栏剥离 / 截取 / json-repair，校验失败带错误重试一次）
- [x] 简单日志（INFO 关键节点走 stderr，`--verbose` 升 DEBUG 含 prompt 摘要）
- [x] Dockerfile 与 Makefile（`make demo-*` 一键复现演示）

测试：44 项 pytest（CLI 边界端到端、JSON 修复各形态、pydantic 契约、重试语义、真实子进程重定向纯净性）。

## 已知问题或未完成内容

- 纯扫描件（无文字层 PDF）不支持，提示「文本为空」；OCR 不在本期范围
- 评分/提取质量依赖所用模型，prompt 以「演示可用」为准，未做系统性调优
- `--mock` 的画像为启发式演示数据（姓名/电话/邮箱识别自简历文本，教育经历为占位值），不代表真实解析能力
- litellm 首次调用会做少量初始化，首包延迟略高；已关闭其联网价格表拉取与 debug 噪音
- Makefile 目标与 Dockerfile 构建在 Windows Git Bash 环境未本机验证（本机无 make/docker，demo 目标的等价命令已逐一验证通过）
- 暂不支持 DOCX/图片简历、批量目录处理

## 项目结构

```text
src/resume_cli/
├── cli.py          # typer 命令编排：parse / extract / score
├── pdf_parser.py   # pdfplumber 封装与四类文件异常
├── ai/             # AI 客户端子包
│   ├── base.py         # 客户端接口（编排层唯一依赖）
│   ├── litellm_client.py   # 真实实现（ADR-0001）
│   ├── mock_client.py      # --mock 本地实现
│   ├── prompts.py      # extract / score 的 prompt 模板
│   └── pipeline.py     # 调用→解析→校验→重试 共用管线
├── models.py       # pydantic 契约：Profile / ScoreResult
├── json_utils.py   # 脏 JSON 修复
├── config.py       # 环境变量集中读取
├── log.py          # 日志初始化（stderr 分流）
└── exceptions.py   # 业务异常体系
tests/              # 44 项测试（CLI 接缝为主）
examples/           # 合成示例简历与 JD
```

## 开发

```bash
uv sync                       # 安装依赖（含 dev）
uv run pytest -q              # 运行测试
uv run python scripts/make_examples.py   # 重新生成示例文件
```
