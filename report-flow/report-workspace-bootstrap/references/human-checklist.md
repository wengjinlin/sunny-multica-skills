# 人工操作清单（一次做完，完成后回复「完成」）

## A. GitLab 自托管连接（workspace 级，每工作区一次；已配过可跳过）

1. Multica 网页 → 设置 →「Git 代码托管（自托管）」→ 新建 GitLab 连接
2. 记下生成的 **webhook URL** 与 **secret**（后续 B 要用）

## B. GitLab webhook（项目级，每仓库一次）

1. GitLab 网页 → 仓库 `{{REPO_URL}}` → Settings → Webhooks → 新建：
   URL 与 secret 粘贴 A 步所得，勾选 **push events** 与 **merge request events**
2. 点 **Test Hook**（push events）确认返回 **HTTP 200**（401 = secret 未填或填错）
3. 老 GitLab（如 11.x）无 push options 建 MR 能力，hook 是 issue 自动关闭的唯一通路，不可跳过

## C. 环境变量注入（agent 无权代写，只能人工；入口：Multica 网页 → 该 agent 详情 → 环境变量）

| agent | 变量 | 用途 |
|---|---|---|
| Report-Developer | MVN_BIN | 本机 mvn 可执行文件绝对路径（Windows 形如 `/c/.../mvn.cmd`）；PATH 可用时可不填 |
| Report-Developer | JAVA_HOME | 本机 JDK 根目录（如 `/d/jdk1.8.0_171`），mvn 运行前置 |
| Report-Developer | NODE_BIN | 本机 node 可执行文件绝对路径（前端构建用）；纯后端任务可不填 |
| Report-DevOps | GITLAB_TOKEN | GitLab project access token，建 MR 用 |
| Mika | GITLAB_TOKEN | GitLab project access token，建区 harness MR 与后续运维用 |

配置提示：值从安全渠道获取，不要贴进 issue/评论/文档；agent 只在自己的运行进程中读取这些变量。

## 完成后

回复「完成」即继续（会自动验证 GitLab 连接与仓库可达）。
