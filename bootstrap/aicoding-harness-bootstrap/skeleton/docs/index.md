# 文档导航

> docs/ 目录的唯一入口。任何角色开工先读本文件，再按「必读顺序」进对应文档。
> 宪法级红线在仓库根 CLAUDE.md / REVIEW.md，本目录维护的是工作字典与详单。

## 目录结构

| 分类 | 路径 | 内容 | 主要读者 |
|---|---|---|---|
| 架构 | `architecture/index.md` | 业务模块对应表（模块定位字典）/高风险区域/ADR/技术债 | 全部角色 |
| 架构 | `architecture/implicit-contracts.md` | 隐性业务约定（口头约定/历史包袱/规范差异现状） | 全部角色 |
| 产品 | `product/index.md` | 业务域划分/术语表/状态机/业务校验铁律 | PM 为主 |
| 规范 | `standards/api.md` | 接口设计规范 + 评审清单 | PM/Developer/Reviewer |
| 规范 | `standards/database.md` | 数据库与 SQL 规范 + 变更检查清单 | PM/Developer/Reviewer |
| 规范 | `standards/testing.md` | 测试规范（新旧代码口径） | Developer/Tester/Reviewer |
| 模板 | `templates/design-review-template.md` | 前端设计人审模板（需求概览/表单字段/表格/按钮权限/接口） | PM/Reviewer |
| 数据库 | `database/index.md` | 全库表清单（按域）+ 再生成规则 | PM/Developer |
| 数据库 | `database/tables/<域>.md` | 每表字段/主键/约束详情 | PM/Developer/Reviewer |
| 平台能力 | `help/index.md` | 平台包能力清单与使用指南 | 全部角色 |
| 教训 | `lessons/index.md` + 角色文件 | 按角色分文件的经验教训 | 全部角色 |
| 人工测试 | `human-test-reports/index.md` + 报告 | 人工测试验证报告（日期-分支名.md，测试者只写现象与处理，归因在复盘做） | 人类测试者 / 复盘 |

<!-- 分析指引：按仓库实际保留的文档增删行（无数据库的项目删 database 两行，无平台包体系删 help 行）；删行后同步删「必读顺序」中的引用；human-test-reports 行全部项目保留（人工收口机制不依赖技术栈） -->

## 必读顺序（按角色）

{{ROLE_READING_ORDER}}

<!-- 分析指引：从 Multica agent list 角色清单生成每个角色的必读列表（PM：product → architecture/index → database → implicit-contracts → help（涉及时）；Tech-Lead：architecture/index → lessons 全部；Developer：architecture/index（代码落位）→ standards 对应篇 → lessons/Developer；Tester：standards/testing → lessons/Tester；Reviewer：standards 全部 → lessons 全部；DevOps：lessons 全部）。与各 agent 指令中的「项目上下文」读单保持一致，双处修改必须同步 -->

## 文档维护规则

1. **代码结构变更**（新模块/新表/新平台包/新隐性约定）→ 对应文档在**同一个 change** 内更新：Tech-Lead 在 tasks.md 显式安排文档 task，不允许「事后补文档」
2. **数据库表结构变更**（建表/加字段）→ DDL 人工执行后，按 `database/index.md` 的「再生成规则」重生成受影响域文档
3. **踩坑沉淀分流**：可复用的平台用法进 `help/`；一次性踩坑进 `lessons/` 角色文件；「大家都知道但代码看不出来」的约定进 `architecture/implicit-contracts.md`；**人工测试发现的问题**按 `human-test-reports/` 机制经复盘提炼进 `lessons/`
4. 本索引只在**目录级变化**（新增/删除文档文件）时更新，不维护条目内容
5. **结构文档对账兜底**：变更随行（规则 1）仍是主防线；DocKeeper agent（周级 autopilot 触发）按 `aicoding-harness-audit` skill 对基线以来的增量做对账，可自动项走 MR，DDL 与存疑项提醒人工——人不需要主动维护本节之外的对账动作

## 结构文档同步状态（DocKeeper 维护，人不填）

| 上次对账基线 commit | 日期 | 方式 |
|---|---|---|
| （由 DocKeeper 首次对账时登记基线 = 当时 origin/master HEAD；此后每次对账在同一 MR 中前移） | | |

<!-- 分析指引：本节随骨架铺入即保留空表；值全部由 DocKeeper agent 读写（aicoding-harness-audit skill），人类与其它 agent 不维护此表 -->
