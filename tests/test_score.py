"""score 命令接缝测试：经 CLI 边界验证评分输出、契约校验与 JD 异常。"""

import json

from conftest import visible_output

from resume_cli.cli import app

SCORE_KEYS = (
    "overall_score",
    "skill_score",
    "experience_score",
    "education_score",
    "comment",
    "interview_questions",
)


def test_mock_score_outputs_result_json(runner, example_resume):
    jd = example_resume.parent / "jd.txt"
    result = runner.invoke(
        app, ["score", str(example_resume), "--jd", str(jd), "--mock"]
    )
    assert result.exit_code == 0, visible_output(result)
    data = json.loads(result.output)
    for key in SCORE_KEYS:
        assert key in data, f"缺少字段 {key}"
    for key in SCORE_KEYS[:4]:
        assert isinstance(data[key], int) and 0 <= data[key] <= 100
    assert data["comment"].strip()
    assert isinstance(data["interview_questions"], list) and data["interview_questions"]
    assert data["mock"] is True


def test_score_rejects_out_of_range_from_ai(runner, example_resume, monkeypatch):
    class OutOfRangeClient:
        def complete(self, system: str, user: str) -> str:
            return json.dumps(
                {
                    "overall_score": 120,
                    "skill_score": 88,
                    "experience_score": 80,
                    "education_score": 75,
                    "comment": "分数越界的返回应被拦截。",
                    "interview_questions": ["问题一"],
                },
                ensure_ascii=False,
            )

    import resume_cli.cli as cli_module

    monkeypatch.setattr(cli_module, "_make_client", lambda mock: OutOfRangeClient())
    jd = example_resume.parent / "jd.txt"
    result = runner.invoke(app, ["score", str(example_resume), "--jd", str(jd)])
    assert result.exit_code == 1
    assert "校验" in visible_output(result)


def test_jd_file_not_found(runner, example_resume, tmp_path):
    result = runner.invoke(
        app, ["score", str(example_resume), "--jd", str(tmp_path / "no_jd.txt"), "--mock"]
    )
    assert result.exit_code == 1
    assert "不存在" in visible_output(result)


def test_jd_file_empty(runner, example_resume, tmp_path):
    empty_jd = tmp_path / "empty.txt"
    empty_jd.write_text("", encoding="utf-8")
    result = runner.invoke(
        app, ["score", str(example_resume), "--jd", str(empty_jd), "--mock"]
    )
    assert result.exit_code == 1
    assert "为空" in visible_output(result)
