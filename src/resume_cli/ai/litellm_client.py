"""litellm 真实实现：统一多提供商模型调用（ADR-0001）。"""

import logging
import os

os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")  # 跳过联网拉取价格表

import litellm

from ..exceptions import AICallError

litellm.suppress_debug_info = True  # 关闭 litellm 的版本打印等噪音
logging.getLogger("LiteLLM").setLevel(logging.ERROR)


def _auth_error(model: str) -> AICallError:
    return AICallError(
        f"AI 调用失败：API Key 无效或未授权（模型 {model}）。\n"
        "请检查对应提供商的 Key 环境变量是否正确。"
    )


def _is_auth_error(exc: Exception) -> bool:
    """DeepSeek 的 401 错误体 code=invalid_request_error，会被 litellm 误映射成
    BadRequestError 而非 AuthenticationException；靠状态码或错误体标记补判。"""
    if getattr(exc, "status_code", None) in (401, 403):
        return True
    return "authentication_error" in str(exc)


class LiteLLMClient:
    def __init__(self, model: str, timeout: float) -> None:
        self._model = model
        self._timeout = timeout

    def complete(self, system: str, user: str) -> str:
        try:
            # 尽力透传 JSON 模式；模型/网关不支持时去掉该参数降级重试
            response = self._completion(system, user, json_mode=True)
            return response.choices[0].message.content or ""
        except litellm.exceptions.BadRequestError as exc:
            if _is_auth_error(exc):
                raise _auth_error(self._model) from exc
            try:
                response = self._completion(system, user, json_mode=False)
            except litellm.exceptions.BadRequestError as retry_exc:
                # 降级后仍 400：多为模型名/provider 写错或请求本身被拒，收敛为业务错误
                raise AICallError(
                    f"AI 调用失败：请求被提供商拒绝（模型 {self._model}）。\n"
                    "请检查 RESUME_CLI_MODEL 的 provider 前缀与模型名是否正确。\n"
                    f"原始错误：{retry_exc}"
                ) from retry_exc
            return response.choices[0].message.content or ""

    def _completion(self, system: str, user: str, json_mode: bool):
        kwargs = {}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        try:
            return litellm.completion(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                timeout=self._timeout,
                **kwargs,
            )
        except litellm.exceptions.BadRequestError:
            raise  # 交由上层 complete() 降级处理，勿包装成 AICallError
        except litellm.exceptions.AuthenticationException as exc:
            raise _auth_error(self._model) from exc
        except litellm.exceptions.RateLimitError as exc:
            raise AICallError(
                "AI 调用失败：已触发提供商限流，请稍后重试或更换模型。"
            ) from exc
        except litellm.exceptions.Timeout as exc:
            raise AICallError(
                f"AI 调用失败：请求超时（{self._timeout:.0f} 秒）。\n"
                "可通过环境变量 RESUME_CLI_TIMEOUT 调大超时。"
            ) from exc
        except Exception as exc:
            raise AICallError(
                f"AI 调用失败：网络或未知错误：{exc}"
            ) from exc
