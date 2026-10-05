"""结构化任务共用管线：调用 → 解析 → 校验 → 失败带错误重试一次。

extract 与 score 共用；两次输出均无效时抛出含最后一次原始响应摘要的错误。
"""

import logging

from pydantic import BaseModel, ValidationError

from ..exceptions import AIOutputInvalidError, JsonParseError
from ..json_utils import parse_model_json, preview
from .base import AIClient

log = logging.getLogger(__name__)

_RETRY_NOTE = "\n\n【上次输出的修正要求】\n你上一次的输出存在问题：{problem}\n请严格修正后，重新输出一个符合要求的 JSON 对象（只输出 JSON 本身）。"


def run_structured_task(client: AIClient, system: str, user: str, model_cls: type[BaseModel]):
    """执行一次结构化 AI 任务，返回 (校验后的模型实例, 最后一次原始响应)。"""
    log.debug("system prompt 摘要：%s", system[:120].replace("\n", " "))
    log.debug("user prompt 摘要：%s", user[:200].replace("\n", " "))
    raw = client.complete(system, user)
    try:
        return model_cls.model_validate(parse_model_json(raw)), raw
    except (JsonParseError, ValidationError) as first_problem:
        log.info("首次输出未通过校验，携带修正要求重试一次")
        raw = client.complete(system, user + _RETRY_NOTE.format(problem=_brief(first_problem)))
        try:
            return model_cls.model_validate(parse_model_json(raw)), raw
        except (JsonParseError, ValidationError) as second_problem:
            raise AIOutputInvalidError(
                f"AI 两次输出均未通过校验，已停止重试。\n"
                f"第一次问题：{_brief(first_problem)}\n"
                f"重试后问题：{_brief(second_problem)}\n"
                f"最后一次原始响应：{preview(raw)}"
            ) from second_problem


def _brief(problem: Exception) -> str:
    if isinstance(problem, JsonParseError):
        return str(problem)
    details = "; ".join(
        f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}"
        for e in problem.errors()[:3]
    )
    return f"字段校验失败：{details}"
