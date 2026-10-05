# 03: score 命令

**What to build:** `score` 子命令：`--jd` 必选参数读取 JD 文本文件，将简历文本与 JD 一并交给模型匹配评分。score prompt 产出契约：overall_score / skill_score / experience_score / education_score（0-100 整数）、comment（简评）、interview_questions（建议面试问题列表）。复用 02 建立的 AI 调用管线与 MockClient（mock 评分同样按关键词启发式生成）。JD 文件异常（不存在 / 内容为空）有区分性错误处理。

**Blocked by:** 02（extract + AI 客户端抽象）

**Status:** ready-for-agent

- [ ] `resume-cli score examples/resume.pdf --jd examples/jd.txt`（真实或 `--mock`）输出符合题目字段的评分 JSON，退出码 0
- [ ] examples/ 含中文 JD 文本文件
- [ ] 四项分数均为 0-100 整数：越界、非整数的返回被校验拦截（契约单测）
- [ ] JD 文件不存在 / 内容为空输出区分性中文错误，退出码 1
- [ ] `--mock` 端到端 CLI 测试全绿，comment 与 interview_questions 为非空中文
