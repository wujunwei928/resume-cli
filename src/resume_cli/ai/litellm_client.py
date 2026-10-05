"""litellm 真实实现：统一多提供商模型调用（ADR-0001）。"""

import logging
import os

os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")  # 跳过联网拉取价格表

import litellm

from ..exceptions import AICallError

litellm.suppress_debug_info = True  # 关闭 litellm 的版本打印等噪音
logging.getLogger("LiteLLM").setLevel(logging.ERROR)


class LiteLLMClient:
    def __init__(self, model: str, timeout: float = 60.0) -> None:
        self._model = model
        self._timeout = timeout

    def complete(self, system: str, user: str) -> str:
        try:
            # 尽力透传 JSON 模式；模型/网关不支持时去掉该参数降级重试
            response = self._completion(system, user, json_mode=True)
            return response.choices[0].message.content or ""
        except litellm.exceptions.BadRequestError:
            response = self._completion(system, user, json_mode=False)
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
        except litellm.exceptions.AuthenticationException as exc:
            raise AICallError(
                f"AI 调用失败：API Key 无效或未授权（模型 {self._model}）。\n"
                "请检查对应提供商的 Key 环境变量是否正确。"
            ) from exc
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
