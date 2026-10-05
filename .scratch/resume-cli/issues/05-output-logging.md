# 05: --output 落盘 + 日志体系

**What to build:** `extract` / `score` 支持 `--output <file>` 将结果保存为缩进 JSON 文件。日志体系：标准库 logging，INFO 级在 stderr 输出关键节点（文件路径、页数、字符数、模型名、耗时、mock 标记），`--verbose` 升 DEBUG（含 prompt 摘要）；结果 JSON 只走 stdout，保证管道重定向纯净；关闭 litellm 自身的冗余 debug 输出。

**Blocked by:** 03（score 命令）

**Status:** ready-for-agent

- [ ] `--output result.json` 写入文件，内容与 stdout 输出一致（缩进 2），stderr 提示保存路径
- [ ] `resume-cli extract a.pdf > out.json` 重定向后 out.json 是纯 JSON，无日志混入
- [ ] 默认 INFO 日志覆盖：文件、页数、字符数、模型名、耗时、mock 标记
- [ ] `--verbose` 输出 DEBUG 级 prompt 摘要
- [ ] litellm 自身的 debug 输出默认不出现在终端
- [ ] --output 与日志分流的端到端测试（CliRunner + 临时目录）全绿
