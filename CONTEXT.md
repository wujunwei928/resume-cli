# resume-cli

面向招聘场景的简历解析 CLI 工具：读取本地 PDF 简历，调用大模型完成结构化信息提取与岗位匹配评分。

## Language

**简历（Resume）**:
候选人提供的 PDF 格式个人履历文件，是所有命令的输入。
_Avoid_: CV、候选人文件

**JD / 岗位描述（Job Description）**:
描述招聘岗位职责与要求的纯文本文件，仅 `score` 命令使用。
_Avoid_: 招聘需求、职位说明

**简历画像（Profile）**:
`extract` 命令从简历中提取出的结构化字段集合（姓名、电话、邮箱、城市、教育经历、技能）。
_Avoid_: 结构化结果、信息抽取结果

**匹配评分（ScoreResult）**:
`score` 命令输出的评估结果：技能/经验/学历三项分项分、总分、评语与建议面试问题。
_Avoid_: 打分、评估报告

**Mock 模式（Mock Mode）**:
通过 `--mock` 启用的演示与测试模式：PDF 解析照常执行，AI 调用替换为本地预置实现，不消耗 API 配额。
_Avoid_: 离线模式、假数据模式

**AI 客户端（AI Client）**:
对大模型调用的统一抽象，真实实现走 litellm，Mock 实现返回预置结果。
_Avoid_: model、provider
