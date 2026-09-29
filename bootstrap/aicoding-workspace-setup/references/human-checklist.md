# 第④步人工窗口清单（一次做完，回复「完成」继续）

> 执行到本步 = 技能已入库、角色 agent 已建好，以下网页操作均可进行。
> 全部完成后回复「完成」；卡住哪条就说明哪条，Mika 给排查指引后幂等重验，不弃流程。
> **值（token / 密码 / secret）走安全渠道，永不贴进对话、issue 或评论**——页面只填值，不截图不粘贴。

## A. GitLab 自托管连接（workspace 级，每工作区一次）

1. Multica 网页 → 设置 →「Git 代码托管（自托管）」→ 新建 GitLab 连接
2. 记下生成的 **webhook URL** 与 **secret**（后续 B 要用）
3. 注意：`multica repo add/checkout` 不会注册或重建 webhook——此连接只能网页配置

## B. GitLab webhook（仓库级，仓库 `{{REPO_URL}}` 每仓库一次）

1. GitLab 网页 → 该仓库 Settings → Webhooks → 新建：URL 与 secret 粘贴 A 步所得，勾选 **push events** 与 **merge request events**
2. 点 **Test Hook**（push events）确认返回 **HTTP 200**（401 = secret 未填或填错）
3. 老 GitLab（如 11.x）无 push options 建 MR 能力，hook 是 close intent 的唯一通路，不可跳过

## C. 环境变量注入（agent 级；入口：Multica 网页 → 该 agent 详情 → 环境变量）

> agent 只在自己的运行进程中读取这些变量；agent 无权写 env，本节只能人工完成。
> 变量名与用途可直接复制；**值从安全渠道获取，不入对话、issue、评论或任何文档**。

### 必配（不配则对应环节降级或失败）

| agent | 变量 | 用途 |
|---|---|---|
| Mika | GITLAB_TOKEN | GitLab project access token，第⑦步自动建 harness MR 用 |
| DevOps | GITLAB_TOKEN | GitLab project access token，建 MR 用 |
| DocKeeper | GITLAB_TOKEN | GitLab project access token，文档对账 MR 用 |
| Tester | TEST_ACCOUNT | 测试账号名（浏览器 QA 登录用） |
| Tester | TEST_PASSWORD | 测试账号密码（敏感：仅环境变量流转） |
| Tester | TEST_ROLE | 测试账号挂靠的角色名——权限系统 UI 绑定菜单/按钮的目标角色；须与账号实际角色一致，否则菜单不可见 |
{{DB_PASSWORD_HINT}}

### 选配（PATH 可用时可不填；构建/测试命令解析用）

| agent | 变量 | 用途 |
|---|---|---|
| Developer | MVN_BIN | 本机 mvn 可执行文件绝对路径（Windows 形如 /c/.../mvn.cmd） |
| Developer | JAVA_HOME | 本机 JDK 根目录（如 /d/jdk1.8.0_171） |
| Developer | NODE_BIN | 本机 node 可执行文件绝对路径（前端构建用）；纯后端项目不填 |
| Tester | MVN_BIN / JAVA_HOME / NODE_BIN | 同上（测试命令解析用） |

> 权威源：`aicoding-agent-bootstrap` 的 `agents/*.md` 各文件「## 自定义 env」节——本表是快照，配置文件更新后以文件为准，改配置须同步改本表。例外：**Mika 的 GITLAB_TOKEN 行与条件项 DB_PASSWORD 行归 aicoding-workspace-setup 编排层所有**（agents/ 目录无 Mika 配置文件，DB_PASSWORD 是 harness 条件项），不在 agents 同步范围。
