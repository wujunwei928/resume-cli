# resume-cli 常用命令（demo-* 统一走 --mock，无 API Key 也可完整复现演示）

.PHONY: install test demo-parse demo-extract demo-score build

install: ## 安装依赖（uv sync）
	uv sync

test: ## 运行全部测试
	uv run pytest -q

demo-parse: ## 演示：提取示例简历文本
	uv run resume-cli parse examples/resume.pdf

demo-extract: ## 演示：Mock 模式提取画像
	uv run resume-cli extract examples/resume.pdf --mock

demo-score: ## 演示：Mock 模式 JD 匹配评分
	uv run resume-cli score examples/resume.pdf --jd examples/jd.txt --mock

build: ## 构建 Docker 镜像
	docker build -t resume-cli .
