"""json_utils 纯函数单测：脏 JSON 各形态的修复与拒绝。"""

import pytest

from resume_cli.exceptions import JsonParseError
from resume_cli.json_utils import parse_model_json

VALID = '{"name": "张伟明", "skills": ["Python"]}'


class TestCleanJson:
    def test_plain_object(self):
        assert parse_model_json(VALID)["name"] == "张伟明"

    def test_code_fence(self):
        assert parse_model_json(f"```json\n{VALID}\n```")["name"] == "张伟明"

    def test_surrounded_by_chatter(self):
        raw = f"好的，以下是提取结果：\n{VALID}\n希望对你有帮助。"
        assert parse_model_json(raw)["skills"] == ["Python"]


class TestRepairableJson:
    def test_trailing_comma(self):
        assert parse_model_json('{"name": "张伟明", "skills": ["Python",]}')["skills"] == [
            "Python"
        ]

    def test_single_quotes(self):
        assert parse_model_json("{'name': '张伟明', 'skills': []}")["name"] == "张伟明"

    def test_line_comment(self):
        raw = '{\n  // 姓名\n  "name": "张伟明", "skills": []\n}'
        assert parse_model_json(raw)["name"] == "张伟明"

    def test_unquoted_key(self):
        assert parse_model_json('{name: "张伟明", "skills": []}')["name"] == "张伟明"


class TestRejects:
    def test_no_json_at_all(self):
        with pytest.raises(JsonParseError) as exc_info:
            parse_model_json("抱歉，我无法处理该文档。")
        assert "无法处理该文档" in str(exc_info.value)

    def test_repaired_to_non_object(self):
        with pytest.raises(JsonParseError):
            parse_model_json("结果是：[1, 2, 3]")

    def test_error_keeps_original_preview(self):
        with pytest.raises(JsonParseError) as exc_info:
            parse_model_json("垃圾输出" * 100)
        assert "垃圾输出" in str(exc_info.value)
