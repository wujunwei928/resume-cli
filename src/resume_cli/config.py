"""配置集中读取：模型、超时与 API Key 存在性检测。"""

import os

DEFAULT_MODEL = "deepseek/deepseek-flash"

# litellm 认识的常见提供商 Key 变量；新增提供商时在此追加
KNOWN_KEY_VARS = (
    "DEEPSEEK_API_KEY",
    "ZHIPUAI_API_KEY",
    "OPENAI_API_KEY",
    "MOONSHOT_API_KEY",
    "ANTHROPIC_API_KEY",
    "OPENROUTER_API_KEY",
)


def resolve_model() -> str:
    """返回 litellm 风格的模型标识（provider/model）。"""
    return os.environ.get("RESUME_CLI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def resolve_timeout() -> float:
    try:
        return float(os.environ.get("RESUME_CLI_TIMEOUT", "60"))
    except ValueError:
        return 60.0


def detect_api_key() -> str | None:
    """返回第一个已配置的提供商 Key 变量名；都没有则返回 None。"""
    for var in KNOWN_KEY_VARS:
        if os.environ.get(var, "").strip():
            return var
    return None
