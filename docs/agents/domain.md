# 领域文档

工程类 skill 在探索本仓库代码时，应按以下规则消费领域文档。

## 探索前先读这些

- 仓库根目录的 **`CONTEXT.md`**
- 仓库根目录的 **`CONTEXT-MAP.md`**（如存在）：它指向每个上下文各自的 `CONTEXT.md`，读取与当前主题相关的那些
- **`docs/adr/`**：阅读与你将要工作的区域相关的 ADR。多上下文仓库中，还要检查 `src/<context>/docs/adr/` 中的上下文级决策

如果这些文件不存在，**静默继续**。不要提示其缺失；也不要一开始就建议创建它们。`/domain-modeling` skill（经 `/grill-with-docs` 与 `/improve-codebase-architecture` 触达）会在术语或决策真正落定时惰性创建它们。

## 文件结构

本仓库为**单上下文（single-context）**布局：

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

## 使用词汇表中的术语

当你的输出涉及领域概念（issue 标题、重构提案、假设、测试名）时，使用 `CONTEXT.md` 中定义的术语，不要漂移到词汇表明确回避的同义词。

如果你需要的概念还不在词汇表中，这是一个信号：要么你在发明项目不用的语言（请重新考虑），要么存在真实缺口（记下来交给 `/domain-modeling`）。

## 标记 ADR 冲突

如果你的输出与现有 ADR 相矛盾，请显式指出，而不是静默覆盖：

> _与 ADR-0007（事件溯源订单）矛盾，但值得重新讨论，因为……_
