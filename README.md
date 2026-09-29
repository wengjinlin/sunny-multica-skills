# sunny-multica-skills

sunny 项目 Multica AI 编排工作区的技能仓库，分两类工件：

- **`skills/`** — 运行期技能：挂在 Multica 角色 agent 上，在 issue 协作流程中被触发执行
- **`bootstrap/`** — 建区脚手架：新工作区/新仓库的一次性复现与初始化流程

## skills/ — 运行期技能（6 个）

| 技能 | 定位 | 主要使用者 |
|---|---|---|
| `aicoding-lookup-ui-reference-v3` | 前端 UI 选型速查手册：标准模块（form-modal / table-modal / form-table-modal、导入导出）、页面模板（query-list）、封装组件（SunnyForm / SunnyModal / SunnyBusinessSearch / useSunnyEditGrid 等，来自 `@sunny-base-web/ui`）三层选型，Arco 原生仅兜底。只输出查阅结论，不生成业务代码 | 全角色（写/评审 Vue 页面前） |
| `aicoding-db-schema-export` | 数据库表结构文档导出：连活库导出表/列/索引/主键/外键/注释，生成或重生成 `docs/database/` 文档，是它的唯一生成通道（禁止临时手写连接与 SQL） | Developer（DDL 后收尾） |
| `aicoding-config-auth-resource-v3` | 权限资源 SQL 生成：从 design.md 的前端页面/按钮清单生成 `auth-resource.sql`（AUTH_RES_MENU / AUTH_MODULE_URL / AUTH_RES_BUTTON 三表注册脚本）。只生成永不执行、永不生成角色授权 | PM（change stage 1 三件套之一） |
| `aicoding-browser-qa` | 报告式浏览器 QA：按 issue 验收点对 Web 页面分级测试（Quick / Standard / Exhaustive），产结构化 QA 报告（健康评分 + 分级问题表 + 截图证据）。只报告不修代码；依赖 gstack 浏览器基座，缺失时降级手测清单 | Tester（stage 4） |
| `aicoding-harness-audit` | 结构文档增量对账：从上次同步基线到 `origin/master` 的变更 diff 映射到应更新的 harness 结构文档（模块表/架构字典/隐性约定/术语表/能力清单），可自动项走 MR，DDL 与存疑项提醒人工 | DocKeeper（周级 autopilot） |
| `aicoding-human-test-retro` | 人工测试报告复盘归因：游标增量读取 `docs/human-test-reports/` 未读报告，逐 ⚠️ 问题做四源证据链归因（报告 × MR diff × OpenSpec 工件 × test-report），产期报 + lesson 草案走 retro 分支 MR，人审合并即决策 | DocKeeper（周级 autopilot） |

## bootstrap/ — 建区脚手架（6 个）

| 脚手架 | 作用 |
|---|---|
| `aicoding-workspace-setup` | **一键安装主入口**：一次会话串联下列全部脚手架（技能入库 → agent → 项目 → 编排 → harness），人工仅开头一轮问答 + 一次网页操作窗口，结尾人审 harness MR，中间全自动；断点续传（重跑自动跳过已完成阶段） |
|---|---|
| `aicoding-skills-bootstrap` | 从 GitHub 仓库拉取 skill 到 Multica 技能库（zip 通道保证附带文档完整；支持整仓 / 指定目录 / 指定技能，`sources.md` 清单模式） |
| `aicoding-agent-bootstrap` | 按 `agents/` 目录下的配置文件批量创建角色 agent（PM / Reviewer / Tester / DocKeeper / DevOps 等），一个文件一个 agent，含中文传参铁律（`@文件` 通道防 GBK 乱码） |
| `aicoding-project-init` | 初始化 Multica 项目：人工 GitLab 集成引导 → chat 内自动验证（repo 注册 + checkout）→ 建项目并绑定仓库 |
| `aicoding-orchestration-bootstrap` | 复现编排层：巡检兜底 autopilot（30 分钟 cron）+ Mika 编排接力入口 + 结构文档对账 autopilot + 人工测试复盘 autopilot（后两者周级，assignee=DocKeeper） |
| `aicoding-harness-bootstrap` | 新仓库 harness 建设：铺骨架（宪法 / 协作 / 审查 / 文档体系 / hooks / openspec）→ 代码分析填充 → `feature/init-harness` 分支人工 MR；已建仓库走对齐模式补缺 |

### 新工作区安装（推荐：一键）

手动做一次初始导入（唯一的启动操作）：

```
# 从本仓库打包 aicoding-workspace-setup 目录为 zip 后：
multica skill import --file <zip>          # 导入主 skill
multica agent skills add <Mika> --skill-ids <主skill-id>   # 挂给 Mika
```

然后对 Mika 说「**安装工作区**」，`aicoding-workspace-setup` 全自动串联全链。整个安装过程人工只接触 3 次：

1. 开头一轮问答（项目名 / 仓库 URL / MR 目标分支 / 数据库信息）
2. 中段一次网页操作窗口（GitLab 连接 + webhook + 各 agent 环境变量注入，一张清单做完）
3. 结尾人审合并 harness MR + 审宪法

中断后随时再说「继续安装」——幂等探测自动跳过已完成阶段，不重做。

### 分步手动（备选）

不想一键时，按原安装链逐个运行：

```
aicoding-skills-bootstrap（拉取 skill：本仓库默认只扫 skills/ 目录，bootstrap/ 下的脚手架须指定目录参数一并拉取；superpowers 系列另从 GitHub 源 obra/superpowers 拉）
  → aicoding-agent-bootstrap（创建角色 agent）
  → 人工 env 注入（如 GITLAB_TOKEN、测试账号等，Multica 网页操作）
  → aicoding-project-init（建项目绑仓库）
  → aicoding-orchestration-bootstrap（编排层）
  → aicoding-harness-bootstrap（仓库 harness）
```

## 约定速记

- **写库 SQL 永不执行**：`ddl-oracle.sql` 与 `auth-resource.sql` 同等待遇，三件套（design.md + ddl + auth-resource）由发起人人工执行，agent 只生成与判读
- **文档是唯一权威源**：`docs/database/` 只能经 `aicoding-db-schema-export` 生成；结构文档漂移由变更随行（第一道）+ `aicoding-harness-audit` 周级对账（第二道）双重防守
- **中文传参铁律**：凡含中文的 CLI 参数值一律经临时文件 `@文件` 传参，禁止命令行内联（GBK 代码页乱码事故）
- **密码只走环境变量 / 位置指针**：密码本体永不写入脚本参数、issue 评论或任何文档
