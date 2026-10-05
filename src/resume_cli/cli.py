"""命令行入口：子命令定义与编排。

stdout 只放结果，日志与错误走 stderr；业务错误退出码 1，用法错误由 typer 产生退出码 2。
"""

import json
from pathlib import Path

import typer
from pydantic import ValidationError

from .ai.base import AIClient
from .ai.litellm_client import LiteLLMClient
from .ai.mock_client import MockClient
from .ai.prompts import extract_user_prompt, EXTRACT_SYSTEM
from .config import detect_api_key, KNOWN_KEY_VARS, resolve_model, resolve_timeout
from .exceptions import ConfigurationError, ResumeCliError
from .json_utils import parse_model_json
from .models import Profile
from .pdf_parser import extract_text

app = typer.Typer(
    help="AI 简历解析 CLI：提取 PDF 文本、结构化简历画像、JD 匹配评分。",
    no_args_is_help=True,
)


@app.callback()
def _root() -> None:
    """resume-cli —— AI 简历解析命令行工具。"""


def _fail(message: str) -> None:
    typer.secho(f"错误：{message}", fg=typer.colors.RED, err=True)
    raise typer.Exit(code=1)


def _make_client(mock: bool) -> AIClient:
    """按 --mock 与环境变量构造 AI 客户端。"""
    if mock:
        return MockClient()
    if detect_api_key() is None:
        raise ConfigurationError(
            "未检测到任何 AI 提供商的 API Key。\n"
            "请设置环境变量（如 DEEPSEEK_API_KEY）后再试，"
            "或使用 --mock 模式体验完整流程（无需 Key）。\n"
            f"支持的 Key 环境变量：{'、'.join(KNOWN_KEY_VARS)}"
        )
    return LiteLLMClient(model=resolve_model(), timeout=resolve_timeout())


@app.command()
def parse(
    pdf_path: Path = typer.Argument(help="PDF 简历文件路径"),
) -> None:
    """读取 PDF 简历并打印其中的文本内容。"""
    try:
        text = extract_text(pdf_path)
    except ResumeCliError as exc:
        _fail(str(exc))
    typer.echo(text)


@app.command()
def extract(
    pdf_path: Path = typer.Argument(help="PDF 简历文件路径"),
    mock: bool = typer.Option(False, "--mock", help="使用本地 Mock 模式，不调用 AI API"),
) -> None:
    """调用 AI 从简历中提取结构化信息，输出画像 JSON。"""
    try:
        text = extract_text(pdf_path)
        client = _make_client(mock)
        raw = client.complete(EXTRACT_SYSTEM, extract_user_prompt(text))
        data = parse_model_json(raw)
        profile = Profile.model_validate(data)
    except ResumeCliError as exc:
        _fail(str(exc))
    except ValidationError as exc:
        problems = "; ".join(
            f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}"
            for e in exc.errors()[:3]
        )
        _fail(f"AI 返回结果未通过字段校验：{problems}")

    payload = profile.model_dump()
    if mock:
        payload["mock"] = True
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
