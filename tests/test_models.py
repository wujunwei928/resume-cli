"""简历画像契约（pydantic）单测：接缝为模型校验行为本身。"""

import pytest
from pydantic import ValidationError

from resume_cli.models import Education, Profile

VALID_PROFILE = {
    "name": "张伟明",
    "phone": "138-0013-8000",
    "email": "zhangweiming@example.com",
    "city": "杭州",
    "education": [
        {
            "school": "杭州电子科技大学",
            "major": "软件工程",
            "degree": "本科",
            "graduation_time": "2018",
        }
    ],
    "skills": ["Python", "React"],
}


class TestProfile:
    def test_accepts_valid_payload(self):
        profile = Profile.model_validate(VALID_PROFILE)
        assert profile.name == "张伟明"
        assert profile.education[0].school == "杭州电子科技大学"

    def test_rejects_missing_name(self):
        payload = dict(VALID_PROFILE)
        del payload["name"]
        with pytest.raises(ValidationError):
            Profile.model_validate(payload)

    def test_rejects_missing_education_and_skills(self):
        payload = {"name": "张伟明"}
        with pytest.raises(ValidationError):
            Profile.model_validate(payload)

    def test_rejects_non_list_skills(self):
        payload = dict(VALID_PROFILE, skills="Python, React")
        with pytest.raises(ValidationError):
            Profile.model_validate(payload)

    def test_allows_empty_skill_list(self):
        payload = dict(VALID_PROFILE, skills=[])
        assert Profile.model_validate(payload).skills == []


class TestEducation:
    def test_rejects_missing_graduation_time(self):
        with pytest.raises(ValidationError):
            Education.model_validate(
                {"school": "演示大学", "major": "计算机", "degree": "本科"}
            )
