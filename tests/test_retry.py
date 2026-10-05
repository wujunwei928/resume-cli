"""校验失败自动重试接缝测试：经 CLI 边界验证「恰好重试一次」与最终报错保留原始响应。"""

import json

from conftest import stdout_json, visible_output

from resume_cli.cli import app

GOOD_PROFILE = {
    "name": "张伟明",
    "phone": "138-0013-8000",
    "email": "zhangweiming@example.com",
    "city": "杭州",
    "education": [
        {"school": "演示大学", "major": "软件工程", "degree": "本科", "graduation_time": "2018"}
    ],
    "skills": ["Python"],
}


class SequenceClient:
    """按脚本依次返回的测试替身，并记录调用次数与重试 prompt。"""

    def __init__(self, responses: list[str]):
        self._responses = responses
        self.calls: list[str] = []

    def complete(self, system: str, user: str) -> str:
        self.calls.append(user)
        return self._responses.pop(0)


def _invoke_extract(cmd, runner, example_resume, monkeypatch, client):
    import resume_cli.cli as cli_module

    monkeypatch.setattr(cli_module, "_make_client", lambda mock: client)
    return runner.invoke(cmd, ["extract", str(example_resume)])


def test_retry_once_after_garbage_then_succeeds(cmd, runner, example_resume, monkeypatch):
    client = SequenceClient(["抱歉，我无法处理。", json.dumps(GOOD_PROFILE, ensure_ascii=False)])
    result = _invoke_extract(cmd, runner, example_resume, monkeypatch, client)
    assert result.exit_code == 0, visible_output(result)
    assert stdout_json(result)["name"] == "张伟明"
    assert len(client.calls) == 2  # 恰好重试一次
    assert "修正" in client.calls[1]  # 重试 prompt 携带修正要求


def test_retry_once_after_invalid_schema_then_succeeds(cmd, runner, example_resume, monkeypatch):
    bad = {"name": "张伟明"}  # 缺 education，校验失败
    client = SequenceClient([json.dumps(bad, ensure_ascii=False), json.dumps(GOOD_PROFILE, ensure_ascii=False)])
    result = _invoke_extract(cmd, runner, example_resume, monkeypatch, client)
    assert result.exit_code == 0, visible_output(result)
    assert len(client.calls) == 2
    assert "education" in client.calls[1]  # 校验错误被拼进重试 prompt


def test_fails_after_second_bad_output_with_raw_preview(cmd, runner, example_resume, monkeypatch):
    client = SequenceClient(["垃圾输出甲", "垃圾输出乙丙丁"])
    result = _invoke_extract(cmd, runner, example_resume, monkeypatch, client)
    assert result.exit_code == 1
    combined = visible_output(result)
    assert "两次" in combined
    assert "垃圾输出乙丙丁" in combined  # 保留最后一次原始响应摘要
    assert len(client.calls) == 2  # 不会第三次调用
