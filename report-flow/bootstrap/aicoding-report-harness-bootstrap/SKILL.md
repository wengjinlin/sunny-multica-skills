---
name: aicoding-report-harness-bootstrap
description: 在业务仓库初始化报表链 harness 增量：把 skeleton/（约 8 个初始 md）拷入新增目录 docs/report-flow/（零侵入，仓库其他文件只读），push feature/init-report-harness 分支并走 GitLab API 自动建 MR，人审合并收口。TRIGGER：用户要求「建报表 harness」「初始化 docs/report-flow」「报表工作区增量入库」时使用。骨架结构权威源 = 本 skill 的 skeleton/（design.md §9.2）。
---

# aicoding-report-harness-bootstrap：报表 harness 增量初始化

把报表链对业务仓库的全部 harness 写入（`docs/report-flow/` 一个新增目录）初始化进仓库，走一次人工 MR。**零侵入铁律**（design.md §9.1）：只允许**新增** `docs/report-flow/`；仓库任何已有文件（`CLAUDE.md` / `AGENTS.md` / `docs/**` / `openspec/**` / hooks / CI 配置等）一律只读——发现需要改它们立即停下报告，不带条件绕过。

## 前置

1. `multica runtime list --output json` 确认 runtime 可用
2. `multica project list --output json` 确认项目已建且绑定业务仓库（未建 → 先跑 aicoding-project-init）
3. `multica repo checkout <REPO_URL>` 确保业务仓库有本地工作副本（幂等）
4. 向用户确认 **MR 目标分支**（如 `test`；项目上下文已有记录则复用不问）

## 执行流程

### 第 1 步：拷入骨架

1. 在业务仓库工作副本根目录创建 `docs/report-flow/`，将本 skill `skeleton/` 全部内容原样拷入（约 8 个初始 md：index / constitution / CHANGELOG / templates×2 / review-checklist / lessons/index / database-snapshots/README）
2. `git status` 自检：**diff 中只允许 `docs/report-flow/` 下的新增文件**，出现任何其他路径的改动 → 全部撤销并报告
3. `changes/` 与 `changes/archive/` 目录随首个 change 由 Report-PM 创建，不预建空目录

### 第 2 步：项目事实降级探测

仓库根无 `CLAUDE.md` 时：在报告中提醒用户 `docs/report-flow/constitution.md` 的「项目事实登记」节需人工填充（最小事实：模块清单 / 技术栈 / 构建命令 / 数据库方言 / MR 目标分支）——报表工作区自持，不为通用链代言。有 `CLAUDE.md` 则只读受益，不提醒。

### 第 3 步：分支 + push

```
git checkout -b feature/init-report-harness
git add docs/report-flow/
git commit -m "docs: 报表工作区 harness 增量（零侵入，仅新增 docs/report-flow/）"
git push origin feature/init-report-harness
```

（分支已存在且内容一致 → 视为已完成，跳到第 4 步。）

### 第 4 步：GitLab API 自动建 MR

- 请求体写 **JSON body 文件**（form 编码中文会 500）：title「报表工作区 harness 增量 init-report-harness」、source_branch `feature/init-report-harness`、target_branch 用前置收集值、description 注明「只新增 docs/report-flow/ 目录，零侵入，合并后报表链工作区就绪」
- `PRIVATE-TOKEN: $GITLAB_TOKEN`（读 Mika 自身进程环境变量；agent 只在自己进程里读 env，永不代写）
- API base 与 project-id 从项目上下文获取，不写死
- **建 MR 失败**（token 错 / 权限不足 / 401）：**不回滚 harness 产物**，降级为人工待办——报告分支名与人话建 MR 指引（GitLab 网页 → 创建 MR → 选该分支与目标分支）

### 第 5 步：报告

- 骨架文件清单（8 个 md 落位表）
- 分支 / MR 链接（或降级指引）
- 剩余人工待办：**人审合并 MR**（+ 无 CLAUDE.md 时补填「项目事实登记」节）
- 后续使用路径一句：日常报表需求向 Report-PM 发起 chat 澄清；超出报表边界的任务到通用链工作区发起（design.md §12）
- 回退说明：本目录是报表链对仓库的唯一持久写入，可单独 revert，不影响通用链工作区

## 铁律

- **零侵入**：只新增 `docs/report-flow/**`；其他一律只读（自检 diff，越界即撤）
- **中文传参**：GitLab API 请求体走 JSON body 文件，禁止 form 编码；CLI 含中文参数值经 multica_call.py 传 `@文件`（utf-8，用完即删）
- **敏感值**：token / 密码永不写入脚本参数、命令行、issue 评论或任何文档
- MR 自动建失败不回滚产物，降级人工

## 维护约定

- `skeleton/` 是 `docs/report-flow/` 初始结构的**唯一权威源**（design.md §9.2 为约束）：改骨架先改这里；建区后业务仓库内 `docs/report-flow/` 的演进走其自身 MR，不回灌本 skill
- 敏感值永不写入 skeleton
