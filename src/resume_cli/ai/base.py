"""AI 客户端接口：CLI 编排层只依赖此抽象，不感知具体实现。"""

from typing import Protocol


class AIClient(Protocol):
    def complete(self, system: str, user: str) -> str:
        """发送 system/user 两条消息，返回模型回复的原始文本。"""
        ...
