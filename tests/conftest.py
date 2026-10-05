"""测试夹具与公共辅助。

click 8.5 的 CliRunner 将 stdout/stderr 合流进 Result.output（capture 仅支持
sys/fd），因此 JSON 断言统一走 stdout_json() 提取器；「重定向纯净」的产品
语义由真实子进程测试（test_output_logging）验证。
"""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from typer.main import get_command

ROOT = Path(__file__).resolve().parent.parent


def visible_output(result) -> str:
    """合并 stdout 与 stderr 后的完整输出。"""
    return (result.output or "") + (result.stderr or "")


def stdout_json(result) -> dict:
    """从合流输出中提取 stdout 的 JSON 对象（工具捕获限制下的提取器）。"""
    text = result.output
    start = text.find("{")
    if start == -1:
        raise AssertionError(f"输出中未找到 JSON：{text!r}")
    data, _ = json.JSONDecoder().raw_decode(text, start)
    return data


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def cmd():
    """typer 应用转成 click 命令，供 click CliRunner 调用。"""
    from resume_cli.cli import app

    return get_command(app)


@pytest.fixture
def example_resume() -> Path:
    path = ROOT / "examples" / "resume.pdf"
    if not path.exists():
        pytest.skip("示例简历未生成，请先运行 scripts/make_examples.py")
    return path
