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
