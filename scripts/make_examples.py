"""生成 examples/ 下的合成示例文件（虚构人物，无隐私数据）。

用法：uv run python scripts/make_examples.py
依赖 reportlab（dev 组），中文使用内置 CID 字体 STSong-Light，无需系统字体文件。
"""

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"

RESUME_LINES = [
    ("张伟明", 20),
    ("电话：138-0013-8000 | 邮箱：zhangweiming@example.com | 城市：杭州", 11),
    ("", 6),
    ("教育经历", 14),
    ("杭州电子科技大学 · 软件工程 · 本科 · 2018 届", 11),
    ("", 6),
    ("技能", 14),
    ("Python / JavaScript / TypeScript / React / FastAPI / Docker / MySQL", 11),
    ("", 6),
    ("工作经历", 14),
    ("2022.03 - 至今  星河科技  全栈工程师", 11),
    ("  - 负责 SaaS 控制台前后端开发（React + FastAPI），服务 3 万+ 用户", 11),
    ("  - 设计并落地基于大模型 API 的智能工单分类服务，准确率 92%", 11),
    ("2018.07 - 2022.02  云洲软件  前端工程师", 11),
    ("  - 主导营销活动 H5 搭建平台前端架构，组件复用率提升 40%", 11),
    ("  - 搭建前端 CI 流水线与组件文档站", 11),
]


def build_resume(path: Path) -> None:
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y = height - 20 * mm
    for text, size in RESUME_LINES:
        if text:
            c.setFont("STSong-Light", size)
            c.drawString(18 * mm, y, text)
        y -= (size + 6) * 0.42 * mm
    c.save()


def main() -> None:
    EXAMPLES.mkdir(exist_ok=True)
    build_resume(EXAMPLES / "resume.pdf")
    print(f"已生成 {EXAMPLES / 'resume.pdf'}")


if __name__ == "__main__":
    main()
