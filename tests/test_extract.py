"""extract 命令接缝测试：经 CLI 边界验证 AI 抽象、mock 模式与配置指引。"""

import json

import pytest

from conftest import stdout_json, visible_output

from resume_cli.cli import app
from resume_cli.exceptions import ResumeCliError


def test_mock_extract_outputs_profile_json(cmd, runner, example_resume):
    result = runner.invoke(cmd, ["extract", str(example_resume), "--mock"])
    assert result.exit_code == 0, result.output
    data = stdout_json(result)
    for key in ("name", "phone", "email", "city", "education", "skills"):
        assert key in data, f"缺少字段 {key}"
    assert data["mock"] is True
    # mock 的技能启发式来自简历真实文本：示例简历含 Python/React
    assert "Python" in data["skills"]


def test_mock_extract_identifies_contact_from_text(cmd, runner, example_resume):
    """mock 承诺：姓名/电话/邮箱直接识别自简历文本，而非全预置。"""
    result = runner.invoke(cmd, ["extract", str(example_resume), "--mock"])
    data = stdout_json(result)
    assert data["name"] == "张伟明"
    assert data["phone"] == "138-0013-8000"
    assert data["email"] == "zhangweiming@example.com"


def test_mock_extract_marks_mock_true(cmd, runner, example_resume):
    result = runner.invoke(cmd, ["extract", str(example_resume), "--mock"])
    assert stdout_json(result)["mock"] is True


def test_missing_key_without_mock_gives_guidance(
    cmd, runner, example_resume, monkeypatch
):
    for var in (
        "DEEPSEEK_API_KEY",
        "ZHIPUAI_API_KEY",
        "OPENAI_API_KEY",
        "MOONSHOT_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENROUTER_API_KEY",
        "OPENAI_BASE_URL",
    ):
        monkeypatch.delenv(var, raising=False)
    result = runner.invoke(cmd, ["extract", str(example_resume)])
    assert result.exit_code == 1
    combined = visible_output(result)
    assert "API Key" in combined or "api key" in combined.lower()
    assert "--mock" in combined


def test_ai_failure_reports_clear_error(cmd, runner, example_resume, monkeypatch):
    class FailingClient:
        def complete(self, system: str, user: str) -> str:
            raise ResumeCliError("AI 调用失败：网络错误，请检查网络后重试。")

    import resume_cli.cli as cli_module

    monkeypatch.setattr(cli_module, "_make_client", lambda mock: FailingClient())
    result = runner.invoke(cmd, ["extract", str(example_resume)])
    assert result.exit_code == 1
    assert "AI 调用失败" in visible_output(result)


def test_extract_rejects_invalid_ai_payload(cmd, runner, example_resume, monkeypatch):
    class GarbageClient:
        def complete(self, system: str, user: str) -> str:
            return "抱歉，我无法处理该文档。"

    import resume_cli.cli as cli_module

    monkeypatch.setattr(cli_module, "_make_client", lambda mock: GarbageClient())
    result = runner.invoke(cmd, ["extract", str(example_resume)])
    assert result.exit_code == 1
    assert "JSON" in result.output or "校验" in result.output


@pytest.fixture(autouse=True)
def _clean_key_env(monkeypatch):
    """隔离外部环境，避免真实 Key 影响测试分支。"""
    from resume_cli.config import KNOWN_KEY_VARS

    for var in KNOWN_KEY_VARS:
        monkeypatch.delenv(var, raising=False)
