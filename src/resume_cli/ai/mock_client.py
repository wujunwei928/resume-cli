"""Mock AI 客户端：--mock 模式的本地实现，零网络调用。

按输入文本的关键词启发式生成结果；姓名/电话/邮箱直接从文本中识别，
技能与城市取自词表命中，使演示输出贴近真实而不依赖 API 配额。
"""

import json
import re

SKILL_VOCAB = (
    "Python", "JavaScript", "TypeScript", "React", "Vue", "FastAPI",
    "Django", "Flask", "Go", "Java", "Docker", "Kubernetes",
    "MySQL", "PostgreSQL", "Redis", "Git", "Linux",
)
CITIES = ("北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", "西安", "苏州")

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_PHONE_RE = re.compile(r"1[3-9]\d[- ]?\d{4}[- ]?\d{4}")


def _body_text(prompt: str) -> str:
    """从 user prompt 中取出材料正文（跳过「…：」指令行）。"""
    parts = prompt.split("：\n\n", 1)
    return parts[1] if len(parts) == 2 else prompt


class MockClient:
    def complete(self, system: str, user: str) -> str:
        if "评分" in system or "匹配" in system:
            return self._score(user)
        return self._profile(user)

    def _profile(self, text: str) -> str:
        text = _body_text(text)
        payload = {
            "name": self._guess_name(text),
            "phone": (m.group() if (m := _PHONE_RE.search(text)) else None),
            "email": (m.group() if (m := _EMAIL_RE.search(text)) else None),
            "city": next((c for c in CITIES if c in text), None),
            "education": [
                {
                    "school": "演示大学",
                    "major": "计算机科学与技术",
                    "degree": "硕士" if "硕士" in text else "本科",
                    "graduation_time": "2020",
                }
            ],
            "skills": [s for s in SKILL_VOCAB if s.lower() in text.lower()] or ["Python"],
        }
        return json.dumps(payload, ensure_ascii=False)

    def _score(self, text: str) -> str:  # 工单 03 实现
        raise NotImplementedError

    @staticmethod
    def _guess_name(text: str) -> str:
        first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
        is_cjk_name = 2 <= len(first) <= 4 and not any(
            ch.isdigit() or ch.isascii() for ch in first
        )
        return first if is_cjk_name else "李演示"
