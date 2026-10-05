"""AI 返回 JSON 的解析（简版）。

本阶段：剥 markdown 围栏 → 截取首尾花括号 → 直接反序列化。
完整三层防线（json-repair 兜底 + 校验重试）见工单 04。
"""

import json

from .exceptions import JsonParseError

_MAX_PREVIEW = 200


def parse_model_json(raw: str) -> dict:
    """从 AI 原始输出中解析出 JSON 对象；失败时抛出含原始摘要的错误。"""
    text = _strip_code_fence(raw).strip()

    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise JsonParseError(
            f"AI 返回内容中未找到 JSON 对象。原始内容：{_preview(raw)}"
        )

    candidate = text[start : end + 1]
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise JsonParseError(
            f"AI 返回的 JSON 无法解析：{exc}。原始内容：{_preview(raw)}"
        ) from exc

    if not isinstance(data, dict):
        raise JsonParseError(f"AI 返回的 JSON 不是对象。原始内容：{_preview(raw)}")
    return data


def _strip_code_fence(raw: str) -> str:
    text = raw.strip()
    if not text.startswith("```"):
        return text
    # 去掉 ```json 首行与末尾 ```
    if "\n" in text:
        text = text.split("\n", 1)[1]
    if text.rstrip().endswith("```"):
        text = text.rstrip()[:-3]
    return text


def _preview(raw: str) -> str:
    return raw[:_MAX_PREVIEW].replace("\n", " ")
