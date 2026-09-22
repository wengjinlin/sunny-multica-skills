---
name: aicoding-harness-bootstrap
description: 在全新仓库建设 harness：铺骨架（宪法/协作/审查/文档/hooks/openspec）→ 代码分析填充 → feature 分支 push → 人工 MR。TRIGGER：「建设仓库 harness」「初始化新项目仓库」「铺 harness」。骨架在 skeleton/，项目内容靠代码分析生成。不建仓库侧 skills 与 commands（skill 全在 Multica 侧维护）。
---

# aicoding-harness-bootstrap：新仓库 harness 建设

**范围声明**：
- **建**：`CLAUDE.md` / `AGENTS.md` / `REVIEW.md` / `docs/index.md`（导航） / `docs/architecture/{index.md + implicit-contracts.md}` / `docs/product/index.md` / `docs/database/{index.md + tables/_template.md}` / `docs/standards/{api,database,testing}.md` / `docs/templates/design-review-template.md`（前端设计人审模板） / `docs/help/{index.md + 7 篇 sunny 能力文档 + _template.md}` / `docs/lessons/{index.md + 各角色 md}` / `docs/human-test-reports/{index.md + _template.md}`（人工测试验证报告，人类维护 agent 只读） / `.claude/hooks/guard_write.py` / `openspec/config.yaml`
- **不建**：仓库侧 skills（全部在 Multica 侧维护，由 bootstrap skills 复现）、`.claude/commands/`（multica 架构下无用）

## 执行模式（重要）

- **全程在当前 chat 会话内直接执行**：仓库 checkout / 骨架铺设 / 代码分析 / commit / push 都由执行 agent 在本会话直接完成——**不开 issue、不派子任务给其他 agent**。issue 子任务完成后没有编排链路自动回到本流程，会断链等人工提醒，这是明确禁止的工作方式；也不要以「chat 会话不做仓库操作」的默认习惯转派
- 分步推进时每步在 chat 输出简短进度（骨架 N 文件、分析填充进度、commit 结果）；只在需要用户提供信息（数据库密码确认、MR 目标分支等）时停下等待

## 执行流程

### 第 0 步：前置

1. `multica repo checkout <REPO_URL>`（或确认仓库已在本工作区），`git fetch origin`
2. 基于 `origin/master` 建 `feature/init-harness` 分支
3. **幂等检查**：仓库已有 CLAUDE.md/AGENTS.md → 转**对齐模式**（逐文件对照骨架补缺节，不覆盖本地定制），报告差异后收工
4. **数据库预检（仅收集连接信息，不执行导出——导出在第 1 步骨架铺完、第 2 步分析时才跑）**：
   - 判有库/无库：扫 pom 驱动依赖（oracle / postgresql / mysql / sqlserver JDBC 驱动）+ `application*.yml` / `*.properties` 的 datasource；判不了 → 问用户
   - 无库 → 报告注明「项目无数据库」，第 1 步铺完后删除 `docs/database/` 两文件并在 `docs/index.md` 去掉对应两行
   - 有库 → 按 aicoding-db-schema-export 第 1 步优先级链收集非敏感参数（agent env → 已有生成声明 → **自动读 test 环境配置**），缺哪项问哪项
   - **密码分两路**：配置文件数据源里有密码字段 → 向用户确认一次「密码就用配置里那个？」，确认后第 2 步在生成声明登记**密码位置指针**（非敏感），首导直接读配置值（单次命令用完即弃），change 期 Developer **零 env**；配置里没有密码 → 用户 chat 提供一次（单次命令 env，用完即弃），并在第 5 步报告提醒注入 `DB_PASSWORD`（命令见报告）
   - 连接信息或密码拿不到 → 用户可改选「人工在能连库的机器跑脚本回传 `schema_dump.json`」；仍不行 → 记入第 5 步人工待办，**不得产出空的 database 文档**

### 第 1 步：铺骨架

把 `skeleton/` 下全部文件按原目录结构拷入仓库根：

```
CLAUDE.md
AGENTS.md
REVIEW.md
docs/index.md                  # 文档导航 + 按角色必读顺序 + 维护规则
docs/architecture/index.md     # 业务模块对应表（模块定位字典）+ 高风险区域/ADR/技术债
docs/architecture/implicit-contracts.md
docs/product/index.md          # 业务域划分 / 术语表 / 状态机 / 业务校验铁律
docs/database/index.md         # 全库表清单 + 再生成规则（无数据库的项目删除）
docs/database/tables/_template.md  # 表详情格式规范
docs/standards/api.md          # 接口规范 + 评审清单
docs/standards/database.md     # 数据库规范 + 变更检查清单（无数据库的项目删除）
docs/standards/testing.md      # 测试规范（新旧代码口径）
docs/templates/design-review-template.md  # 前端设计人审模板（非 sunny 系前端按第 2 步指引重写）
docs/help/                     # 能力清单 + 7 篇 sunny 能力文档（po/s3/lock/sendoa/import/export/kafka）+ _template.md；非 sunny 体系项目按第 2 步指引重写
docs/lessons/index.md          # 机制 + 角色索引（条目只写角色文件，索引不维护条目）
docs/lessons/_template.md      # 角色文件模板 → 填充时按角色清单复制为 {Role}.md
docs/human-test-reports/index.md    # 人工测试验证报告机制 + 记录索引（人类维护，agent 只读；归因在复盘做）
docs/human-test-reports/_template.md  # 报告模板 → 测试者复制为 日期-分支名.md（只写现象+处理+文件，不归因）
hooks/guard_write.py           → 落位到目标仓库 .claude/hooks/guard_write.py
openspec/config.yaml
```

（骨架内不直接建 `.claude/` 路径——部分运行环境对 `.claude/hooks` 有写保护；落位复制在 第 3 步 hook 安装时执行。）

### 第 2 步：代码分析填充（核心）

逐文件消灭 `{{占位符}}`。**每条填入内容必须有代码证据**，分析来源：

| 占位目标 | 分析方法 |
|---|---|
| 项目定位/模块表 | 根目录扫描 + 各模块 `pom.xml` / `package.json` |
| 技术栈/端口 | 依赖清单 + 配置文件端口（**只读**，不抄凭据） |
| 构建命令与工具路径 | §4 抄 pom/package.json scripts 的命令语义（机器无关）；§5 写自解析协议（PATH → agent env 候选验证 → 常见位置 glob 探测 → 人工待办），**禁写本机路径快照**；填完在当前 runtime 按链完整实测 |
| 分层规则/命名前缀 | 抽样 controller/service/mapper/entity 归纳（每类 ≥3 例） |
| 平台包优先级 | 二方包依赖清单（如 `com.sunny:*`），能力→包映射表 |
| 保护目录 | 配置/DB 脚本实际路径，与 hook 默认清单对齐 |
| 拼音/缩写对照 | 业务包名扫描；无缩写则在 implicit-contracts.md 注明「不适用」 |
| 基础设施 | yml 只读提取（地址可写，**凭据永不写**） |
| MR 目标分支 | 问用户（如 `test`）；角色速查表从 Multica `agent list` 对齐 |
| lessons 角色文件 | 按 Multica `agent list` 角色清单，从 `_template.md` 复制生成 `docs/lessons/{Role}.md`，同步填 index 角色索引与 AGENTS.md §7 读写矩阵 |
| 业务模块对应表（模块定位字典） | controller/service 目录名 × entity 表名 × 数据库表前缀三方对齐；业务域清单与 product/index.md 同刷 |
| 产品规则（业务域/术语/状态机） | 从 controller 注释、字典表、表注释归纳；术语含拼音缩写展开 |
| standards 三篇详单 | 从 CLAUDE.md 红线 + 代码抽样（每类 ≥3 例）+ implicit-contracts 差异生成；宪法红线 ↔ standards 详单两向引用 |
| design 人审模板 | sunny 系前端直接沿用；非 sunny 系（无 SunnyForm/EditGrid/权限字典体系）按项目组件体系整体重写表头与封闭枚举，保留「逐字段选型 + 偏离声明」结构 |
| docs 导航必读顺序 | 按 Multica `agent list` 角色清单生成各角色读单，与各 agent 指令「项目上下文」读单一致 |
| 数据库表文档 | 见下方「数据库文档生成」——数据字典导出 → 按 `tables/_template.md` 格式化 |

**禁止**：无证据的规则、猜测的业务语义、密钥/密码/token 明文入任何文件。

**数据库文档生成**（填充 `docs/database/` 两文件时执行）：

- 一律走工作区 **aicoding-db-schema-export** skill（连接信息收集 → 固定脚本导出 → 按 `tables/_template.md` 格式化，结果一致性由脚本保证）；**禁止**临时手写连接代码或 SQL 导出
- **前置硬校验**：本会话必须能 Skill 调用 aicoding-db-schema-export（由 workspace agent 执行本 skill 时须先给它分配该 skill）——调不到 = **阻断**，报告贴补齐命令（`multica skill import ...` / `multica agent skills add ...`）后停，禁止跳过继续、禁止手写 SQL 顶替
- 连接信息以第 0 步预检收集结果为准；到本步仍不就绪 → 停下二选一问用户：提供密码 / 人工在能连库机器跑 skill 第 2 步命令回传 `schema_dump.json`（从 skill 第 3 步继续）
- 连不上库：按该 skill 的降级路径——人工在能连库的机器跑同一脚本、回传 `schema_dump.json`，仍是脚本导出
- 域划分与 `product/index.md` 业务域对齐；无前缀归属的杂项表进 `_unmapped` 域

### 第 3 步：hook 安装与验证

1. `guard_write.py` 落位 `.claude/hooks/`，保护清单与本仓库第 2 步分析一致（默认 application*.yml / db / sql / settings.xml / pom.xml，按需增删 pattern）
2. 自测一次：尝试写保护路径应被 block，写普通路径应放行

### 第 4 步：commit + push

`feature/init-harness` 一次提交，message 说明各文件用途；**立即 push**（未 push 的本地分支跨 runtime 不可见）。

### 第 5 步：报告

- 文件清单表：骨架文件 × 填充状态（全部消灭占位符才可 commit）
- **数据库状态行（含库项目必列）**：已生成（域数/表数，随 harness 一次提交；密码在配置里的注明「密码位置已登记生成声明，change 期 Developer 零 env」）/ 未生成（原因 + 补齐待办：提供连接重跑，或人工跑脚本回传 JSON）；密码不在配置的加提醒「change 期 Developer 重生成需配置环境变量 DB_PASSWORD（数据库密码）——入口：Multica 网页 → Developer agent 详情 → 环境变量；值不入评论」（人话格式，无命令）
- **人工待办**：MR 创建 + 首版人审——宪法首版必须人审，它约束后续所有 agent
- 提示后续微调路径：文档演进走仓库 MR；结构变更回写本 skill 的 skeleton/

## 铁律

- 只在 feature 分支动工，禁止直推 master / 保护分支
- 占位符未消灭的文件不得 commit（防半成品入库）
- 敏感值（密码/token/secret）永不写入任何 harness 文件

## 维护约定

- `skeleton/` 是**结构**权威源：harness 章节布局变更须回写；项目内容演进不回写（那是各仓库自己的 MR，漂移由 aicoding-harness-audit skill + DocKeeper 周级对账兜底）
- 与其他 bootstrap 的边界：角色/编排/Multica 项目配置分别归 aicoding-agent-bootstrap / aicoding-orchestration-bootstrap / aicoding-project-init，本 skill 只管仓库内文件
