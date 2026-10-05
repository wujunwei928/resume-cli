# 07: README（面向面试官的完整文档）

**What to build:** 按笔试题目要求撰写中文 README，八节齐全：项目简介、技术选型、环境变量配置方式、安装方式、CLI 命令说明、示例输入和输出、已实现功能、已知问题或未完成内容。示例输出从真实运行（或 --mock）截取，保证与实际行为一致；目标是面试官 clone 后数分钟内跑通全部三命令。

**Blocked by:** 04（JSON 三层防线）、05（--output + 日志）、06（Dockerfile + Makefile）

**Status:** ready-for-agent

- [ ] 八节齐全：项目简介 / 技术选型 / 环境变量配置 / 安装方式 / CLI 命令说明 / 示例输入输出 / 已实现功能 / 已知问题
- [ ] 环境变量表覆盖 RESUME_CLI_MODEL、RESUME_CLI_TIMEOUT 与各提供商官方 key 变量
- [ ] 安装方式同时覆盖 uv 与 pip 两条路径
- [ ] 三个子命令与全局 flag（--mock / --verbose / --output）均有可复制的完整命令示例
- [ ] 示例输入输出与实际运行结果一致（演示以 --mock 为主，真实调用给出配置说明）
- [ ] 已实现功能对照题目逐项勾选（核心三命令 + 5 个加分项），已知问题如实列出
- [ ] 按面试官视角从零 clone 走一遍 README，数分钟内可跑通 parse / extract / score
