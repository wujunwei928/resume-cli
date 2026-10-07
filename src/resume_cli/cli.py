"""命令行入口：子命令定义与编排。

stdout 只放结果，日志与错误走 stderr；业务错误退出码 1，用法错误由 typer 产生退出码 2，
裸执行（无子命令）打印帮助并以 0 退出。
"""

import json
import logging
import time
from pathlib import Path

import typer

from .ai.base import AIClient
from .ai.litellm_client import LiteLLMClient
from .ai.mock_client import MockClient
from .ai.pipeline import run_structured_task
from .ai.prompts import (
    extract_user_prompt,
    EXTRACT_SYSTEM,
    score_user_prompt,
    SCORE_SYSTEM,
)
from .config import detect_api_key, KNOWN_KEY_VARS, resolve_model, resolve_timeout
from .exceptions import ConfigurationError, JdFileError, ResumeCliError
from .log import setup_logging
from .models import Profile, ScoreResult
from .pdf_parser import extract_text

log = logging.getLogger(__name__)

app = typer.Typer(
    help="AI 简历解析 CLI：提取 PDF 文本、结构化简历画像、JD 匹配评分。",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", help="输出 DEBUG 级调试日志（含 prompt 摘要）"),
) -> None:
    """resume-cli —— AI 简历解析命令行工具。"""
    setup_logging(verbose=verbose)
    if ctx.invoked_subcommand is None:
        # 裸执行或只给全局选项时：打印帮助并以 0 退出（类 Unix 成功惯例）。
        # 不用 no_args_is_help——click 8.5 将其实现为 UsageError，退出码为 2。
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


def _fail(message: str) -> None:
    typer.secho(f"错误：{message}", fg=typer.colors.RED, err=True)
    raise typer.Exit(code=1)


def _log_extracted(pdf_path: Path, extracted) -> None:
    log.info("PDF 解析完成：%s（%d 页 / %d 字符）", pdf_path, extracted.pages, len(extracted.text))


def _make_client(mock: bool) -> AIClient:
    """按 --mock 与环境变量构造 AI 客户端。"""
    if mock:
        log.info("使用 Mock 模式（不调用 AI API）")
        return MockClient()
    if detect_api_key() is None:
        raise ConfigurationError(
            "未检测到任何 AI 提供商的 API Key。\n"
            "请设置环境变量（如 DEEPSEEK_API_KEY）后再试，"
            "或使用 --mock 模式体验完整流程（无需 Key）。\n"
            f"支持的 Key 环境变量：{'、'.join(KNOWN_KEY_VARS)}"
        )
    model = resolve_model()
    log.info("使用模型：%s", model)
    return LiteLLMClient(model=model, timeout=resolve_timeout())


def _run_ai_task(client: AIClient, system: str, user: str, model_cls):
    started = time.perf_counter()
    result, raw = run_structured_task(client, system, user, model_cls)
    log.info("AI 调用完成：耗时 %.1fs / 返回 %d 字符", time.perf_counter() - started, len(raw))
    return result


def _dump_payload(payload: dict, mock: bool, output: Path | None) -> None:
    if mock:
        payload["mock"] = True
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    typer.echo(rendered)
    if output is not None:
        try:
            output.write_text(rendered + "\n", encoding="utf-8")
        except OSError as exc:
            _fail(f"无法写入输出文件 {output}：{exc}")
        typer.secho(f"已保存到 {output}", fg=typer.colors.GREEN, err=True)


@app.command()
def parse(
    pdf_path: Path = typer.Argument(help="PDF 简历文件路径"),
) -> None:
    """读取 PDF 简历并打印其中的文本内容。"""
    try:
        extracted = extract_text(pdf_path)
    except ResumeCliError as exc:
        _fail(str(exc))
    _log_extracted(pdf_path, extracted)
    typer.echo(extracted.text)


@app.command()
def extract(
    pdf_path: Path = typer.Argument(help="PDF 简历文件路径"),
    mock: bool = typer.Option(False, "--mock", help="使用本地 Mock 模式，不调用 AI API"),
    output: Path = typer.Option(None, "--output", help="结果同时保存到该 JSON 文件"),
) -> None:
    """调用 AI 从简历中提取结构化信息，输出画像 JSON。"""
    try:
        extracted = extract_text(pdf_path)
        _log_extracted(pdf_path, extracted)
        client = _make_client(mock)
        profile = _run_ai_task(
            client, EXTRACT_SYSTEM, extract_user_prompt(extracted.text), Profile
        )
    except ResumeCliError as exc:
        _fail(str(exc))
    _dump_payload(profile.model_dump(), mock, output)


def _read_jd(jd_path: Path) -> str:
    if not jd_path.exists():
        raise JdFileError(f"JD 文件不存在：{jd_path}\n请检查 --jd 参数指向的路径。")
    if not jd_path.is_file():
        raise JdFileError(f"JD 路径不是文件：{jd_path}\n请提供 JD 文本文件的路径。")
    try:
        jd_text = jd_path.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError as exc:
        raise JdFileError(
            f"JD 文件不是 UTF-8 编码：{jd_path}\n请将文件另存为 UTF-8 编码后重试。"
        ) from exc
    except OSError as exc:
        raise JdFileError(f"无法读取 JD 文件：{jd_path}\n原始错误：{exc}") from exc
    if not jd_text:
        raise JdFileError(f"JD 文件内容为空：{jd_path}\n请提供包含岗位描述的文本文件。")
    log.info("JD 读取完成：%s（%d 字符）", jd_path, len(jd_text))
    return jd_text


@app.command()
def score(
    pdf_path: Path = typer.Argument(help="PDF 简历文件路径"),
    jd_path: Path = typer.Option(..., "--jd", help="岗位描述（JD）文本文件路径"),
    mock: bool = typer.Option(False, "--mock", help="使用本地 Mock 模式，不调用 AI API"),
    output: Path = typer.Option(None, "--output", help="结果同时保存到该 JSON 文件"),
) -> None:
    """调用 AI 评估简历与 JD 的匹配程度，输出评分 JSON。"""
    try:
        extracted = extract_text(pdf_path)
        _log_extracted(pdf_path, extracted)
        jd_text = _read_jd(jd_path)
        client = _make_client(mock)
        result = _run_ai_task(
            client, SCORE_SYSTEM, score_user_prompt(extracted.text, jd_text), ScoreResult
        )
    except ResumeCliError as exc:
        _fail(str(exc))
    _dump_payload(result.model_dump(), mock, output)


def main() -> None:
    """入口：Ctrl/Cmd+C 收敛为干净提示与退出码 130（128+SIGINT），不甩 traceback。"""
    try:
        app()
    except KeyboardInterrupt:
        typer.secho("\n已取消。", fg=typer.colors.YELLOW, err=True)
        raise SystemExit(130)


if __name__ == "__main__":
    main()
