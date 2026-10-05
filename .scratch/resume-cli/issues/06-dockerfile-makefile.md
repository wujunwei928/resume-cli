# 06: Dockerfile + Makefile

**What to build:** 容器化交付与一键复现：Dockerfile 基于 python:3.12-slim 安装项目并设 entrypoint；Makefile 提供 install / test / demo-parse / demo-extract / demo-score / build 目标，demo-* 统一以 `--mock` 调用 examples 数据，保证无 Key 可复现演示。

**Blocked by:** 03（score 命令；可与 04 / 05 并行）

**Status:** ready-for-agent

- [ ] `make install` 与 `make test` 在 Windows Git Bash 环境可用
- [ ] `make demo-parse` / `make demo-extract` / `make demo-score` 均以 --mock 成功运行 examples 数据
- [ ] Dockerfile 构建成功且容器内 `resume-cli --help` 可运行；若本机无 Docker 环境，在工单 Comments 注明「未本机验证」
- [ ] 提供 .dockerignore，排除依赖缓存、测试产物等无关文件
