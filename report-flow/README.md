# report-flow — 报表开发专用简易流程（独立工作区）

针对**查询列表 + 导出**类报表开发任务的精简 AI 编码流程，**独立部署为报表专用工作区**（与通用链工作区并存，绑定同一业务仓库）。从现有 5-stage 通用链裁剪而来：**速度优先、准确率靠固定模板 + 静态审查 + 人工收口三重保障、对业务仓库零侵入**。

## 零侵入原则（本方案核心约束）

报表链对业务仓库的 harness 层写入**全部收敛到 `docs/report-flow/` 一个新增目录**（设计工件 / 权限 SQL / 审查报告 / 归档 / lessons / CHANGELOG 全在其中）；仓库已有文件（`CLAUDE.md` / `AGENTS.md` / `docs/*` / `openspec/` / hooks 等）**一律只读不改**——共用文档以 `docs/report-flow/constitution.md` 作为增量模块说明承载报表专用约定。原仓库上的通用链工作区不受任何影响，详见 `design.md` §9。

## 与现有流程对照（快在哪）

| 环节 | 现有通用链 | 报表链 |
|---|---|---|
| 设计 | PM 产 OpenSpec 四工件（proposal/specs/design/api）+ 逐件 validate | Report-PM 产**单工件 report-design.md**（一份含全部设计要素）+ auth-resource.sql |
| 人工审 | 四工件一次审 | 一份文档一次审 |
| 任务拆解 | Tech-Lead 拆 tasks.md + DAG + plan.md | **砍掉**——报表单一模块，Developer 按 report-design.md 直接实现 |
| 编码 | Developer 逐 task TDD + 每 task Reviewer 微循环 | Developer 一次实现全量（后端自测 + 前端组件复用）→ Reviewer **一次总审** |
| 测试 | Tester 跑集成/边界/浏览器 QA | **砍掉**——接口自测并入 Developer，页面验收并入 MR 阶段人工收口 |
| 发布 | DevOps 归档 + MR + 人工收口 | 不变（复用） |

角色 5+1 → **4+1**（Report-PM / Report-Developer / Report-Reviewer / Report-DevOps + Mika 编排复用，独立工作区单链路由）。

## 部署形态

**全新独立工作区**：优先跑 `report-workspace-bootstrap` 一键建区 skill（挂载给新工作区的 Mika 后说「建报表工作区」即走七步：拉 4 技能 → 建 4 agent → 人工 env 窗口 → 绑定同一业务仓库 → 报表版编排层 → `docs/report-flow/` 增量 harness 自动建 MR），也可按 `design.md` §10 分步手跑。回退方式见 `design.md` §10。

## skills 用量对照（省在哪）

| skill | 通用链 | 报表链 | 理由 |
|---|---|---|---|
| aicoding-lookup-ui-reference-v2/v3 | ✅ | ✅ 保留（PM 选型 / Developer 用法 / Reviewer 比对） | 报表组件正确用法是准确率核心 |
| aicoding-config-auth-resource-v2/v3 | ✅ | ✅ 保留（Report-PM） | 报表页面需挂菜单 + 按钮权限 |
| openspec-* 全系 | ✅ 6 个 | ❌ 全砍 | 单工件不走 OpenSpec 工件链 |
| superpowers:* 全系 | ✅ 5 个 | ❌ 全砍 | 无 plan.md 可执行；自测指令内嵌 Developer |
| aicoding-db-schema-export | ✅ | ❌ 砍 | 报表免 DDL，无文档再生成场景 |
| aicoding-browser-qa | ✅ | ❌ 砍 | 验收走 MR 阶段人工收口 |
| aicoding-harness-audit / human-test-retro | ✅ | ❌ 砍 | 周级 autopilot 事务，与单报表任务无关 |

每个 agent 挂载 skills：**最多 2 个**（lookup + config-auth，且只在需要的角色挂）。

## 文件清单

| 文件 | 作用 |
|---|---|
| `README.md` | 本文件：方案总览与对照 |
| `design.md` | 主设计文档：流程 / 角色 / 工件模板 / 人工门 / 编排对接 / 部署方式 |
| `agents/Report-PM.md` | 报表 PM agent 指令（可直接用于 aicoding-agent-bootstrap 创建） |
| `agents/Report-Developer.md` | 报表 Developer agent 指令 |
| `agents/Report-Reviewer.md` | 报表 Reviewer agent 指令 |
| `agents/Report-DevOps.md` | 报表 DevOps agent 指令 |
| `report-workspace-bootstrap/` | **一键建区 skill**（design.md §10 预留脚手架）：主 SKILL 编排七步 + 报表版 Mika 编排（`mika-instructions-report.md`）+ 巡检剧本（`autopilot-report.md`）+ 人工清单（`references/human-checklist.md`）+ 业务仓库 `docs/report-flow/` 骨架（`skeleton/`，§9.2 八文件） |
| `skills/` | 4 个共用业务 skill 的**自包含副本**（lookup-v2/v3、config-auth-v2/v3，拷贝自仓库 `skills/`，上游改动须同步）；报表工作区可通过 `.../tree/main/report-flow` 整目录拉取 |

## 适用边界

- **走本流程**：新报表页、报表加列/加查询条件、报表导出配置——查询现有库表 + query-list 类页面 + 既有导出通道，不建表不加字段。
- **不走本流程**（到通用链工作区发起）：涉建表/视图/加字段（有 DDL）、涉复杂业务流程编排（非查询展示类）、跨多模块大型变更、BUG 修复（走通用 C 类诊断）。

边界判定由 Report-PM 在澄清阶段做出：**判断不了或命中"不走"清单 → 明确建议到通用链工作区发起（澄清结论可复用）**，不勉强套报表链。
