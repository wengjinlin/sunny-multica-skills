# 报表开发简易流程 — 主设计文档

> 版本：v2（2026-11-11）｜权威源：本文件。agent 指令（agents/ 目录）与本文流程描述不一致时，以编排层 stage 链模板（§7）为基准双处同改。
>
> v2 变更：部署形态从「同工作区新增 agent」升级为**独立工作区**；新增 §9 报表 harness 仓库增量建设（对原仓库零侵入）；工件与 lessons 归属全部收敛到 `docs/report-flow/`。

## 1. 目标与设计原则

针对「查询列表 + 既有导出通道」类报表任务，从通用 5-stage 链裁剪出最快路径，并**独立部署为报表专用工作区**。

1. **快**：单工件设计、砍任务拆解层、砍独立测试 stage、一次总审代替逐 task 微循环。
2. **准**：不靠流程多而靠**输入质量**——报表设计模板四张封闭表、组件选型默认命中（query-list + useExport，免三层选型）、Reviewer 固定四关对照审查、MR 阶段人工收口三查。
3. **省**：每 agent 挂载 skills ≤2；不用的能力（OpenSpec 工件链、superpowers、DDL、browser QA）一律不挂。
4. **零侵入**（v2 新增）：报表链对业务仓库的 harness 层写入**全部收敛到 `docs/report-flow/` 一个新增目录**；仓库已有文件（含 CLAUDE.md / AGENTS.md / docs/* / openspec/ / hooks）一律只读不改。原仓库上的通用链工作区不受任何影响。

## 2. 适用边界（判定即分流）

**走报表链**：
- 新报表页面（查询现有表/视图 → 列表展示 → 导出）
- 存量报表加查询条件 / 加列 / 改导出配置
- 报表菜单与按钮权限注册

**不走（建议到通用链工作区发起）**：
- 涉建表 / 视图 / 加字段 / 加索引（有 DDL）
- 非查询展示类（业务流程编排、表单提交类页面）
- 跨多模块大型变更
- BUG 修复

**判定责任**：Report-PM 澄清阶段判定；判不了或命中"不走"清单 → chat 结论中明确建议**到通用链工作区发起**（跨工作区分流，见 §12）并停住。

## 3. 流程总览

```
chat 澄清（Report-PM，业务+技术双向）
  → 用户确认 → Report-PM 建 report change issue（Mika 守门）
  → stage 1  Report-PM：report-design.md + auth-resource.sql
  → 【人工门：人审一份设计 + 执行 auth-resource.sql + 权限绑定】
  → stage 2  Report-Developer：后端接口+自测 → 前端 api/层+query-list 页面 → 完成信号
  → Report-Reviewer 一次总审（对照 report-design.md 固定四关）
      通过 @Mika → stage 3；打回 → 返工重走审查
  → stage 3  Report-DevOps：归档 + CHANGELOG + GitLab API 建 MR + 人工收口指引
  → 发起人 MR 阶段人工验收（查询/导出/权限三查）→ 合并 → 主 issue 自动关闭
```

- 本工作区为**报表专用独立工作区**：Mika 只路由报表链，不存在双链并存路由。
- Mika 编排机制完全复用（编排信号 / 守门 / metadata / 30 分钟兜底巡检），仅 stage 链内容为报表链版本（§7 模板写入 issue 描述——**issue 描述是唯一执行权威**）。
- Reviewer 是嵌在 stage 2 内的横向关卡：Developer 完成信号 ≠ 推进，必须过总审。

## 4. 角色设计（4 agent，独立工作区专用实例）

4 个报表专用 agent（`Report-*`）+ Mika（编排）。与通用工作区的同名角色完全隔离（不同工作区不同实例）。

### 4.1 Report-PM（澄清 + 单工件设计）

- 入口同通用 PM：chat 澄清（explore 姿态）→ 确认后建单；issue 执行（stage 1）。
- 澄清重点（报表四要素）：**数据来源**（哪些表/域，查表结构见 §9.4 口径）、**查询条件**（字段/是否必填/默认值）、**列清单**（列名/来源字段/格式/汇总行）、**权限挂载点**（菜单挂在哪、按钮编码）。
- 技术栈判定（第零步，沿用通用机制）：按 CLAUDE.md §2 模块表判 Vue2/Vue3 → Vue2 用 lookup-v2 + config-auth-v2，Vue3 用 lookup-v3 + config-auth-v3；结论写进 report-design.md 开头。
- 组件选型**默认命中**：查询列表 = query-list 模板（Vue2 系官方代码生成器 queryList / Vue3 系 query-list 页面模板），导出 = 模板自带 useExport / exportDialog——**无需三层选型**；仅当需求含弹窗选实体等附加场景时按 lookup skill 归类补查。
- 产出两件（路径见 §9.2）：`docs/report-flow/changes/{change-id}/report-design.md`（§5 模板）+ `docs/report-flow/changes/{change-id}/auth-resource.sql`（走第零步选定的 config-auth skill 生成）。**不使用任何 openspec skill 与 CLI**。
- 不产 ddl.sql；澄清中发现需建表/加字段 → 触发 §2 分流。

### 4.2 Report-Developer（一次实现全量）

- 无 plan.md / tasks.md：以 report-design.md 为唯一实现依据，按固定顺序实现：
  1. 后端：查询接口（含分页、查询条件映射、导出接口复用既有通道）
  2. **接口自测**（内嵌，代替 Tester 的接口部分）：curl 实测——响应结构符合契约、分页字段齐全、典型条件命中预期列、空结果不报错；结果贴完成评论
  3. 前端：`api/` 层函数（按 report-design.md 接口契约，前后端锚点）→ query-list 页面（组件用法按 lookup skill，选型已定**禁止更换**）
  4. 自勾：report-design.md 末尾"实现状态"节标注完成项
- commit + push（原子性，message 引用 change-id）→ 完成信号 @Mika。
- 前后端在同一仓库则一个 Developer 一口气完成（报表体量小，无需多实例并行）；前后端分仓则建两个 task 子 issue 由 Mika 分别点火（排他边界 = 仓库边界）。

### 4.3 Report-Reviewer（一次总审，固定四关）

只读审查，对照 report-design.md 固定四关（不做通用链 4/10 关路由判断，报表恒走 quick）：

| 关 | 审什么 | 打回条件 |
|---|---|---|
| ① 接口契约关 | method/path/入参/响应结构/分页字段 ↔ report-design.md 接口契约逐项比对 | 任何偏离 |
| ② 查询条件与列关 | 页面查询区字段 ↔ 设计查询条件表；列表列 ↔ 设计列清单（名称/格式/顺序） | 漏项、错位、擅自增删 |
| ③ 组件与权限关 | 页面结构符合 query-list 模板用法（lookup skill 为准）；菜单/按钮权限编码 ↔ auth-resource.sql 一致 | 枚举外选型未声明；编码不一致 |
| ④ 安全与规范关 | SQL 无注入（参数化）、无 select *、深分页、软删除/数据权限过滤符合宪法；命名/分层符合 CLAUDE.md | 任何红线 |

- 产出 `docs/report-flow/changes/{change-id}/review-reports/review-report.md` → 通过 @Mika 进 stage 3 / 打回置 in_progress @原 Developer。
- 连续 2 次打回 → 评论升级人类（同通用机制）。

### 4.4 Report-DevOps（归档 + MR + 收口）

- 精简发布链：归档（`docs/report-flow/changes/{change-id}/` 移入 `docs/report-flow/changes/archive/`，纯目录移动，不跑 openspec CLI）→ 报表 CHANGELOG 条目（`docs/report-flow/CHANGELOG.md`，**不动通用链的 `docs/CHANGELOG.md`**）→ lesson 批量落盘（如有）→ tag → GitLab API 建 MR（JSON body，禁 form 编码）→ 完成评论附**报表人工收口指引**（§8）。
- 等人工合并；合并后主 issue 自动关闭。

## 5. 核心工件：report-design.md 模板

> 模板的权威源落仓库为 `docs/report-flow/templates/report-design-template.md`（§9.2）；本节为设计基准。

```markdown
# 报表设计：{报表名}（{change-id}）

## 技术栈判定
{Vue2 / Vue3，依据 CLAUDE.md §2 模块表；后续组件/权限 skill 以此为准}

## 报表定位
{业务用途 / 使用者 / 使用频率}

## 数据来源
{表/视图清单（表名 + 关联关系 + 关键过滤条件）；表结构依据（见 §9.4 口径）}

## 查询条件表（封闭：逐字段一行）
| 字段 | 来源列 | 组件 | 必填 | 默认值 |
|---|---|---|---|---|

## 列清单（封闭：逐列一行）
| 列名 | 来源字段 | 格式(日期/金额/枚举) | 排序 | 汇总行 |

## 导出
{走既有通道：query-list 模板自带导出 / exportDialog；导出文件名列清单全量}

## 接口契约
- {method} {path}（权限编码：{code}）
  - 入参：{分页 + 查询条件映射}
  - 响应：{统一 Result<?>，记录结构 = 列清单，分页字段}
- {导出接口如有，注明复用通道}

## 权限资源
{菜单挂载路径 + 按钮编码清单 → auth-resource.sql（第零步选定的 config-auth skill 生成）}

## 侵入面清单
{要改的现有文件逐个列出（老报表改造时必填；新报表为新建文件清单）}

## 偏离声明
{默认模板未覆盖 / 枚举外组件 / 需人审确认的决策，逐条列；无则写"无"}

## 验收点
{可核验清单：查询条件组合 / 列数据正确性 / 导出可用 / 菜单按钮可见}

## 实现状态（Developer 自勾区）
- [ ] 后端接口 + 自测
- [ ] 前端 api/ 层
- [ ] query-list 页面
```

设计质量规则：
- 四张封闭表（查询条件/列/接口/权限）**字段齐全才算设计完成**——PM 完成评论须自查四表无空行。
- 偏离声明是唯一需要人重点审的段落（其余是结构化事实），让人审聚焦。

## 6. 人工门（一次审 + 权限就绪）

门的定义（写入 issue 描述，审核人照做）：

1. 审 `report-design.md`（一份文档；重点偏离声明段）
2. 通过 → 评论「人审通过」+ @Mika；打回 → 评论意见 + @Mika（Mika 路由回 Report-PM 返工，阻塞 stage 2）
3. 在库上执行 `auth-resource.sql` + 权限系统 UI 将菜单/按钮绑定到测试账号所属角色 → 评论「权限已就绪」+ @Mika（只置 metadata 不阻塞 stage 2——Developer 开发不依赖权限，人工验收才依赖）

metadata 键沿用通用机制：`spec_review` / `role_bind`（无 `ddl` 键——报表免 DDL）。

## 7. 编排对接（独立工作区单链版）

本工作区 Mika 只路由报表链。复用编排层全部机制（编排信号 / 守门五要素 / metadata / 人工门协议 / 30 分钟兜底巡检），差异仅两点：

1. **stage 链文本**为报表链版本（下方建单模板）；
2. **角色名**全部为 Report-*（守门点名 Report-PM，微循环点名 Report-Reviewer）。

建单模板（Report-PM chat 确认后建单时照填，五要素缺一不可）：

```markdown
### change-id
{change-id}

### 澄清结论（chat）
{决策表 / 数据来源 / 查询条件·列·权限要点——执行时直接采信，不再反问}

### stage 链（报表链）
1 Report-PM:report-design.md+auth-resource.sql →【人工门：人审（一份设计）+ 权限就绪（执行 SQL + UI 绑定）】
→ 2 Report-Developer:前后端代码+接口自测 → Report-Reviewer 总审（四关）
→ 3 Report-DevOps:归档+MR+人工收口

### 人工门
stage 1 完成后你需要：
1. 审 docs/report-flow/changes/{change-id}/report-design.md
2. 通过 → 评论「人审通过」+ @Mika；打回 → 评论意见 + @Mika
3. 执行 auth-resource.sql + 权限系统 UI 绑定菜单/按钮到测试账号所属角色 → 评论「权限已就绪」+ @Mika

### 验收点
{从澄清结论提炼}
```

Mika 工作区补充（`mika-instructions.md` 报表版）要点：编排接力入口 / 建单守门五要素 / 报表链基准（与建单模板同源，权威源在编排层）/ Reviewer 总审微循环（Developer 完成信号 → 点名 Report-Reviewer；通过 @Mika 进 stage 3；打回不路由等返工）/ 人工门协议（spec_review + role_bind 两键，无 ddl）。文本可直接由通用版裁剪而来。

## 8. 人工收口指引（DevOps 完成评论附录，报表版）

```
【人工收口指引（报表）】
1. 拉分支本地跑起前后端：git fetch origin && git checkout feature/{change-id}
2. 报表三查：
   ① 用测试账号登录 → 菜单可见、页面能开
   ② 各查询条件组合 → 数据正确（与库/源报表抽查比对 2-3 组）
   ③ 导出 → 文件可下载、列与页面一致
3. 全部通过 → 合并 MR（主 issue 自动关闭）；有问题 → 本地改后 push 本分支，重大问题评论 @Mika 路由返工
```

## 9. 报表 harness 仓库增量建设（v2 核心：对原仓库零侵入）

### 9.1 总原则：写面收敛

报表链对业务仓库的**全部 harness 层写入收敛到 `docs/report-flow/` 一个新增目录**。写面 / 禁改面：

| 类别 | 范围 | 规则 |
|---|---|---|
| ✅ 写面 A：业务代码 | `src/` 等业务代码（新增页面/接口） | 任务本身，照常开发，经 MR 合并 |
| ✅ 写面 B：harness 增量 | `docs/report-flow/**`（新增目录） | 报表链全部工件 / 文档 / 归档 / lessons 只写这里 |
| ❌ 禁改面 | 仓库其他一切已有文件与目录：`CLAUDE.md`、`AGENTS.md`、`REVIEW.md`、`docs/architecture/**`、`docs/database/**`、`docs/CHANGELOG.md`、`docs/lessons/**`、`docs/templates/**`、`openspec/**`、`.claude/**`（hooks）、`.gitlab-ci*` 等一切配置 | **一律只读**：可引用其内容作为权威源，但禁止修改、禁止 append、禁止 rename |

- 零侵入的动机：同一个业务仓库可能同时挂着通用链工作区（其 harness-audit / lessons / CHANGELOG / hooks 都在运行），报表工作区任何对这些文件的写入都会造成两条链互相踩踏。物理目录隔离 = 天然互不干扰。
- 取舍说明：报表工作区**不安装任何 git hooks**（不动 `.claude/` 等已有配置）——工具白名单与禁改面靠 agent 指令约束 + Reviewer 第④关核查。若原仓库已有通用链 hooks 且保护目录清单与报表写面兼容，则被动受益，不主动改。

### 9.2 增量目录结构

```
docs/report-flow/                        # 报表链 harness 全部增量（唯一写面 B）
├── index.md                             # 入口导览：本目录结构 + 与主 harness（CLAUDE.md 等）的关系声明
├── constitution.md                      # 报表宪法增量（模块说明，见 9.3）
├── CHANGELOG.md                         # 报表链独立发布台账（不动通用 docs/CHANGELOG.md）
├── templates/
│   ├── report-design-template.md        # §5 模板的仓库权威源
│   └── issue-create-template.md         # §7 建单模板的仓库权威源
├── review-checklist.md                  # Reviewer 四关详单的仓库权威源
├── lessons/                             # 报表链持续学习（不动通用 docs/lessons/）
│   ├── index.md
│   └── {Report-PM|Report-Developer|Report-Reviewer|Report-DevOps}.md
├── database-snapshots/                  # 表结构自用副本（见 9.4）
│   └── <域>.md
└── changes/
    ├── {change-id}/                     # 在途 change 工件
    │   ├── report-design.md
    │   ├── auth-resource.sql
    │   └── review-reports/review-report.md
    └── archive/                         # 已归档 change（DevOps git mv 落此）
```

### 9.3 共用文档的处理：constitution.md 模块说明

仓库根级共用文档（`CLAUDE.md` / `AGENTS.md` / `REVIEW.md`）**一个字都不改**，处理规则：

1. **仍作为权威源被读**：报表 agent 开工必读仓库根 `CLAUDE.md`（若存在）——项目事实（模块/技术栈/方言/编码规范）以它为唯一权威源；Git 策略 / MR 目标分支以 `AGENTS.md` §4 为准。通用链 harness 文档（`docs/architecture/`、`docs/database/`、`REVIEW.md` 等，若存在）同样**只读引用**。
2. **报表专用约定以 `docs/report-flow/constitution.md` 为准**，它是对主宪法的**增量模块说明**，内容固定四节：
   - 「定位」：本目录是报表专用工作区的 harness 增量；与主宪法的关系 = 主宪法管项目事实，本模块只补报表链专用规则（适用边界 / 单工件制 / 零侵入写面 / 归档路径）。
   - 「适用边界」：§2 清单原文。
   - 「写面声明」：§9.1 写面/禁改面表原文。
   - 「冲突裁决」：本模块与主宪法冲突时，项目事实类（技术栈/方言/规范）以主宪法为准，流程类（工件/路径/审查方式）以本模块为准。
3. agent 指令侧落实：4 个 Report agent 的「项目上下文」节均写明"先读 `CLAUDE.md`（若存在，只读权威源）再读 `docs/report-flow/constitution.md`（报表流程权威源）"。
4. 仓库**尚无**任何 harness（无 CLAUDE.md）时的降级：constitution.md 增设「项目事实登记」节承载最小事实（模块清单/技术栈/构建命令/数据库方言），由建区时人工问答填充——报表工作区自持，不为通用链代言。

### 9.4 表结构查阅口径（不动 docs/database/）

| 情况 | 口径 |
|---|---|
| 原仓库已有 `docs/database/`（通用链生成） | **只读引用**，照常查 `tables/<域>.md` |
| 原仓库没有 | Report-PM 澄清时向用户索取表结构；高频用表由 PM 将 DDL/字段说明整理为快照写入 `docs/report-flow/database-snapshots/<域>.md`（**报表自用副本，只增不改原仓库**，来源与日期注明）；需要系统性全量导出时建议用户在通用链工作区跑 `aicoding-db-schema-export`（那是它的唯一生成通道，产物落 `docs/database/` 由通用链 MR 入库，报表链只读受益） |

### 9.5 与原仓库通用 harness 的互不干扰核对

| 通用链机制 | 报表链影响 | 隔离方式 |
|---|---|---|
| `aicoding-harness-audit` 周级对账扫描固定文档路径 | 不会扫到 `docs/report-flow/` | 目录隔离，audit 清单不含它 |
| 通用 `docs/lessons/` 读写 | 报表链不读不写 | 报表自持 `docs/report-flow/lessons/` |
| 通用 `docs/CHANGELOG.md` | 报表链不写 | 报表自持 `docs/report-flow/CHANGELOG.md` |
| guard hooks（若已装） | 报表链不装不改 | 被动兼容：hooks 只拦保护目录，`docs/report-flow/` 与业务代码不在保护清单 |
| openspec 目录 | 报表链不使用 | 工件走 `docs/report-flow/changes/` |
| 分支/MR | 共用 `feature/{change-id}` 命名与 MR 流程 | 无冲突：MR 是仓库原生机制，报表 MR 的 description 含 `Closes` 关报表工作区自己的 issue |

## 10. 部署方式（独立工作区）

**推荐：全新独立工作区**（与通用链工作区并存，绑定同一业务仓库），基于现有 bootstrap 分步裁剪：

| 步骤 | 用什么 | 裁剪点 |
|---|---|---|
| 1. skills 拉取 | `aicoding-skills-bootstrap` | 只拉 4 个：lookup-v2/v3、config-auth-v2/v3；superpowers / openspec 系不拉 |
| 2. agent 创建 | `aicoding-agent-bootstrap` | 只建 5 个：4 个 `Report-*`（用 `report-flow/agents/` 配置）+ Mika；通用 6 角色不建 |
| 3. Mika 编排补充 | 手工贴入 §7 报表版要点 | 单链版 mika-instructions（裁剪通用版） |
| 4. 人工 env 注入 | Multica 网页 | Report-Developer：MVN_BIN / JAVA_HOME / NODE_BIN；Report-DevOps：GITLAB_TOKEN；其余无 |
| 5. 项目初始化 | `aicoding-project-init` | 建项目绑定**同一业务仓库**；GitLab 集成引导与通用工作区一致 |
| 6. 编排层 | `aicoding-orchestration-bootstrap` | 巡检 autopilot（30 分钟兜底）保留；doc-audit / retro 两个周级 autopilot **不装**（那些是通用链 harness 事务） |
| 7. 报表 harness 增量 | 轻量初始化（可人工可 agent） | 按 §9.2 建 `docs/report-flow/` 骨架（index / constitution / templates / review-checklist / lessons 初始文件）→ `feature/init-report-harness` 分支人工 MR——只新增目录，零侵入 |

- 步骤 1–6 复用现有 bootstrap 能力，无需新脚手架；步骤 7 体量小（约 8 个初始 md 文件），人工或任一 agent 按本文档执行即可。后续若频发建区，可把 7 步固化成一个 `report-workspace-bootstrap` 脚手架（本次不实现，仅预留）。
- **回退**：整个报表工作区可独立下线，不残留任何对原仓库的 harness 改动（唯一产物 `docs/report-flow/` 目录随历史 MR 存在，可单独 revert）。

## 11. 准确率保障机制汇总

| 机制 | 层 | 作用 |
|---|---|---|
| 报表设计四张封闭表 | 设计输入 | 消除 Developer 自由发挥空间——列/条件/契约/权限全部预定义 |
| 组件默认命中 query-list + 导出通道 | 设计输入 | 砍掉三层选型的不确定性，模板即正确答案 |
| 接口自测（curl 实测） | 开发 | 后端数据正确性的机器验证 |
| Reviewer 固定四关对照审 | 静态审查 | 实现 ↔ 设计逐项比对，偏离即打回；第④关兼核零侵入红线（写面外改动 = 打回） |
| lessons 持续学习 | 全程 | `docs/report-flow/lessons/`（报表自持），历史踩坑视同约束 |
| 人工收口三查 | 终验 | 查询/导出/权限的最终人工确认 |

## 12. 与通用链的升级/降级路径（跨工作区）

- 报表任务澄清中发现需 DDL / 非查询类 → Report-PM 停住，chat 建议：「本需求超出报表链边界，请到通用链工作区发起（澄清结论可直接引用本文）」；不代建通用链 issue。
- 通用链上的报表类需求 → 发起人可主动到报表工作区重新发起（同样跨工作区，澄清结论可复用）。
- 一次 change 不混链；两个工作区各自独立 issue 域与编排，天然不串。
