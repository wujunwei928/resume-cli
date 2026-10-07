"""PDF 简历文本提取：pdfplumber 封装与四类文件异常。"""

from dataclasses import dataclass
from pathlib import Path

import pdfplumber

from .exceptions import EmptyPdfTextError, NotAPdfError, PdfFileNotFoundError, PdfUnreadableError

_PDF_MAGIC = b"%PDF-"


@dataclass
class ExtractedText:
    """提取结果：纯文本与来源页数。"""

    text: str
    pages: int


def extract_text(path: Path) -> ExtractedText:
    """读取本地 PDF 简历，返回文本与页数。

    依次处理：文件不存在 → 非 PDF → 无法读取 → 文本为空。
    """
    path = Path(path)
    if not path.exists():
        raise PdfFileNotFoundError(f"文件不存在：{path}\n请检查路径是否正确。")

    try:
        with path.open("rb") as f:
            head = f.read(len(_PDF_MAGIC))
    except OSError as exc:  # 目录、无读取权限等文件系统层错误统一收敛
        raise PdfUnreadableError(
            f"PDF 无法读取：{path}\n路径可能是目录或无读取权限。原始错误：{exc}"
        ) from exc
    if head != _PDF_MAGIC:
        raise NotAPdfError(f"文件不是 PDF：{path}\n请提供 PDF 格式的简历文件。")

    try:
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
    except Exception as exc:  # pdfplumber 对损坏/加密文件的报错类型不统一，统一收敛
        raise PdfUnreadableError(
            f"PDF 无法读取：{path}\n文件可能已损坏或设有密码。原始错误：{exc}"
        ) from exc

    text = "\n".join(pages).strip()
    if not text:
        raise EmptyPdfTextError(
            f"PDF 文本为空：{path}\n该文件可能是不含文字层的扫描件，本工具暂不支持 OCR。"
        )
    return ExtractedText(text=text, pages=len(pages))
