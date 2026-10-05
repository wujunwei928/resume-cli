"""AI 返回 JSON 的解析：三层防线中的解析层。

剥 markdown 围栏 → 截取首尾花括号 → 严格反序列化 → json-repair 兜底修复
（尾逗号、单引号、注释、裸键等）。完全失败时抛出含原始摘要的错误。
"""

import json

from json_repair import repair_json

from .exceptions import JsonParseError

_MAX_PREVIEW = 200


def preview(raw: str, limit: int = _MAX_PREVIEW) -> str:
    """单行化并截断的原始响应摘要，供错误信息复用。"""
    return raw[:limit].replace("\n", " ")


def parse_model_json(raw: str) -> dict:
    """从 AI 原始输出中解析出 JSON 对象；失败时抛出含原始摘要的错误。"""
    text = _strip_code_fence(raw).strip()

    candidate = _slice_object(text)
    if candidate is None:
        raise JsonParseError(
            f"AI 返回内容中未找到 JSON 对象。原始内容：{_preview(raw)}"
        )

    data = _loads_strict(candidate)
    if data is None:
        data = _loads_repaired(candidate)
    if data is None:
        raise JsonParseError(
            f"AI 返回的 JSON 无法解析（已尝试自动修复）。原始内容：{_preview(raw)}"
        )

    if not isinstance(data, dict):
        raise JsonParseError(f"AI 返回的 JSON 不是对象。原始内容：{_preview(raw)}")
    return data


def _slice_object(text: str) -> str | None:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return text[start : end + 1]


def _loads_strict(candidate: str) -> object | None:
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def _loads_repaired(candidate: str) -> object | None:
    try:
        return repair_json(candidate, return_objects=True)
    except Exception:
        return None


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
    return preview(raw)
