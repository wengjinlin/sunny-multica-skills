# AGENTS.md — 协作总纲

---

## 0. 适用范围

本文件是所有 agent 在本仓库协作的总纲（角色职责字典、Git 策略、工件约定、变更联动）。宪法（红线）见 `CLAUDE.md`，审查关卡见 `REVIEW.md`。

---

## 1. 废弃产物隔离

{{DEPRECATED_ARTIFACTS}}

<!-- 分析指引：列出历史上废弃的编排器/产物路径（若有），声明「不写入、不读取、不复制」；全新仓库无废弃产物可写「（无）」 -->

---

## 2. stage 编号约定

默认链模板维护在**编排 agent（Mika）的工作区配置**中——它在创建 change issue 时把链写入 issue 描述；本仓库不维护链序（避免双源漂移）。

- issue 的 `stage` 字段编号 ↔ 主导 agent 的对照字典：见 §3 角色速查表。
- 单个 change 的实际流程**以其 issue 描述为唯一执行权威**（人工可定制增删阶段）；与任何文档不一致时按 issue 执行，不质疑不纠正。

---

## 3. 角色速查表

| Agent | 一句话职责 | 主导 stage | 模型 | 关键工具权限 |
|---|---|---|---|---|
| {{AGENT_ROW}} | {{...}} | {{...}} | {{...}} | {{...}} |

<!-- 分析指引：从 Multica 侧 agent-bootstrap 建立的角色对齐（multica agent list）；此表是仓库侧字典，变更须回写 -->

---

## 4. Git 策略（分支级权限）

- **开发分支**：每个 change 在 `feature/{change-id}` 上工作，所有 agent 的产物 commit 都打到这条分支
- **基线**：开工先 `git fetch origin`，基于最新 `origin/master` 创建 feature 分支；后续接力 checkout 已存在的 feature 分支
- **合并目标**：MR 目标是 `{{MR_TARGET_BRANCH}}`（不是 master）
- **保护分支**：`master` / `{{MR_TARGET_BRANCH}}` 禁止直推，只能经 MR 由人类合并
- 工件 commit 后**必须立即 push**——未 push 的本地分支在其他 runtime 拉不到，跨机协作会断链

---

## 5. OpenSpec 工件结构

```
openspec/changes/{change-id}/
├── proposal.md       # stage 1 产出（WHY + 边界）
├── specs.md          # stage 2 产出（WHAT）
├── design.md         # stage 2 产出（HOW）
└── tasks.md          # stage 3 产出（执行 + 排他文件清单）
```

- 每次产出工件后必须跑 `openspec validate <change-id>`
- 跨工件引用用相对路径（同 change-id 目录内），不用绝对 SHA

---

## 6. 变更联动（上游改动 → 下游义务）

| 触发 | 下游义务 | 执行方式 |
|---|---|---|
| PM 修改 proposal.md（已 in_review 之后） | Architect 必须 re-specs + re-design | PM 在原 issue 评论贴新版本 + @mention Architect；Mika 把下游所有 stage 子 issue 置 `blocked`，等重做后解锁 |
| Architect 修改 specs/design（已 in_review 之后） | Tech-Lead 必须 re-tasks | 同上，Architect @mention Tech-Lead + Mika 阻塞 stage≥3 子 issue |
| Architect 产出 ddl.sql（建表/加字段） | 人工在库上执行 DDL 后流程才可继续；受影响域数据库文档须在本 change 内重生成 | 人工执行后评论回执 @Mika；Mika 置 `ddl=executed` 并解锁 stage≥3（Developer 测试依赖表结构先存在）；Tech-Lead 的 tasks.md 必含「按 docs/database/index.md 再生成规则重生成受影响域表文档」task |
| Developer 实施时发现 design 漏字段 | 反向触发 Architect | Developer 不得擅自扩边界：task issue 评论 + status `blocked` + @mention Mika，由 Mika 决定是否回退 |

---

## 7. 持续学习层（docs/lessons/ 目录，按角色分文件）

- **开工必读**：各角色先读 `docs/lessons/index.md`（机制与条目格式），再读自己角色（及各自指令中指定）的 `docs/lessons/{角色}.md`，历史教训视同本级约束执行
- 条目只写入本角色文件（索引不维护条目）；条目含来源 change-id 与 ❌/✅ 对照动作
- 各角色读/写分区：

| 角色 | 读 | 写 |
|---|---|---|
| {{ROLE_LESSON_MATRIX}} | {{...}} | {{...}} |

<!-- 分析指引：角色文件与读写矩阵按 Multica agent list 对齐（与 §3 速查表同源，角色文件从 _template.md 复制生成）；升级规则：同一教训第 2 次出现由 Reviewer 标注晋升宪法，经人类确认写入 CLAUDE.md/REVIEW.md 并删除原条目 -->
