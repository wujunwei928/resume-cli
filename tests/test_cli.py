"""CLI 接缝测试：从命令行边界断言行为（退出码 / stdout / stderr）。"""

from pathlib import Path

import pytest
from conftest import visible_output

from resume_cli.cli import app

USAGE_EXIT_CODE = 2  # typer/click 的用法错误退出码
BUSINESS_EXIT_CODE = 1


class TestHelp:
    def test_root_help_lists_parse(self, cmd, runner):
        result = runner.invoke(cmd, ["--help"])
        assert result.exit_code == 0
        assert "parse" in result.output

    def test_parse_help(self, cmd, runner):
        result = runner.invoke(cmd, ["parse", "--help"])
        assert result.exit_code == 0
        assert "PDF" in result.output

    @pytest.mark.parametrize("subcommand", [[], ["parse"], ["extract"], ["score"]])
    def test_short_help_equals_long_help(self, cmd, runner, subcommand):
        short = runner.invoke(cmd, [*subcommand, "-h"])
        long = runner.invoke(cmd, [*subcommand, "--help"])
        assert short.exit_code == 0
        assert short.output == long.output


class TestParse:
    def test_usage_error_without_args(self, cmd, runner):
        result = runner.invoke(cmd, ["parse"])
        assert result.exit_code == USAGE_EXIT_CODE

    def test_prints_resume_text(self, cmd, runner, example_resume):
        result = runner.invoke(cmd, ["parse", str(example_resume)])
        assert result.exit_code == 0
        assert "张伟明" in result.output
        assert "zhangweiming@example.com" in result.output

    def test_file_not_found(self, cmd, runner, tmp_path):
        result = runner.invoke(cmd, ["parse", str(tmp_path / "no_such.pdf")])
        assert result.exit_code == BUSINESS_EXIT_CODE
        assert "不存在" in visible_output(result)

    def test_not_a_pdf(self, cmd, runner, tmp_path):
        fake = tmp_path / "resume.pdf"
        fake.write_text("这不是 PDF，只是一个改了后缀的文本文件。", encoding="utf-8")
        result = runner.invoke(cmd, ["parse", str(fake)])
        assert result.exit_code == BUSINESS_EXIT_CODE
        assert "不是 PDF" in visible_output(result)

    def test_corrupted_pdf(self, cmd, runner, tmp_path):
        broken = tmp_path / "broken.pdf"
        broken.write_bytes(b"%PDF-1.7\n" + b"\x00\x01garbage" * 64)
        result = runner.invoke(cmd, ["parse", str(broken)])
        assert result.exit_code == BUSINESS_EXIT_CODE
        assert "无法读取" in visible_output(result)

    def test_empty_text_pdf(self, cmd, runner, tmp_path):
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        blank = tmp_path / "blank.pdf"
        c = canvas.Canvas(str(blank), pagesize=A4)  # 只建一页，不画任何文字
        c.showPage()
        c.save()

        result = runner.invoke(cmd, ["parse", str(blank)])
        assert result.exit_code == BUSINESS_EXIT_CODE
        assert "文本为空" in visible_output(result)

    def test_directory_path(self, cmd, runner, tmp_path):
        result = runner.invoke(cmd, ["parse", str(tmp_path)])
        assert result.exit_code == BUSINESS_EXIT_CODE
        assert "无法读取" in visible_output(result)


class TestMain:
    def test_keyboard_interrupt_exits_cleanly(self, monkeypatch):
        from resume_cli import cli as cli_module

        def interrupted():
            raise KeyboardInterrupt

        monkeypatch.setattr(cli_module, "app", interrupted)
        with pytest.raises(SystemExit) as exc_info:
            cli_module.main()
        assert exc_info.value.code == 130
