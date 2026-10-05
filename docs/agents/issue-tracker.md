# Issue 跟踪：本地 Markdown

本仓库的 issue 与规格说明以 Markdown 文件形式存放在 `.scratch/` 下。

## 约定

- 一个特性一个目录：`.scratch/<feature-slug>/`
- 规格说明为 `.scratch/<feature-slug>/spec.md`
- 实施 issue 按一单一文件放在 `.scratch/<feature-slug>/issues/<NN>-<slug>.md`，从 `01` 开始编号，绝不合并为单个 tickets 文件
- Triage 状态记录在 issue 文件顶部的 `Status:` 行（角色字符串见 `triage-labels.md`）
- 评论与讨论历史追加到文件底部的 `## Comments` 标题下

## 当 skill 说「发布到 issue tracker」

在 `.scratch/<feature-slug>/` 下新建文件（目录不存在则先创建）。

## 当 skill 说「获取相关工单」

按引用路径读取文件。用户通常会直接给出路径或 issue 编号。

## Wayfinding 操作

供 `/wayfinder` 使用。**map（地图）**是一个文件，每个 ticket 对应一个 **child（子）**文件。

- **Map**：`.scratch/<effort>/map.md`（正文为 Notes / Decisions-so-far / Fog）。
- **子工单**：`.scratch/<effort>/issues/NN-<slug>.md`，从 `01` 开始编号，正文写问题。`Type:` 行记录工单类型（`research`/`prototype`/`grilling`/`task`）；`Status:` 行记录 `claimed`/`resolved`。
- **阻塞关系**：文件顶部的 `Blocked by: NN, NN` 行。当其列出的每个文件都是 `resolved` 时，该工单解除阻塞。
- **前沿（Frontier）**：扫描 `.scratch/<effort>/issues/` 中开放、未阻塞、未认领的文件；编号最小者优先。
- **认领（Claim）**：开始任何工作前，先设 `Status: claimed` 并保存。
- **解决（Resolve）**：在 `## Answer` 标题下追加答案，设 `Status: resolved`，然后把上下文指针（要点 + 链接）追加到 `map.md` 的 Decisions-so-far 中。
