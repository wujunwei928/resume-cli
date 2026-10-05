"""测试夹具与公共辅助。"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parent.parent


def visible_output(result) -> str:
    """合并 stdout 与 stderr 后的完整输出（兼容 click 各版本的捕获行为）。"""
    combined = result.output or ""
    try:
        combined += result.stderr or ""
    except ValueError:  # click 8.1 默认 mix_stderr=True 时访问 stderr 会抛错
        pass
    return combined


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def example_resume() -> Path:
    path = ROOT / "examples" / "resume.pdf"
    if not path.exists():
        pytest.skip("示例简历未生成，请先运行 scripts/make_examples.py")
    return path
