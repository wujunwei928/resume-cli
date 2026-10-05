"""命令行入口：子命令定义与编排。

stdout 只放结果，日志与错误走 stderr；业务错误退出码 1，用法错误由 typer 产生退出码 2。
"""

from pathlib import Path

import typer

from .exceptions import ResumeCliError
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


if __name__ == "__main__":
    app()
