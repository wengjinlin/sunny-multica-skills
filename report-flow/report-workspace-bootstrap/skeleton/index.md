# docs/report-flow — 报表专用工作区 harness 增量

本目录是**报表专用工作区**对业务仓库的全部 harness 层写入（唯一写面 B）：设计工件 / 权限 SQL / 审查报告 / 归档 / lessons / CHANGELOG 全在其中。仓库其他已有文件（`CLAUDE.md` / `AGENTS.md` / `docs/**` / `openspec/**` / hooks 等）一律只读不改——写面与禁改面声明见 [constitution.md](constitution.md)。

## 目录结构

| 路径 | 作用 |
|---|---|
| `constitution.md` | 报表宪法增量模块（定位 / 适用边界 / 写面声明 / 冲突裁决 / 项目事实登记） |
| `CHANGELOG.md` | 报表链独立发布台账（不动通用链 `docs/CHANGELOG.md`） |
| `templates/report-design-template.md` | 报表设计单工件模板（权威源） |
| `templates/issue-create-template.md` | Report-PM 建单模板（权威源） |
| `review-checklist.md` | Report-Reviewer 固定四关详单（权威源） |
| `lessons/` | 报表链持续学习（自持，不动通用链 `docs/lessons/`） |
| `database-snapshots/` | 表结构自用副本（见其 README 口径说明） |
| `changes/{change-id}/` | 在途 change 工件（report-design.md / auth-resource.sql / review-reports/） |
| `changes/archive/` | 已归档 change（Report-DevOps `git mv` 落此） |

## 与主 harness 的关系

- 项目事实（模块 / 技术栈 / 方言 / 编码规范）以仓库根 `CLAUDE.md` 为唯一权威源（若存在）；Git 策略 / MR 目标分支以 `AGENTS.md` §4 为准——均**只读引用**。
- 报表流程专用规则（适用边界 / 单工件制 / 零侵入写面 / 归档路径）以本目录 `constitution.md` 为准。
