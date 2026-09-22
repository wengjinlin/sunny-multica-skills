---
name: aicoding-project-init
description: 初始化 Multica 项目：引导人工完成 GitLab 集成与 token 配置，chat 内自动验证（repo 注册 + checkout 拉取），验证通过后创建 project 并绑定仓库资源；全程 chat 会话内完成，不开 issue。TRIGGER：用户要求「初始化项目 / 建项目绑仓库 / 配置 GitLab 集成 / 新工作区建项目」时使用。人工清单与验证流程在本文，项目描述模板在 project.md。
---

# aicoding-project-init：人工集成 → 自动验证 → 建项目

本 skill 串联三类事项：**人工网页操作**（GitLab 连接 / webhook / token）→ **chat 内自动验证**（repo 注册 + checkout 拉取）→ **自动建项目**（create + 资源绑定 + description 模板）。

前置依赖：aicoding-agent-bootstrap 建议先跑完（DevOps agent 及其 GITLAB_TOKEN 供后续建 MR 用）；本 skill 验证环节在 chat 内执行，不依赖 DevOps。

## 执行模式（重要）

- **全程在当前 chat 会话内直接执行**：人工 checklist 等待、验证命令、建项目操作都在本会话完成——**不开 issue、不派子任务给其他 agent**。issue 子任务完成后没有编排链路自动回到本流程，会断链等人工提醒，这是明确禁止的工作方式
- 每步完成在 chat 输出简短结果让用户看到进度；只在需要用户提供信息或人工操作时停下等待

> 安装链顺序：aicoding-importing-skills → aicoding-agent-bootstrap →（人工 env 注入，如 GITLAB_TOKEN）→ **本 skill** → aicoding-orchestration-bootstrap → aicoding-harness-bootstrap

## 中文传参铁律

`--description` / `--title` 等参数**没有** `--xxx-file` 变体；`$(cat file)` 把中文内联进命令行时，PowerShell / cmd / GBK 代码页会把 UTF-8 内容转成乱码入库。**凡含中文的参数值一律经 multica_call.py 传 `@文件`**，禁止 `$(cat)` 内联、禁止命令行直写中文。

执行前先把以下助手脚本写入工作目录 `multica_call.py`：

```python
# 用法：python multica_call.py <子命令...> --description @<utf-8 文件路径>
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

以 `@` 开头的参数值被替换为该 utf-8 文件全文；UUID / URL / 数字等纯 ASCII 参数直接传。临时文件用完即删。

## 执行流程

### 第 0 步：前置检查（幂等探测）

1. `multica runtime list --output json` 确认 runtime 可用
2. `multica agent list --output json` 记录 **DevOps** 状态（不存在 → 提醒安装链顺序应先跑 aicoding-agent-bootstrap，但**不终止**：本 skill 验证不依赖 DevOps，项目可先建，DevOps 建好后补配 GITLAB_TOKEN 即可）
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

**C. token 配置（项目级）**

给 DevOps agent 配置环境变量 **GITLAB_TOKEN**（GitLab project access token，建 MR 用）——入口：Multica 网页 → DevOps agent 详情 → 环境变量。值从安全渠道获取，不入库不入评论。（agent 无权写 env，必须人工配置）

### 第 2 步：自动验证（本会话直接执行，不开 issue）

用户回复完成后，**在当前 chat 会话内直接执行**以下验证（不建 issue、不转派 DevOps——issue 子任务完成后不会自动回到本流程，会断链）：

1. `multica repo add <REPO_URL> --description @repodesc.tmp`（说明文字「<项目名>仓库」写 utf-8 临时文件；幂等，已存在不重复；失败多为 A 步 GitLab 连接未生效或 URL 有误）
2. `multica repo checkout <REPO_URL>` 拉取仓库——成功 = A（workspace GitLab 连接）+ 仓库可达验证通过

**结果判定**：
| 现象 | 结论 | 动作 |
|---|---|---|
| repo add / checkout 报连接或认证失败 | A 未生效或 REPO_URL 有误 | 告知用户检查连接与 URL，重试 |
| checkout 拉取超时 / 网络错误 | 仓库不可达 | 告知用户检查网络，重试 |
| 成功 | 集成就绪 | 进第 3 步 |

- **webhook（B）**：无 CLI 可查，以用户在 B 步点 Test Hook 得到 HTTP 200 为准（人工已验证）；其影响面是 MR close intent，不阻塞建项目
- **token（C）**：DevOps 的 GITLAB_TOKEN 本步不验证（执行会话读不到其他 agent 的环境变量）——留待 DevOps 首次建 MR 时自然验证，401 届时再检查配置
- 重验幂等：直接重复上述两条命令即可，均可安全重跑

### 第 3 步：注册仓库 + 创建项目 + 绑定资源

1. **注册到 workspace 仓库表**（agent 的 Repositories 可用域；幂等，已有不重复）：
   `multica repo add <REPO_URL> --description @repodesc.tmp`（说明文字写 utf-8 临时文件）
2. `project.md` 模板替换 `{{PROJECT_NAME}}` / `{{REPO_URL}}` 写 `proj.tmp`；项目名写 `title.tmp`（均 utf-8，见「中文传参铁律」）
3. 创建（github_repo 资源随 `--repo` 自动绑定）：
   ```
   python multica_call.py project create --title @title.tmp --repo <REPO_URL> \
     --description @proj.tmp --status in_progress --output json
   ```
   记录 project-id。对齐模式则跳过 create，只做 `python multica_call.py project update <id> --description @proj.tmp`
4. 确认两处落点：`multica repo list`（应含 REPO_URL）+ `multica project resource list <project-id> --output json`（应见 github_repo → REPO_URL）

### 第 4 步：报告

- 项目 UUID + 可导航链接格式：`[<项目名>](mention://project/<project-id>)`
- 验证证据摘要（repo checkout 结果；webhook 以用户 Test Hook HTTP 200 为准；DevOps 的 GITLAB_TOKEN 未验证——首次建 MR 时自然验证）
- 后续提示（未完成层提醒）：编排层（aicoding-orchestration-bootstrap）、仓库 harness（aicoding-harness-bootstrap）

## 铁律

- secret / token 永不写入本 skill、issue 评论或任何文件——checklist 里只写获取方式
- 验证失败**不阻断流程框架**：报告差异、等用户修正、幂等重验
- 已存在的 project 不重建，只对齐 description 与资源

## 维护约定

- `project.md` 是项目描述模板（指针型：只导航不维护细节），改布局须同步
- 各工作区 GitLab 版本差异（hook 路径/Test 按钮位置）以用户现场为准，本 skill 只约束验证判据
