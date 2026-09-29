---
name: aicoding-workspace-setup
description: 新 Multica 工作区一键安装：一次会话串联技能入库 → 角色 agent 创建 → 项目绑定仓库 → 编排层 → 仓库 harness 全链，人工仅开头一轮问答 + 一次网页操作窗口，结尾人审 harness MR，中间全自动；断点续传（重跑自动跳过已完成阶段）。TRIGGER：「安装工作区」「一键安装」「初始化新工作区」「搭建新工作区」「workspace setup」。
metadata:
  author: mika-ecq
  version: '1.0'
---

# aicoding-workspace-setup：一键安装工作区

**定位**：编排型主 skill——只管时序 / 断点探测 / 人工窗口 / 终局报告；各环节的具体做法归对应子 skill，本 skill **不复制子流程内容**（子 skill 更新时本 skill 无需跟）。

**执行者**：Mika。**全程在当前 chat 会话内直接执行**——不开 issue、不派子任务给其他 agent（issue 子任务完成后没有编排链路自动回到本流程，会断链等人工提醒）；每阶段在 chat 输出简短进度，只在人工点停等。

**前置**：本 skill 已被导入并挂载给 Mika（初始入口，人工一次）；runtime 已 setup daemon（`multica runtime list` 探测，不可用则停等人工处理）。

## 输入

`$ARGUMENTS` 可选 =「项目名 仓库URL」（空格分隔）；未给全则第①步问答补齐，不给也能跑到①停下问。

---

## 执行时序（8 阶段）

```
① 一轮问答 ─→ ② 自动拉技能 ─→ ③ 自动建 agent ─→ ④ 人工窗口（唯一）
                                                    │ 用户回复「完成」
                                                    ↓
⑧ MR 人审 ←─ ⑦ 自动 harness（push + 自动建 MR）←─ ⑥ 自动编排层 ←─ ⑤ 自动建项目
```

### ① 一轮问答（chat 内，一次问完）

缺哪项问哪项，问全即止（探测能答的不问用户）：

| 信息 | 用途 | 来源 |
|---|---|---|
| 项目名 / 仓库 URL | ⑤ 建项目 | 用户必答（$ARGUMENTS 已给则不问） |
| MR 目标分支 | ⑦ harness 填充 + 自动建 MR | 用户必答（如 `test`） |
| 有无数据库 + 连接信息（db_type/host/port/user/service/schema） | ⑦ 数据库文档 | 扫目标仓库 pom 驱动依赖 + application*.yml / *.properties 自动判、自动读 **test 环境**配置补缺；判不了或缺项才问 |
| 数据库密码来源 | ⑦ 连库导出 | 三选一问用户：**配置文件里有**（读配置值，登记密码位置指针）/ **用户当场提供**（只进单次命令环境变量，用完即弃）/ **无库** |

问完同时预告：agent 建成后会有一轮网页操作清单（④），请留意。

### ② 自动：拉取全部技能

- 照 [`references/pull-repo-skills.md`](references/pull-repo-skills.md) 执行（双来源：本仓库全部技能 + superpowers 系列 GitHub 源 obra/superpowers）
- **不依赖** aicoding-skills-bootstrap 已挂载（首跑时库里只有本 skill，方法论以内置附带文档解鸡生蛋）
- 拉完给 Mika 补挂载 6 个 skill（5 个 bootstrap + aicoding-db-schema-export——⑦ 的硬校验依赖），`skills add` 追加式
- 单个导入失败不阻断：登记留终局报告

### ③ 自动：创建全部角色 agent

- Skill 调用 **aicoding-agent-bootstrap** 执行（7 个角色：PM / Tech-Lead / Developer / Reviewer / Tester / DocKeeper / DevOps）
- 完成后收集其总体报告的**env 人类待办清单**与**缺失登记**，供 ④ 渲染与终局报告用

### ④ 人工窗口（唯一一次网页操作，一次清单做完）

1. 渲染 [`references/human-checklist.md`](references/human-checklist.md)：
   - `{{REPO_URL}}` 替换为 ① 的仓库 URL
   - `{{DB_PASSWORD_HINT}}` 按 ① 判定替换：密码在配置文件 → **删除整行**；密码不在配置 → 替换为 Developer 的 `DB_PASSWORD`（数据库密码，连库导表结构文档用）一行归入必配表
2. 等用户回复「完成」——不催、不设时限
3. 间接验证（幂等可重验）：`multica repo add <REPO_URL>` + `multica repo checkout <REPO_URL>` 成功 = GitLab 连接（A）+ 仓库可达验证通过；失败不弃流程：报告差异 → 等用户修正 → 重验
4. env 注入（C 项）**不可探测**——沿用原链设计：DevOps 的 GITLAB_TOKEN 留待其首次建 MR 自然验证；Mika 的 GITLAB_TOKEN 在 ⑦ 建 MR 时自然验证，401 届时回头检查配置

### ⑤ 自动：初始化项目

- Skill 调用 **aicoding-project-init** 执行，两处编排覆盖：
  - 第 0 步向用户确认的项目名 / 仓库 URL → 用 ① 收集值，**不再问**
  - 第 1 步人工三事项 checklist（GitLab 连接 / webhook / token）→ **已在 ④ 完成，跳过输出与等待**；其第 2 步验证命令照常执行（幂等）
- 产物：project UUID + github_repo 资源绑定

### ⑥ 自动：复现编排层

- Skill 调用 **aicoding-orchestration-bootstrap** 执行（无人工点；DocKeeper 或某 skill 缺失按其原有「不阻断」设计登记待办）

### ⑦ 自动：仓库 harness + 自动建 MR

- Skill 调用 **aicoding-harness-bootstrap** 执行。编排覆盖其人工点：
  - 数据库预检的连接信息 / 密码来源 → 用 ① 收集结果，**不停等**；密码「用户当场提供」的以单次命令 env 传给导出脚本，用完即弃
  - MR 目标分支 → 用 ① 收集值，**不再问**
- **MR 自动建**（覆盖子 skill 报告中「人工待办：MR 创建」）：harness push 完 `feature/init-harness` 后，Mika 走 GitLab API 建 MR——请求体写 **JSON body 文件**（form 编码中文会 500），`PRIVATE-TOKEN: $GITLAB_TOKEN`（读 Mika 自身进程环境变量），API base 与 project-id 从项目上下文获取不写死——同 aicoding-harness-audit 的既有做法
- 建 MR 失败（token 错 / 权限不足）：**不回滚 harness 产物**，降级为人工待办——报告分支名与人话建 MR 指引

### ⑧ 人工收尾（最后一步，人审）

人审合并 harness MR + 审宪法（宪法首版必须人审，铁律）。终局报告的唯一剩余人工待办就是这一项。

---

## 断点续传（无状态文件，纯幂等探测）

中断后用户再说「安装工作区 / 继续安装」即从断点续跑。每阶段开始前先探测，已完成则跳过并在进度里注明「跳过（已完成）」：

| 阶段 | 探测命令 | 「已完成」判据 |
|---|---|---|
| ② 拉技能 | `multica skill list --output json` | 本仓库 + superpowers 系列全部 skill 名在库 |
| ③ 建 agent | `multica agent list --output json` | agents/ 配置的 7 个 agent 名全部存在 |
| ④ 人工窗口 | `multica repo add <REPO_URL>` + `multica repo checkout <REPO_URL>` | add / checkout 成功（间接证明 GitLab 连接与仓库可达）；**env 不可探测，靠对话上下文** |
| ⑤ 建项目 | `multica project list --output json` | 同名 project 存在且 github_repo 资源已绑定 |
| ⑥ 编排层 | `multica autopilot list --output json` | 3 个 autopilot（编排兜底巡检 / 结构文档对账 / 人工测试复盘）存在 |
| ⑦ harness | 仓库内 `git branch -r` | `feature/init-harness` 已 push（或已合并进目标分支） |

新会话续跑（探测不到会话内历史）时：④ 的完成度以探测命令间接判断，必要时**重发清单向用户确认——宁可重问不瞎猜**。

## 失败处置分级

| 级别 | 例 | 处置 |
|---|---|---|
| 非致命 | 个别 skill 导入失败、agent 某项挂载缺失、附件超限 | 登记待办，继续（继承子 skill「不中断批处理」铁律） |
| 致命停等 | GitLab 连接失败、repo checkout 不可达、数据库密码拿不到 | 停下，人话报告修正指引，用户修好回「继续」后幂等重验 |
| 降级 | Mika 建 MR 失败（token 错 / 权限不足） | harness 产物保留，MR 转人工待办 |

## 终局报告

一次大汇总收口全部阶段：

1. **8 阶段产物表**：阶段 × 状态（完成 / 跳过及原因）× 产物（skill 入库数、agent UUID 表、project UUID + 链接 `[<项目名>](mention://project/<project-id>)`、autopilot ×3 UUID、harness 分支 + MR 链接或降级指引）
2. **缺失登记汇总**：②③ 各子 skill 报告的缺失项合并，附补齐命令
3. **唯一剩余人工待办**：人审合并 harness MR + 审宪法
4. **后续微调路径**一句：文档演进走仓库 MR；结构变更回写对应 skill

## 铁律

- **中文传参**：凡含中文的 CLI 参数值一律经 multica_call.py 传 `@文件`（临时 utf-8 文件，用完即删），禁止 `$(cat)` 内联、禁止命令行直写中文
- **敏感值**：密码 / token / secret 永不写入脚本参数、命令行、issue 评论或任何文档；用户当场提供的密码只进单次命令的环境变量
- **写库 SQL 永不执行；env 永不代写**（env 是人工通道，agent 只在自己进程里读）
- **不中断批处理**：任何非致命缺失只登记不回滚不跳阶段
- 每阶段 chat 输出简短进度；只在人工点（①④⑧）停等

## 维护约定

- 时序 / 断点判据 / 人工窗口编排 / 终局报告改动 → 改本 skill
- 单个环节的具体做法改动 → 改对应子 skill（本 skill 不跟）
- 子 skill 保持独立可分步手动运行（用户不想一键时仍可按 README 分步链跑）
- `references/human-checklist.md` 的 env 表是 agents/*.md 的快照：agents 配置变更须同步改快照
