"""简历画像契约：AI 提取结果的字段校验（pydantic v2）。"""

from pydantic import BaseModel, Field


class Education(BaseModel):
    """一段教育经历。"""

    school: str
    major: str
    degree: str
    graduation_time: str


class Profile(BaseModel):
    """简历画像：extract 命令的输出契约。"""

    name: str
    phone: str | None = None
    email: str | None = None
    city: str | None = None
    education: list[Education]
    skills: list[str] = Field(default_factory=list)
