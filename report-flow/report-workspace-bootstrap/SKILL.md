---
name: aicoding-report-workspace-bootstrap
description: 报表专用 Multica 工作区一键建区：一次会话按 report-flow/design.md §10 七步串联——拉 4 个业务 skill → 建 4 个 Report-* agent → 人工 env 窗口 → 项目绑定同一业务仓库 → 报表版 Mika 编排 + 精简编排层（仅巡检兜底）→ docs/report-flow/ 增量 harness + 自动建 MR，断点续传，对业务仓库零侵入。TRIGGER：「建报表工作区」「报表工作区安装」「一键建报表工作区」「report workspace setup」。
metadata:
  author: mika-ecq
  version: '1.0'
---

# aicoding-report-workspace-bootstrap：一键建报表工作区

**定位**：编排型主 skill——只管时序 / 断点探测 / 人工窗口 / 终局报告；报表建区差异点（agent 配置、Mika 编排文本、巡检剧本、harness 骨架）全部以本目录附带文件为权威源。设计依据：本仓库 `report-flow/design.md`（§10 部署七步）。

**执行者**：Mika。**全程在当前 chat 会话内直接执行**——不开 issue、不派子任务；每阶段输出简短进度，只在人工点停等。

**前置**：本 skill 已导入并挂载给 Mika（初始入口，人工一次）；runtime 已 setup daemon（`multica runtime list` 探测，不可用则停等人工处理）。

**与通用链工作区的关系**：本流程产出的报表工作区与既有通用链工作区**并存**、绑定**同一业务仓库**；harness 写面收敛到业务仓库 `docs/report-flow/` 一个新增目录，零侵入（design.md §9）。

## 输入

`$ARGUMENTS` 可选 =「项目名 仓库URL」（空格分隔）；未给全则第①步问答补齐。

---

## 执行时序（8 阶段）

```
① 一轮问答 ─→ ② 拉业务技能 ─→ ③ 建 Report agent ─→ ④ 人工窗口（唯一）
                                                      │ 用户回复「完成」
                                                      ↓
⑧ MR 人审 ←─ ⑦ harness 增量（skeleton + push + 自动建 MR）←─ ⑥ 编排层（报表版）←─ ⑤ 建项目
```

### ① 一轮问答（chat 内，一次问完）

| 信息 | 用途 | 来源 |
|---|---|---|
| 项目名 / 仓库 URL | ⑤ 建项目 | 用户必答（$ARGUMENTS 已给则不问） |
| MR 目标分支 | ⑦ harness 增量建 MR | 用户必答（如 `test`） |

报表链免 DDL、无数据库文档生成——**不问数据库连接信息**（表结构查阅口径见业务仓库 `docs/report-flow/constitution.md` 落成后的说明）。

问完同时预告：agent 建成后会有一轮网页操作清单（④），请留意。

### ② 自动：拉取业务技能（4 个）

- **不依赖** aicoding-skills-bootstrap 已挂载（首跑时库里只有本 skill，方法论内置）：
  1. `git clone --depth 1 https://github.com/wengjinlin/sunny-multica-skills <临时目录>`
  2. 待拉清单 = `<临时目录>/report-flow/skills/` 下全部 4 个 skill（lookup-v2/v3、config-auth-v2/v3，自包含副本）；再从 `<临时目录>/bootstrap/aicoding-project-init` 加拉 1 个（⑤ 的执行框架）
  3. 逐 skill 打 zip（**顶层就是 SKILL.md 与附带文件平级**，排除 `.git`/`__pycache__`/`node_modules`/`.pyc`）→ `multica skill import --file <zip> --on-conflict overwrite --output json`（结果先落盘再解析）
  4. **附件校验补漏**（强制，`--url` 通道实测丢附件，zip 也要复核）：`multica skill files list <skill-id>` 对照源目录文件清单（去掉 SKILL.md 本体），缺失逐个 `multica skill files upsert <skill-id> --path <zip内路径> --content-file <源文件>`
  5. Mika 补挂载：`multica agent skills add <Mika-UUID> --skill-ids <aicoding-project-init 的 id>`（add 追加式，禁止 set）
- 单个失败不阻断：登记留终局报告
- **不拉**：superpowers 系、openspec 系、db-schema-export、browser-qa、harness-audit、human-test-retro（design.md §10 裁剪清单）

### ③ 自动：创建 4 个 Report agent

- 配置目录 = `<临时目录>/report-flow/agents/`（4 个 `Report-*.md`，文件数 = 创建数；格式同 aicoding-agent-bootstrap：frontmatter 标量 → create 参数 + 正文「## 指令 / ## 分配 skill / ## 分配 MCP / ## 自定义 env」四节）
- Mika 是工作区内置默认 agent，**不创建**；通用链 6 角色（PM/Tech-Lead/…）**不建**
- 执行前先写 `multica_call.py`（见文末铁律）；逐文件：
  1. **幂等**：同名 agent 已存在 → 只做三动作（`--instructions @instr.tmp` 整体覆盖 / skills 按配置对齐，配置「（无）」则不动现有挂载 / MCP 非「（无）」才 update）；其余字段一律不碰
  2. **创建**：`python multica_call.py agent create --name <name> --description @desc.tmp --max-concurrent-tasks <n> --visibility workspace --runtime-id <runtime-id> --instructions @instr.tmp`（frontmatter 空字段省略参数）
  3. **分配 skill**：按「## 分配 skill」节 `multica agent skills add <id> --skill-ids <…>`（按 name 解析 id）；缺失的 skill 只登记不阻断
  4. **env**：不执行任何 env 读写（env 是人工通道）——逐 key 整理进 ④ 的清单
- 收集**env 人类待办清单**与**缺失登记**，供 ④ 渲染与终局报告用

### ④ 人工窗口（唯一一次网页操作，一次清单做完）

1. 渲染 [`references/human-checklist.md`](references/human-checklist.md)：`{{REPO_URL}}` 替换为 ① 的仓库 URL
2. 等用户回复「完成」——不催、不设时限
3. 间接验证（幂等可重验）：`multica repo add <REPO_URL>` + `multica repo checkout <REPO_URL>` 成功 = GitLab 连接 + 仓库可达；失败不弃流程：报告差异 → 等修正 → 重验
4. env 注入不可探测：Report-DevOps 的 GITLAB_TOKEN 留待其首次建 MR 自然验证；Mika 的 GITLAB_TOKEN 在 ⑦ 建 MR 时自然验证，401 届时回头检查配置

### ⑤ 自动：初始化项目

- Skill 调用 **aicoding-project-init**（② 已入库挂载），两处编排覆盖：
  - 第 0 步向用户确认的项目名 / 仓库 URL → 用 ① 收集值，**不再问**
  - 第 1 步人工三事项 checklist（GitLab 连接 / webhook / token）→ **已在 ④ 完成，跳过输出与等待**；其第 2 步验证命令照常执行（幂等）
- 产物：project UUID + github_repo 资源绑定（绑定**同一业务仓库**，与通用链工作区并存）

### ⑥ 自动：报表版编排层（仅 2 组件）

通用版 4 组件裁剪为 2：**保留**巡检兜底 autopilot + Mika 编排接力入口；**不装** doc-audit / retro 两个周级 autopilot（通用链 harness 事务）。`multica autopilot list --output json` 记录现有名单作幂等基准。

1. **巡检 autopilot**：`autopilot-report.md` 全文写 `./ap.tmp`、标题「编排兜底巡检（报表）」写 `./title.tmp`（utf-8）。同名已存在 → 取 ID 只更新剧本（`autopilot update <id> --description @ap.tmp`，不碰触发器/assignee）；不存在 → `python multica_call.py autopilot create --title @title.tmp --description @ap.tmp --agent Mika --mode run_only --output json`。触发器**先查后加**：`multica autopilot trigger-add <AUTOPILOT_ID> --kind schedule --cron "*/30 * * * *" --timezone Asia/Shanghai`。记录 **AUTOPILOT_ID**
2. **Mika 编排接力入口**：`multica agent get <Mika-ID> --output json` 读当前**自定义 instructions**（不是 system_instructions）；`mika-instructions-report.md` 中 `{{AUTOPILOT_ID}}` 全部替换；**幂等合并**——已含「## 工作区补充：编排接力与建单（报表专用工作区，单链版）」节 → 该节整节替换、其余原样保留；没有 → 末尾追加。合并结果写 utf-8 临时文件回写：`python multica_call.py agent update <Mika-ID> --instructions @instr.tmp`

### ⑦ 自动：harness 增量 + 自动建 MR（零侵入）

1. 在 ⑤ checkout 的业务仓库工作副本中，将本 skill 附带的 `skeleton/` 全部内容拷入 `docs/report-flow/`（**只新增这一个目录**，约 8 个初始 md；禁改仓库任何已有文件——design.md §9.1 禁改面）
2. 仓库根无 `CLAUDE.md` 时：提醒用户 `docs/report-flow/constitution.md` 的「项目事实登记」节需人工填充（最小事实：模块清单/技术栈/构建命令/数据库方言）
3. `git checkout -b feature/init-report-harness` → add / commit（message 注明「报表工作区 harness 增量，零侵入，仅新增 docs/report-flow/」）→ push
4. **MR 自动建**：走 GitLab API——请求体写 **JSON body 文件**（form 编码中文会 500），`PRIVATE-TOKEN: $GITLAB_TOKEN`（读 Mika 自身进程环境变量），API base 与 project-id 从项目上下文获取不写死；MR description 注明只新增 `docs/report-flow/` 目录
5. 建 MR 失败（token 错 / 权限不足）：**不回滚 harness 产物**，降级为人工待办——报告分支名与人话建 MR 指引

### ⑧ 人工收尾（最后一步，人审）

人审合并 `feature/init-report-harness` MR。终局报告的唯一剩余人工待办就是这一项。

---

## 断点续传（无状态文件，纯幂等探测）

中断后用户再说「建报表工作区 / 继续建区」即从断点续跑。每阶段开始前先探测，已完成则跳过并注明「跳过（已完成）」：

| 阶段 | 探测命令 | 「已完成」判据 |
|---|---|---|
| ② 拉技能 | `multica skill list --output json` + `multica agent skills list <Mika-UUID>` | 4 个业务 skill + aicoding-project-init 全在库，且 project-init 已挂载 Mika（挂载追加式，重跑安全） |
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
2. **缺失登记汇总**：②③ 的缺失项合并，附补齐命令
3. **唯一剩余人工待办**：人审合并 init-report-harness MR（+ 仓库无 CLAUDE.md 时补填「项目事实登记」节）
4. **后续使用路径**一句：日常需求向 Report-PM 发起 chat 澄清；超出报表边界的任务到通用链工作区发起（design.md §12）

## 铁律

- **中文传参**：凡含中文的 CLI 参数值一律经 multica_call.py 传 `@文件`（临时 utf-8 文件，用完即删），禁止 `$(cat)` 内联、禁止命令行直写中文。助手脚本：

  ```python
  # multica_call.py — 用法：python multica_call.py <子命令...> --description @<utf-8 文件路径>
  import subprocess, sys
  args = []
  for a in sys.argv[1:]:
      args.append(open(a[1:], 'rb').read().decode('utf-8') if a.startswith('@') else a)
  r = subprocess.run(['multica'] + args, capture_output=True, text=True, encoding='utf-8')
  print(r.returncode)
  print((r.stdout or '')[:2000])
  if r.returncode:
      print((r.stderr or '')[-800:])
  ```

- **敏感值**：密码 / token / secret 永不写入脚本参数、命令行、issue 评论或任何文档
- **env 永不代写**（env 是人工通道，agent 只在自己进程里读）
- **不中断批处理**：任何非致命缺失只登记不回滚不跳阶段
- **零侵入**：⑦ 只允许新增 `docs/report-flow/`，业务仓库其他文件一律只读
- 每阶段 chat 输出简短进度；只在人工点（①④⑧）停等

## 维护约定

- 时序 / 断点判据 / 人工窗口编排 / 终局报告改动 → 改本 skill
- agent 内容改动 → 改 `report-flow/agents/*.md`（本仓库唯一权威源；`report-flow/skills/` 下的 4 个业务 skill 是 `skills/` 同名目录的**自包含副本**，上游改动须同步拷贝）
- Mika 编排文本 / 巡检剧本改动 → 改 `mika-instructions-report.md` / `autopilot-report.md`，并在服务端手工改过后回写防漂移；报表 stage 链基准与 `report-flow/agents/Report-PM.md` 内嵌建单模板**双处同改**（权威源在编排层，见 design.md §7）
- harness 骨架改动 → 改 `skeleton/`（§9.2 结构为约束）
