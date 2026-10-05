"""litellm 客户端 JSON 模式降级测试：不发生网络调用，只验证本项目的降级逻辑。"""

import litellm

from resume_cli.ai.litellm_client import LiteLLMClient


class _FakeChoice:
    class message:
        content = "ok"


class _FakeResponse:
    choices = [_FakeChoice()]


def test_bad_request_falls_back_without_json_mode(monkeypatch):
    """模型不支持 response_format 时应去掉该参数重试，而不是报错退出。"""
    calls = []

    def fake_completion(**kwargs):
        calls.append(kwargs)
        if "response_format" in kwargs:
            raise litellm.exceptions.BadRequestError(
                message="response_format is not supported",
                llm_provider="demo",
                model="demo/m",
            )
        return _FakeResponse()

    monkeypatch.setattr(litellm, "completion", fake_completion)
    client = LiteLLMClient(model="demo/m", timeout=1.0)

    assert client.complete("system", "user") == "ok"
    assert len(calls) == 2
    assert "response_format" in calls[0]
    assert "response_format" not in calls[1]


def test_json_mode_supported_calls_once(monkeypatch):
    """模型支持 response_format 时只调用一次，参数正常透传。"""
    calls = []

    def fake_completion(**kwargs):
        calls.append(kwargs)
        return _FakeResponse()

    monkeypatch.setattr(litellm, "completion", fake_completion)
    client = LiteLLMClient(model="demo/m", timeout=1.0)

    assert client.complete("system", "user") == "ok"
    assert len(calls) == 1
    assert calls[0]["response_format"] == {"type": "json_object"}
