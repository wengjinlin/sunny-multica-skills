---
name: aicoding-project-init
description: 初始化 Multica 项目：引导人工完成 GitLab 集成与 token 注入，自动验证，验证通过后创建 project 并绑定仓库资源。TRIGGER：用户要求「初始化项目 / 建项目绑仓库 / 配置 GitLab 集成 / 新工作区建项目」时使用。人工清单与验证流程在本文，项目描述模板在 project.md。
---

# aicoding-project-init：人工集成 → 自动验证 → 建项目

本 skill 串联三类事项：**人工网页操作**（GitLab 连接 / webhook / token）→ **自动验证**（通过 DevOps 一次性任务）→ **自动建项目**（create + 资源绑定 + description 模板）。

前置依赖：aicoding-agent-bootstrap 已跑完（验证环节需要 DevOps agent 及其 GITLAB_TOKEN）。

## 执行流程

### 第 0 步：前置检查（幂等探测）

1. `multica runtime list --output json` 确认 runtime 可用
2. `multica agent list --output json` 确认 **DevOps** 存在并记下 UUID（不存在 → 提示先跑 aicoding-agent-bootstrap，终止）
3. `multica project list --output json` 探测同名 project：已存在 → 进入**对齐模式**（只补资源绑定与 description，不重建），记下 project-id
4. 向用户确认：项目名 / 仓库 URL（下称 REPO_URL）

### 第 1 步：输出人工三事项 checklist

向用户逐条列出（区分 workspace 级与项目级），等待用户回复「完成」：

**A. GitLab 自托管连接（workspace 级，每工作区一次）**
1. Multica 网页 → 设置 →「Git 代码托管（自托管）」→ 新建 GitLab 连接
2. 记下生成的 **webhook URL** 与 **secret**（后续 B 要用）
3. 注意：`multica repo add/checkout` 不会注册或重建 webhook——此连接只能网页配置

**B. GitLab webhook（项目级，每仓库一次）**
1. GitLab 网页 → 该仓库 Settings → Webhooks → 新建：
   URL 与 secret 粘贴 A 步所得，勾选 **push events** 与 **merge request events**
2. 点 **Test Hook**（push events）确认返回 **HTTP 200**（401 = secret 未填或填错）
3. 老 GitLab（如 11.x）无 push options 建 MR 能力，hook 是 close intent 的唯一通路，不可跳过

**C. token 注入（项目级）**
```
multica agent env set <DevOps-UUID> --custom-env-file <文件>
# 文件内容：{"GITLAB_TOKEN": "<值>"}   # 值从安全渠道获取，不入库不入评论
```
（agent 无权执行 env set，必须人工；命令可直接复制）

### 第 2 步：自动验证（DevOps 一次性任务）

用户回复完成后，建一次性验证 issue（assign DevOps，评论用 `[@DevOps](mention://agent/<uuid>)` 触发，UUID 以 agent list 为准），任务描述：

```
[verify] GitLab 集成验证（一次性，完成即 done）
用你的 env 中 GITLAB_TOKEN 执行以下只读验证，评论回报每项结果后置 done：
1. GET /api/v4/user（Header: PRIVATE-TOKEN）→ 回报 HTTP 码 + username
2. 由 repo URL 取 project：GET /api/v4/projects/<url-encoded-path>（或 search）→ 回报 project id
3. GET /api/v4/projects/<id>/hooks → 回报：hook 总数、各 hook 的 url 域名部分、
   push_events / merge_requests_events 布尔值（只报元数据，不报 secret/token）
```

**结果判定**：
| 现象 | 结论 | 动作 |
|---|---|---|
| user 返回 401 | C 未生效或值错 | 告知用户检查 token，重验 |
| hooks 为空 / 无 URL 指向 Multica host | B 未生效 | 告知用户检查 hook，重验 |
| 事件布尔为 false | B 勾选不全 | 告知用户补勾，重验 |
| 全部通过 | 集成就绪 | 进第 3 步 |

- A（连接本体）无 CLI 可查——由 hook 的存在且 Test 非 401 间接覆盖
- 重验幂等：旧验证 issue 已 done 则新建一个；不要复用已关闭 issue

### 第 3 步：注册仓库 + 创建项目 + 绑定资源

1. **注册到 workspace 仓库表**（agent 的 Repositories 可用域；幂等，已有不重复）：
   `multica repo add <REPO_URL> --description "<项目名>仓库"`
2. `project.md` 模板替换 `{{PROJECT_NAME}}` / `{{REPO_URL}}`，写 utf-8 临时文件（description，禁命令行内联中文）
3. 创建（github_repo 资源随 `--repo` 自动绑定）：
   ```
   multica project create --title <项目名> --repo <REPO_URL> \
     --description "$(cat proj.tmp)" --status in_progress --output json
   ```
   记录 project-id。对齐模式则跳过 create，只做 `multica project update <id> --description "$(cat proj.tmp)"`
4. 确认两处落点：`multica repo list`（应含 REPO_URL）+ `multica project resource list <project-id> --output json`（应见 github_repo → REPO_URL）

### 第 4 步：报告

- 项目 UUID + 可导航链接格式：`[<项目名>](mention://project/<project-id>)`
- 验证证据摘要（DevOps 回报的 whoami / hook 状态）
- 后续提示（未完成层提醒）：仓库 harness 重建（harness-kit）、编排层（aicoding-orchestration-bootstrap）、角色层（aicoding-agent-bootstrap）

## 铁律

- secret / token 永不写入本 skill、issue 评论或任何文件——checklist 里只写获取方式
- 验证失败**不阻断流程框架**：报告差异、等用户修正、幂等重验
- 已存在的 project 不重建，只对齐 description 与资源

## 维护约定

- `project.md` 是项目描述模板（指针型：只导航不维护细节），改布局须同步
- 各工作区 GitLab 版本差异（hook 路径/Test 按钮位置）以用户现场为准，本 skill 只约束验证判据
