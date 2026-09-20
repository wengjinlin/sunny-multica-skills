# REVIEW.md — 审查清单

> Reviewer 角色按本文件执行；Developer 自检时可参照。关卡内容按仓库技术栈在填充步按代码证据调整。

---

## 0. 触发条件（先决定走哪条路径）

| 场景 | 路径 | 关卡数 |
|---|---|---|
| 改动 < 50 行，无 SQL，无架构变化 | **quick-review** | 4 关 |
| 改动 ≥ 50 行 / 含 SQL / 涉及分层 / 涉及表结构 | **full-review** | 10 关 |
| 涉及 protected 路径（宪法 §10 清单） | **full-review + 人工复核** | 10 关 + 人类 |

<!-- 分析指引：50 行阈值与关卡数可按团队口味调整；protected 路径引用宪法 §10，勿在此重复清单（防双源漂移） -->

---

## 1. quick-review 清单（4 关）

适用：小改动、纯方法体修改、Bug 修复。

### 关 1：spec-align（规约对齐）

- [ ] 改动是否在 `tasks.md` 声明的 task 范围内？
- [ ] 是否实现了 `specs.md` 中所有相关 requirement？
- [ ] 有无超出 task 范围的"顺手改"？

**违反**：打回，要求拆分到独立 task。

### 关 2：risk-check（风险检查）

- [ ] 是否触及宪法 §10 保护目录？
- [ ] 是否引入新依赖？如有，是否在 `design.md` 声明？
- [ ] 是否修改公共字段（建表规范中的平台通用字段）？
- [ ] 是否影响日志切面等横切关注点？

**违反**：打回，要求走 full-review。

### 关 3：lesson-check（经验命中检查）

- [ ] 本次打回/审查发现的问题是否命中 `docs/lessons/` 角色文件已有条目？
  - 命中 → 该条目曝光不足，在 review-report 标注「建议晋升宪法」（同类第 2 次），@Mika 转人类确认
- [ ] 本次是否产生新教训？
  - 是 → review-report 末尾按 `docs/lessons/index.md` 条目格式追加条目（DevOps 归档时落盘到对应角色文件）
- [ ] 通过的改动抽查 Developer 是否读过相关 lesson（review-report 中引用条目编号）

### 关 4：archive（归档准备）

- [ ] issue 评论是否贴了路径 + diff 摘要？
- [ ] `tasks.md` 是否所有 task 状态置完成？
- [ ] 是否还有 `in_progress` 子 issue？

详细命令：`openspec validate <change-id>`。

---

## 2. full-review 清单（10 关）

适用：大改动、新功能、涉及架构或表结构。

### 关 1：verify（OpenSpec 校验）

- [ ] `proposal.md` / `specs.md` / `design.md` / `tasks.md` 四件套齐全？
- [ ] 顺序是否正确（proposal → specs → design → tasks）？
- [ ] `tasks.md` 每个 task 是否含 `id` / `title` / `files` / `parallel_group` / `depends_on`？

详细命令：`openspec validate <change-id>`。

### 关 2：review（通用代码审查）

- [ ] 命名是否符合 `docs/architecture/implicit-contracts.md`？
- [ ] 是否有未使用的 import / 变量？
- [ ] 是否有幻觉式重命名（缩写未查对照表）？
- [ ] 注释语言是否与团队约定一致？

### 关 3：{{ARCH_GATE_NAME}}（架构/分层审查）

{{ARCH_GATE_ITEMS}}

<!-- 分析指引：从宪法 §8 分层规则逐条转成检查项（每条一个 checkbox）；无分层传统的项目可删本关 -->

### 关 4：{{DATA_GATE_NAME}}（数据访问/SQL 审查）

{{DATA_GATE_ITEMS}}

<!-- 分析指引：DB 方言、DELETE/UPDATE 必须 WHERE、SELECT * 禁用、索引走查等按实际数据库填写；含 DDL 变更时必查：ddl.sql 为平铺 SQL 语句（无 PL/SQL 匿名块 / EXECUTE IMMEDIATE / DBMS_OUTPUT / 存在性预检查包装，触发器后不加 `/`）；无 DB 的项目可删本关。diff 级 SQL 安全四问必查：UPDATE/DELETE 是否必带 WHERE、有无字符串拼接 SQL、新查询是否可能索引失效、事务边界是否把远程调用圈进来 -->

### 关 5：security（安全审查）

- [ ] 是否有 SQL 拼接（字符串拼接 + SQL）？
- [ ] 是否有未脱敏的敏感字段（密码、token、证件号）？
- [ ] 鉴权豁免注解是否漏用/滥用？
- [ ] 文件上传是否限制大小 / 类型？
- [ ] 服务间调用是否带鉴权上下文？
- [ ] **LLM 信任边界**：外部返回 / LLM 产出 / 第三方数据是否未经结构·类型·范围校验直接入库或参与执行？
- [ ] **条件副作用**：同一条件分支内是否混合了校验逻辑与写操作（副作用应与校验分离）？

### 关 6：simplify（简化 + AI 冗余审查）

- [ ] 是否有重复代码可提取？
- [ ] 是否有过度抽象（"为未来设计"）？
- [ ] 函数是否超过 80 行？
- [ ] 圈复杂度是否超过 10？
- [ ] 注释是否冗余（描述 what 而不是 why）？
- [ ] **AI 冗余物**（AI 生成代码高发坏味道，重点排查）：过度防御（catch 后吞异常或不必要的空判）/ 死代码与永假分支 / 无用注释堆砌（复述代码的"Generated"式注释）/ 同一抽象重复发明（仓库已有工具类又写一个）/ 幻觉式重命名引用不存在的既有方法

### 关 7：qa（质量审查）

- [ ] 是否有单元测试？
- [ ] 测试是否覆盖关键路径（happy path + 至少 1 个边界）？
- [ ] 测试是否真实（不 mock 数据库连接，按团队约定）？
- [ ] 是否有日志（关键路径含 entry / exit / exception）？

### 关 8：prepare-review（准备 review 摘要）

- [ ] 生成 diff 摘要（不超过 10 行）
- [ ] 列出所有改动文件路径
- [ ] 列出跑了哪些校验命令及结果
- [ ] 列出剩余风险（已知但未解决的）
- [ ] 把以上贴到 issue 评论

### 关 9：lesson-check（经验命中检查）

- [ ] 本次打回/审查发现的问题是否命中 `docs/lessons/` 角色文件已有条目？
  - 命中 → 该条目曝光不足，在 review-report 标注「建议晋升宪法」（同类第 2 次），@Mika 转人类确认
- [ ] 本次是否产生新教训？
  - 是 → review-report 末尾按 `docs/lessons/index.md` 条目格式追加条目（DevOps 归档时落盘到对应角色文件）
- [ ] 通过的改动抽查 Developer 是否读过相关 lesson（review-report 中引用条目编号）

### 关 10：archive（归档）

- [ ] `tasks.md` 全部 task 完成？
- [ ] 所有子 issue 状态置 `in_review` 或 `done`？
- [ ] `openspec/changes/{change-id}/` 移到 `openspec/changes/archive/`？
- [ ] 是否更新 `docs/architecture/implicit-contracts.md`（如发现新缩写/新约定）？

---

## 3. Reviewer 工具权限

**仅允许**：

- `Read(**)` / `Glob(**)` / `Grep(**)`
- 只读 git（`git status` / `git diff` / `git log`）

**禁止**：

- `Edit(**)` / `Write(**)` —— Reviewer 不改代码，打回由 Developer 改
- 构建/测试命令 —— 跑测试由 Tester 负责

---

## 4. 打回规则

### 4.1 打回必须附修改建议

打回评论格式：

```
## 打回原因
<关名>：<具体违反项>

## 修改建议
1. <文件路径:行号>：<建议>
2. ...

## 重新提交条件
- <必须解决的项>
```

### 4.2 升级规则

- 同一 task 连续 **2 次打回** → 升级到人类 reviewer
- 升级评论格式：`@human-reviewer 需人工介入：T<id> 已 2 次打回，原因：...`

### 4.3 Reviewer 不能做的事

- 不能改代码（只能打回）
- 不能直接 merge（走 MR 由人类合并）
- 不能跳关（必须按顺序，除非 task 明确豁免）
- 不能凭经验判断（必须查 `docs/architecture/implicit-contracts.md`）

### 4.4 结论置信度分级（review-report 每条结论标注）

| 置信度 | 判据 | 动作 |
|---|---|---|
| 高 | grep / 只读命令可复现的证据 | 直接定论，可作打回依据 |
| 中 | 模式聚合 / 启发式推断 | 标注「存疑」列出，允许一定噪声 |
| 低 | 需理解视觉/业务意图才能确认 | 列为「可能——请人工验证」，**不得作为打回唯一依据** |
