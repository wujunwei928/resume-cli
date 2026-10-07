"""litellm 客户端 JSON 模式降级测试：不发生网络调用，只验证本项目的降级逻辑。"""

import litellm
import pytest

from resume_cli.ai.litellm_client import LiteLLMClient
from resume_cli.exceptions import AICallError


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


def test_misclassified_auth_error_does_not_fall_back(monkeypatch):
    """DeepSeek 的 401 错误体 code=invalid_request_error，会被 litellm 误映射为
    BadRequestError；此时应报鉴权错误而不是误判成 JSON 模式不支持去降级重试。"""
    calls = []

    def fake_completion(**kwargs):
        calls.append(kwargs)
        raise litellm.exceptions.BadRequestError(
            message='DeepseekException - {"error":{"message":"Authentication Fails,'
            ' Your api key: ****ecfc is invalid","type":"authentication_error",'
            '"param":null,"code":"invalid_request_error"}}',
            llm_provider="deepseek",
            model="deepseek/deepseek-flash",
        )

    monkeypatch.setattr(litellm, "completion", fake_completion)
    client = LiteLLMClient(model="deepseek/deepseek-flash", timeout=1.0)

    with pytest.raises(AICallError, match="API Key 无效"):
        client.complete("system", "user")
    assert len(calls) == 1  # 鉴权失败不应再发起无意义的降级重试


def test_fallback_retry_failure_wrapped_as_ai_call_error(monkeypatch):
    """降级重试仍抛非鉴权 BadRequestError（模型名/provider 写错、上下文超长等
    400 类错误）时，应收敛为 AICallError 而不是裸 traceback。"""
    calls = []

    def fake_completion(**kwargs):
        calls.append(kwargs)
        raise litellm.exceptions.BadRequestError(
            message="LLM Provider NOT provided. Pass in the LLM provider you are trying to call.",
            llm_provider="foo",
            model="foo/bar",
        )

    monkeypatch.setattr(litellm, "completion", fake_completion)
    client = LiteLLMClient(model="foo/bar", timeout=1.0)

    with pytest.raises(AICallError, match="RESUME_CLI_MODEL"):
        client.complete("system", "user")
    assert len(calls) == 2  # 先 JSON 模式、后降级重试，各一次
