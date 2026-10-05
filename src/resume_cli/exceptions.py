"""业务异常体系。

退出码约定：0 成功；2 用法错误（由 typer/click 产生）；1 业务错误（本模块各异常）。
"""


class ResumeCliError(Exception):
    """业务错误基类：消息面向用户，应为中文并附下一步建议。"""


class PdfFileNotFoundError(ResumeCliError):
    """简历文件不存在。"""


class NotAPdfError(ResumeCliError):
    """文件不是 PDF（魔数校验失败）。"""


class PdfUnreadableError(ResumeCliError):
    """PDF 损坏或加密，无法读取。"""


class EmptyPdfTextError(ResumeCliError):
    """PDF 可打开但提取不到文本（如纯扫描件）。"""


class ConfigurationError(ResumeCliError):
    """运行所需配置缺失（如 API Key 未配置）。"""


class AICallError(ResumeCliError):
    """AI 调用失败（网络 / 鉴权 / 限流 / 超时等）。"""


class JsonParseError(ResumeCliError):
    """AI 返回内容中无法解析出 JSON 对象。"""


class AIOutputInvalidError(ResumeCliError):
    """AI 两次输出（含一次带修正要求的重试）均未通过解析或校验。"""


class JdFileError(ResumeCliError):
    """JD 文件不存在或内容为空。"""
