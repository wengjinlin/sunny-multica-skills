---
name: aicoding-report-workspace-bootstrap
description: 报表专用 Multica 工作区一键建区：一次会话按 report-flow/design.md §10 七步串联——拉技能 → 建 Report agent → 人工 env 窗口 → 项目绑定同一业务仓库 → 报表编排层 → harness 增量自动建 MR，断点续传，对业务仓库零侵入。各环节做法归 report-flow/bootstrap/ 下的分步 skill。TRIGGER：「建报表工作区」「报表工作区安装」「一键建报表工作区」「report workspace setup」。
metadata:
  author: mika-ecq
  version: '1.1'
---

# aicoding-report-workspace-bootstrap：一键建报表工作区

**定位**：编排型主 skill——只管时序 / 断点探测 / 人工窗口 / 终局报告；各环节的具体做法归 `report-flow/bootstrap/` 下的 3 个分步 skill（aicoding-report-agent-bootstrap / aicoding-report-orchestration-bootstrap / aicoding-report-harness-bootstrap）与复用 skill（aicoding-project-init），本 skill **不复制子流程内容**（子 skill 更新时本 skill 无需跟）。分步手动链见 `report-flow/README.md`。

**执行者**：Mika。**全程在当前 chat 会话内直接执行**——不开 issue、不派子任务；每阶段输出简短进度，只在人工点停等。

**前置**：本 skill 已导入并挂载给 Mika（初始入口，人工一次）；runtime 已 setup daemon（`multica runtime list` 探测，不可用则停等人工处理）。

**与通用链工作区的关系**：产出的报表工作区与既有通用链工作区**并存**、绑定**同一业务仓库**；harness 写面收敛到业务仓库 `docs/report-flow/` 一个新增目录，零侵入（design.md §9）。

## 输入

`$ARGUMENTS` 可选 =「项目名 仓库URL」（空格分隔）；未给全则第①步问答补齐。

---

## 执行时序（8 阶段）

```
① 一轮问答 ─→ ② 拉技能 ─→ ③ 建 Report agent ─→ ④ 人工窗口（唯一）
                                                  │ 用户回复「完成」
                                                  ↓
⑧ MR 人审 ←─ ⑦ harness 增量（分步 skill：skeleton + push + 自动建 MR）←─ ⑥ 编排层（分步 skill）←─ ⑤ 建项目
```

### ① 一轮问答（chat 内，一次问完）

| 信息 | 用途 | 来源 |
|---|---|---|
| 项目名 / 仓库 URL | ⑤ 建项目 | 用户必答（$ARGUMENTS 已给则不问） |
| MR 目标分支 | ⑦ harness 增量建 MR | 用户必答（如 `test`） |

报表链免 DDL、无数据库文档生成——**不问数据库连接信息**。问完同时预告：agent 建成后会有一轮网页操作清单（④），请留意。

### ② 自动：拉取技能（4 业务 + 4 编排）

- **不依赖** aicoding-skills-bootstrap 已挂载（首跑时库里只有本 skill，方法论内置）：
  1. `git clone --depth 1 https://github.com/wengjinlin/sunny-multica-skills <临时目录>`
  2. 待拉清单 8 个：`report-flow/skills/` 下 4 个业务 skill（lookup-v2/v3、config-auth-v2/v3，自包含副本）+ `report-flow/bootstrap/` 下 3 个分步 skill + `bootstrap/aicoding-project-init`
  3. 逐 skill 打 zip（**顶层就是 SKILL.md 与附带文件平级**，排除 `.git`/`__pycache__`/`node_modules`/`.pyc`）→ `multica skill import --file <zip> --on-conflict overwrite --output json`（结果先落盘再解析）
  4. **附件校验补漏**（强制，`--url` 通道实测丢附件，zip 也要复核）：`multica skill files list <skill-id>` 对照源目录文件清单（去掉 SKILL.md 本体），缺失逐个 `multica skill files upsert <skill-id> --path <zip内路径> --content-file <源文件>`
  5. Mika 补挂载 4 个编排 skill：`multica agent skills add <Mika-UUID> --skill-ids <3 个分步 skill + aicoding-project-init 的 id>`（add 追加式，禁止 set）
- 单个失败不阻断：登记留终局报告
- **不拉**：superpowers 系、openspec 系、db-schema-export、browser-qa、harness-audit、human-test-retro（design.md §10 裁剪清单）

### ③ 自动：创建 Report agent

- Skill 调用 **aicoding-report-agent-bootstrap** 执行（读其自带 `agents/` 4 个 Report-* 配置；Mika 内置不创建，通用 6 角色不建）
- 完成后收集其总体报告的 **env 人类待办清单**与**缺失登记**，供 ④ 渲染与终局报告用

### ④ 人工窗口（唯一一次网页操作，一次清单做完）

1. 渲染 [`references/human-checklist.md`](references/human-checklist.md)：`{{REPO_URL}}` 替换为 ① 的仓库 URL
2. 等用户回复「完成」——不催、不设时限
3. 间接验证（幂等可重验）：`multica repo add <REPO_URL>` + `multica repo checkout <REPO_URL>` 成功 = GitLab 连接 + 仓库可达；失败不弃流程：报告差异 → 等修正 → 重验
4. env 注入不可探测：Report-DevOps 的 GITLAB_TOKEN 留待其首次建 MR 自然验证；Mika 的 GITLAB_TOKEN 在 ⑦ 建 MR 时自然验证，401 届时回头检查配置

### ⑤ 自动：初始化项目

- Skill 调用 **aicoding-project-init**（② 已入库挂载），两处编排覆盖：
  - 第 0 步向用户确认的项目名 / 仓库 URL → 用 ① 收集值，**不再问**
  - 第 1 步人工三事项 checklist（GitLab 连接 / webhook / token）→ **已在 ④ 完成，跳过输出与等待**；其第 2 步验证命令照常执行（幂等）
- 产物：project UUID + github_repo 资源绑定（绑定**同一业务仓库**）

### ⑥ 自动：报表版编排层

- Skill 调用 **aicoding-report-orchestration-bootstrap** 执行（2 组件：巡检兜底 autopilot + Mika 报表单链版接力入口；doc-audit / retro 不装是其内置裁剪，无人工点）

### ⑦ 自动：harness 增量 + 自动建 MR

- Skill 调用 **aicoding-report-harness-bootstrap** 执行。编排覆盖其人工点：
  - 第 0 步 MR 目标分支 → 用 ① 收集值，**不再问**
  - 第 1 步 repo checkout → **已在 ④ 完成**（幂等可重跑）
- 产物：业务仓库 `docs/report-flow/` 骨架 + `feature/init-report-harness` 分支 + MR 链接（失败降级人工指引，不回滚产物——继承子 skill 设计）

### ⑧ 人工收尾（最后一步，人审）

人审合并 `feature/init-report-harness` MR（+ 业务仓库无 CLAUDE.md 时补填 `docs/report-flow/constitution.md`「项目事实登记」节——⑦ 已探测提醒）。终局报告的唯一剩余人工待办就是这一项。

---

## 断点续传（无状态文件，纯幂等探测）

中断后用户再说「建报表工作区 / 继续建区」即从断点续跑。每阶段开始前先探测，已完成则跳过并注明「跳过（已完成）」：

| 阶段 | 探测命令 | 「已完成」判据 |
|---|---|---|
| ② 拉技能 | `multica skill list --output json` + `multica agent skills list <Mika-UUID>` | 8 个 skill（4 业务 + 3 分步 + project-init）全在库，且 4 个编排 skill 已挂载 Mika（挂载追加式，重跑安全） |
| ③ 建 agent | `multica agent list --output json` | report-flow/agents/ 配置的 4 个 Report-* agent 名全部存在 |
| ④ 人工窗口 | `multica repo add <REPO_URL>` + `multica repo checkout <REPO_URL>` | add / checkout 成功；env 不可探测，靠对话上下文，必要时**重发清单向用户确认——宁可重问不瞎猜** |
| ⑤ 建项目 | `multica project list --output json` | 同名 project 存在且 github_repo 资源已绑定 |
| ⑥ 编排层 | `multica autopilot list --output json` + `multica agent get <Mika-ID>` | 「编排兜底巡检（报表）」autopilot 存在且带 schedule 触发器；Mika instructions 已含报表版「工作区补充」节 |
| ⑦ harness | 业务仓库内 `git branch -r` | `feature/init-report-harness` 已 push（或已合并进目标分支） |

## 失败处置分级

| 级别 | 例 | 处置 |
|---|---|---|
| 非致命 | 个别 skill 导入失败、agent 某项挂载缺失、附件超限 | 登记待办，继续（不中断批处理） |
| 致命停等 | GitLab 连接失败、repo checkout 不可达 | 停下，人话报告修正指引，用户修好回「继续」后幂等重验 |
| 降级 | Mika 建 MR 失败（token 错 / 权限不足） | harness 产物保留，MR 转人工待办 |

## 终局报告

1. **8 阶段产物表**：阶段 × 状态（完成 / 跳过及原因）× 产物（skill 入库数、agent UUID 表、project UUID + 链接 `[<项目名>](mention://project/<project-id>)`、autopilot UUID + cron、harness 分支 + MR 链接或降级指引）
2. **缺失登记汇总**：②③ 各子 skill 报告的缺失项合并，附补齐命令
3. **唯一剩余人工待办**：人审合并 init-report-harness MR（+ 无 CLAUDE.md 时补填「项目事实登记」节）
4. **后续使用路径**一句：日常需求向 Report-PM 发起 chat 澄清；超出报表边界的任务到通用链工作区发起（design.md §12）

## 铁律

- **中文传参**：凡含中文的 CLI 参数值一律经 multica_call.py 传 `@文件`（临时 utf-8 文件，用完即删），禁止 `$(cat)` 内联、禁止命令行直写中文（脚本见任一分步 skill，②拉取后按子 skill 自带协议执行）
- **敏感值**：密码 / token / secret 永不写入脚本参数、命令行、issue 评论或任何文档
- **env 永不代写**（env 是人工通道，agent 只在自己进程里读）
- **不中断批处理**：任何非致命缺失只登记不回滚不跳阶段
- **零侵入**：业务仓库只允许新增 `docs/report-flow/`，其他文件一律只读（⑦ 子 skill 自检）
- 每阶段 chat 输出简短进度；只在人工点（①④⑧）停等

## 维护约定

- 时序 / 断点判据 / 人工窗口编排 / 终局报告改动 → 改本 skill
- 单个环节的具体做法 / 模板文件（agents 配置、巡检剧本、Mika 编排文本、harness 骨架）改动 → 改 `report-flow/bootstrap/` 对应分步 skill（本 skill 不跟）
- 分步 skill 保持独立可分步手动运行（用户不想一键时按 `report-flow/README.md` 分步链跑）
- `references/human-checklist.md` 的 env 表是 4 个 Report agent 配置 + Mika 的快照：agents 配置变更须同步改快照；**Mika 的 GITLAB_TOKEN 行归本 skill 所有**（分步链中该值由 aicoding-project-init 的人工三事项引导，不在 Report agent 配置内）
