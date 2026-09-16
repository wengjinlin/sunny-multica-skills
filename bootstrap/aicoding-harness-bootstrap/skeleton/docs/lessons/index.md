# lessons — 项目经验库（持续学习层，按角色分文件）

> **结构**：本目录 = 本索引 + 每角色一个 md 文件（条目只写角色文件，**不在本索引维护条目或计数**，防索引漂移）。
>
> **机制**：Reviewer 打回 / Tester 测试踩坑 / DevOps 发布踩坑时追加条目；DevOps 归档 change 时把散落在 review-report / test-report 的条目合并进对应角色文件；同类错误第 2 次出现由 Reviewer 标注「建议晋升宪法」，经人类确认后写入 CLAUDE.md / REVIEW.md 红线并删除原条目。
>
> **条目格式**（必须含日期、来源 change-id、❌/✅ 对照动作；拒绝空话式教训）：
>
> - [YYYY-MM-DD] [change-id] 一句话标题
>   ❌ 错误做法（具体到命令/代码形态）
>   ✅ 正确做法（具体可执行）

## 角色索引

| 角色 | 文件 | 说明 |
|---|---|---|
| {{ROLE_INDEX_ROW}} | [{{ROLE_NAME}}.md]({{ROLE_NAME}}.md) | {{...}} |

<!-- 分析指引：角色文件与索引行按 Multica agent list 对齐（与 AGENTS.md §3 速查表同源）；每个角色文件从同目录 _template.md 复制生成。各角色读/写分区见 AGENTS.md §7 矩阵 -->
