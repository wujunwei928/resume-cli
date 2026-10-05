"""--output 落盘与日志体系接缝测试。"""

import json

from conftest import stdout_json, visible_output


class TestOutputFile:
    def test_extract_output_writes_same_json(self, cmd, runner, example_resume, tmp_path):
        out = tmp_path / "result.json"
        result = runner.invoke(
            cmd,
            ["extract", str(example_resume), "--mock", "--output", str(out)],
        )
        assert result.exit_code == 0, visible_output(result)
        assert out.exists()
        assert json.loads(out.read_text(encoding="utf-8")) == stdout_json(result)
        assert "已保存" in visible_output(result)

    def test_score_output_writes_same_json(self, cmd, runner, example_resume, tmp_path):
        out = tmp_path / "score.json"
        jd = example_resume.parent / "jd.txt"
        result = runner.invoke(
            cmd,
            ["score", str(example_resume), "--jd", str(jd), "--mock", "--output", str(out)],
        )
        assert result.exit_code == 0, visible_output(result)
        assert json.loads(out.read_text(encoding="utf-8")) == stdout_json(result)

    def test_output_to_unwritable_path_fails(self, cmd, runner, example_resume, tmp_path):
        bad = tmp_path / "no_such_dir" / "result.json"
        result = runner.invoke(
            cmd, ["extract", str(example_resume), "--mock", "--output", str(bad)]
        )
        assert result.exit_code == 1
        assert "写入" in visible_output(result) or "保存" in visible_output(result)


class TestLogging:
    def test_real_stdout_redirect_is_pure_json(self, cmd, example_resume, tmp_path):
        """真实子进程 + 重定向：stdout 文件必须只含 JSON（管道纯净的产品级验证）。"""
        import subprocess
        import sys

        out = tmp_path / "redirected.json"
        with out.open("w", encoding="utf-8") as fh:
            subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "from resume_cli.cli import app; app()",
                    "extract",
                    str(example_resume),
                    "--mock",
                ],
                stdout=fh,
                stderr=subprocess.DEVNULL,
                check=True,
            )
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["name"] == "张伟明"

    def test_info_logs_on_stderr(self, cmd, runner, example_resume):
        result = runner.invoke(cmd, ["extract", str(example_resume), "--mock"])
        stderr = result.stderr or ""
        assert "页" in stderr and "字符" in stderr
        assert "Mock" in stderr or "mock" in stderr

    def test_parse_info_logs_pages_and_chars(self, cmd, runner, example_resume):
        result = runner.invoke(cmd, ["parse", str(example_resume)])
        assert "页" in result.stderr or ""

    def test_verbose_enables_debug_prompt_preview(self, cmd, runner, example_resume):
        result = runner.invoke(
            cmd, ["--verbose", "extract", str(example_resume), "--mock"]
        )
        assert result.exit_code == 0
        assert "DEBUG" in result.stderr
