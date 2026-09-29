# aicoding-workspace-setup 设计文档

- 日期：2026-09-29
- 状态：待用户审阅
- 产物位置：`bootstrap/aicoding-workspace-setup/`

## 1. 背景与目标

新 Multica 工作区的安装链目前要手动依次运行 5 个 bootstrap skill（skills 拉取 → agent 创建 → project-init → orchestration → harness），人工在不同阶段被反复叫停。本 skill 把整条链编排成一次会话：**人在开头接入（一轮问答 + 一次网页操作窗口），结尾人审一次 MR，中间全自动**。

成功判据：
- 用户对新工作区的 Mika 说一句「安装工作区」，跑完即得：全技能入库、全角色 agent 建好、项目绑定仓库、编排层 3 个 autopilot 就位、仓库 harness 分支已 push 且 MR 已建好等人审
- 全程人工接触仅 3 次：初始问答、中段网页操作窗口、结尾 MR 审阅合并
- 中断后重跑不重做已完成步骤（断点续传）

## 2. 范围

**建**：
- `bootstrap/aicoding-workspace-setup/SKILL.md` — 编排主流程
- `bootstrap/aicoding-workspace-setup/references/pull-repo-skills.md` — 第②步精简拉取通道（固定本仓库场景，解决鸡生蛋）
- `bootstrap/aicoding-workspace-setup/references/human-checklist.md` — 第④步人工窗口清单模板

**不建**：
- 不复制 5 个子 skill 的流程内容（只编排引用，防双重维护漂移）
- 不改 5 个子 skill 本身（它们保持独立可用）
- 不做无库项目的特殊分支（探测到无库时沿用 harness-bootstrap 原有删减逻辑）

## 3. 已确认的设计决策

| 决策点 | 结论 |
|---|---|
| 执行者 | Mika（默认内置 agent，无需先建） |
| 收尾边界 | harness MR 由 agent 自动创建，人只做审阅合并（宪法首版必须人审，铁律保留） |
| 命名 | `aicoding-workspace-setup` |
| 初始入口（无法消除的最小启动操作） | 用户手动 `multica skill import` 本 skill 单包 + `multica agent skills add <Mika> --skill-ids <本skill>`，然后对 Mika 说「安装工作区」 |
| 时序重排 | 人工窗口后移到 agent 建成之后——env 配置入口在 agent 详情页，agent 建成才做得了；原链顺序依赖兼容（project-init 不验证 token，DevOps 首次建 MR 时自然验证） |

## 4. 执行时序（8 阶段）

```
① 一轮问答 ─→ ② 自动拉技能 ─→ ③ 自动建 agent ─→ ④ 人工窗口（唯一）
                                                    │ 用户回复「完成」
                                                    ↓
⑧ MR 人审 ←─ ⑦ 自动 harness（push + 自动建 MR）←─ ⑥ 自动编排层 ←─ ⑤ 自动建项目
```

### ① 一轮问答（chat 内，一次问完）

Mika 收集 4 类信息，缺哪项问哪项：

| 信息 | 用途 | 默认值 |
|---|---|---|
| 项目名 / 仓库 URL | project-init 第 3 步 | 无默认，必答 |
| MR 目标分支 | harness 第 2 步 + 自动建 MR | 无默认，必答（如 `test`） |
| 有无数据库 + 连接信息（db_type/host/port/user/service/schema） | harness 第 2 步数据库文档 | 扫 pom/yml 自动判有库无库；连接信息自动读 test 配置补缺 |
| 数据库密码来源 | harness 第 2 步 | 三选一：配置文件里有 / 用户提供（单次命令 env，用完即弃）/ 无库 |

同时预告：agent 建成后会有一轮网页操作清单，请留意。

### ② 自动：拉取本仓库全部技能

- 照 `references/pull-repo-skills.md` 执行（固定 repo = sunny-multica-skills 仓库；clone → 逐 skill 打 zip（顶层平铺、排除 .git/__pycache__/node_modules/.pyc）→ `multica skill import --file ... --on-conflict overwrite` → 附件校验补漏）
- 来源含两个：本仓库全部技能 + superpowers 系列（GitHub 源 obra/superpowers，Tech-Lead/Developer 的 plan/TDD 能力依赖）
- 此步**不依赖** aicoding-skills-bootstrap 已挂载（鸡生蛋解法：方法论以附带文档形式内置）
- 拉取完成后立即给 Mika 补挂载：5 个 bootstrap skill + `aicoding-db-schema-export`（harness 第 2 步硬校验要用）——`multica agent skills add`（追加式，禁用 set）
- 校验后进入 ③

### ③ 自动：创建全部角色 agent

- Skill 调用 aicoding-agent-bootstrap 执行
- 完成后收集其总体报告中的「env 人类待办清单」+「缺失登记」，供 ④ ⑤ 使用

### ④ 人工窗口（唯一一次网页操作，一次清单做完）

输出 `references/human-checklist.md` 渲染后的清单（结合 ①③ 的具体值），等用户回复「完成」：

| 项 | 级别 | 内容 |
|---|---|---|
| A. GitLab 自托管连接 | workspace 级 | Multica 网页 → 设置 → Git 代码托管（自托管）→ 新建连接，记下 webhook URL 与 secret |
| B. GitLab webhook | 仓库级 | GitLab 网页 → 仓库 Settings → Webhooks → 粘贴 A 所得，勾 push + merge request events，Test Hook 得 HTTP 200 |
| C. env 注入 | agent 级 | ③ 输出的清单（DevOps: GITLAB_TOKEN；Tester: TEST_ACCOUNT/TEST_PASSWORD/TEST_ROLE；Developer: DB_PASSWORD——仅当密码不在配置；**Mika: GITLAB_TOKEN——自动建 harness MR 用**） |

用户回复「完成」后，用 `multica repo add` + `multica repo checkout` 的结果间接验证 A/B（幂等可重验）；env 无法探测，沿用原链设计（DevOps 首次建 MR 自然验证）。验证失败不弃流程：报告差异 → 等用户修正 → 重验。

### ⑤ 自动：初始化项目

Skill 调用 aicoding-project-init 执行（跳过其第 0 步向用户的确认——信息已在 ① 收齐；跳过其第 1 步人工 checklist——已在 ④ 完成）。

### ⑥ 自动：复现编排层

Skill 调用 aicoding-orchestration-bootstrap 执行（无人工点；DocKeeper 缺失等按其原有「不阻断」设计登记）。

### ⑦ 自动：仓库 harness + 自动建 MR

- Skill 调用 aicoding-harness-bootstrap 执行（数据库连接信息/密码来源/分支已齐，不停等；密码用户提供的场景以单次命令 env 传入）
- **对子 skill 报告中「人工待办：MR 创建」的覆盖**：Mika 用自己的 GITLAB_TOKEN 走 GitLab API 建 MR（写 JSON body 文件防中文 500，`PRIVATE-TOKEN: $GITLAB_TOKEN`，API base 与 project-id 从项目上下文获取——同 aicoding-harness-audit 的既有做法）；建 MR 失败不回滚 harness 产物，降级为人工待办并给出分支名与建 MR 指引

### ⑧ 人工收尾（已确认保留）

人审合并 harness MR + 审宪法。主 skill 终局报告唯一剩余人工待办就是这一项。

## 5. 断点续传（无状态文件，纯幂等探测）

每个阶段开始前探测实际状态，已完成则跳过；用户中断后再说「继续安装」即从断点续跑：

| 阶段 | 探测命令 | 「已完成」判据 |
|---|---|---|
| ② 拉技能 | `multica skill list --output json` | 本仓库全部 skill 名在库 |
| ③ 建 agent | `multica agent list --output json` | agents/ 配置的 agent 名全部存在 |
| ④ 人工窗口 | `multica repo add` + `repo checkout` | add/checkout 成功（间接证明 GitLab 连接与仓库可达）；env 不可探测，靠对话上下文 |
| ⑤ 建项目 | `multica project list --output json` | 同名 project 存在且 github_repo 资源已绑定 |
| ⑥ 编排层 | `multica autopilot list --output json` | 3 个 autopilot（编排兜底巡检/结构文档对账/人工测试复盘）存在 |
| ⑦ harness | 仓库内 git | `feature/init-harness` 分支存在且已 push（或已合并） |

探测不到会话内历史（如新开会话续跑）时：④ 的人工窗口完成度以探测命令间接判断 + 需要时重发清单确认，宁可重问不瞎猜。

## 6. 失败处置分级

| 级别 | 例 | 处置 |
|---|---|---|
| 非致命 | 个别 skill 导入失败、agent 某项挂载缺失、附件超限 | 登记待办，继续（继承子 skill「不中断批处理」铁律） |
| 致命停等 | GitLab 连接失败、repo checkout 不可达、数据库密码拿不到 | 停下，人话报告修正指引，用户修好回「继续」后幂等重验 |
| 降级 | Mika 建 MR 失败（token 错/权限不足） | harness 产物保留，MR 转人工待办 |

**继承的铁律**（对子 skill 全部沿用）：
- 中文参数值一律 `@文件` 传参（multica_call.py），禁命令行内联中文
- 密码/token/secret 永不写入脚本参数、命令行、issue 评论、任何文档——用户当场提供的密码只进单次命令的环境变量
- 写库 SQL 永不执行；env 永不代写（人工通道）
- 每阶段在 chat 输出简短进度，只在人工点停等

## 7. SKILL.md 内容大纲

```
frontmatter（name / description 含 TRIGGER：「安装工作区」「一键安装」「初始化新工作区」）
├── 定位与执行者（Mika；全程 chat 内直执行，不开 issue 不派子任务）
├── 输入（$ARGUMENTS 可选=项目名/仓库URL；未给则进 ① 问答）
├── 执行时序（8 阶段，各阶段：做什么/调用哪个子 skill/探测判据/产物）
├── 断点续传（§5 判据表）
├── 失败处置分级（§6）
├── 终局报告（5 阶段产物 UUID/链接表 + 缺失登记汇总 + 唯一剩余人工待办：审 MR）
├── 铁律（继承 §6 清单）
└── 维护约定（子 skill 流程变更只动子 skill；本 skill 只护时序/判据/清单模板）
```

## 8. 与其他 skill 的边界

- 主 skill **不含**任何子 skill 的具体操作步骤——时序、探测判据、人工窗口编排、终局报告归它；建 agent 的细节归 agent-bootstrap，以此类推
- 子 skill 保持独立可单独运行（用户不想一键时仍可手动分步）
- 后续微调路径：安装流程顺序调整改本 skill；单个环节做法调整改对应子 skill

## 9. 验证方式

skill 为纯说明书，验证 = 安装走查：
1. 静态走查：对照 5 个子 skill 的执行流程逐阶段核对引用、探测判据、人工点覆盖无遗漏
2. 实战验证：下一个新工作区初始化时首跑本 skill，对照成功判据复盘
