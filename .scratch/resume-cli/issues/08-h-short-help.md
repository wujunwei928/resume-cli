# 08: `-h` 短选项等价 `--help`

**What to build:** 根命令与全部子命令（`parse` / `extract` / `score`）支持 `-h` 作为 `--help` 的短选项，行为完全一致（帮助输出逐字节相同，退出码 0）。实现：`typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})`，app 级一处配置，click 的 Context 向子命令继承，无需逐命令重复声明。

**Status:** ready-for-agent

- [x] `resume-cli -h` 与 `resume-cli --help` 输出一致，退出码 0
- [x] `parse` / `extract` / `score` 子命令各自 `-h` 与 `--help` 输出一致，退出码 0
- [x] help 面板的 Options 区显示 `--help  -h` 提示（click 8.5 富文本格式）
- [x] CliRunner 参数化回归测试覆盖根命令与三个子命令，全绿
- [x] README「CLI 命令说明」小节同步 `-h` 简写说明
