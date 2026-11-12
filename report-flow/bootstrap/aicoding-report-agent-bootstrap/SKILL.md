---
name: aicoding-report-agent-bootstrap
description: 在报表专用工作区批量创建 4 个 Report-* 角色 agent（Report-PM / Report-Developer / Report-Reviewer / Report-DevOps）。TRIGGER：用户要求「建报表 agent」「按 report-flow/agents 建 agent」「部署报表角色层」时使用。框架不含 agent 内容——配置维护在本 skill 的 agents/ 目录，文件数即创建数；通用链 6 角色不建。
---

# aicoding-report-agent-bootstrap：按配置批量创建报表角色 agent

本 skill 是 **aicoding-agent-bootstrap 框架的报表裁剪版**：读取 `agents/` 目录下的 4 个配置文件，逐个创建 agent 并应用全部配置。agent 内容不写死在框架里——增删报表角色 = 增删 `agents/*.md` 文件（改动须同步回写上游权威源 `report-flow/agents/`，见文末维护约定）。

与通用版差异：**只建 4 个 Report-\***（文件数即创建数）；Mika 是工作区内置默认 agent，不创建（第 0 步只找 UUID 供 `{{MIKA_ID}}` 替换）；不建通用链 6 角色。

## 配置文件格式（agents/*.md）

每个文件分两部分：

**frontmatter（标量设置 → agent create 参数）**

| 字段 | 对应参数 | 空值含义 |
|---|---|---|
| `name` | `--name` | 必填 |
| `description` | `--description` | — |
| `model` | `--model` | 空 = 跟随 runtime 默认（省略该参数） |
| `thinking_level` | `--thinking-level` | 空 = 默认（省略） |
| `service_tier` | `--service-tier` | 空 = 默认（省略） |
| `max_concurrent_tasks` | `--max-concurrent-tasks` | — |
| `visibility` | `--visibility` | `workspace` = 全员可触发 |

**正文固定四节**

| 节 | 内容 | 应用方式 |
|---|---|---|
| `## 指令` | instructions 全文；`{{MIKA_ID}}` 为占位符 | 写 utf-8 临时文件，经 multica_call.py 传 `--instructions @instr.tmp`（见「中文传参铁律」） |
| `## 分配 skill` | 每行一个 skill 名（可带括号说明），或「（无）」 | `multica agent skills add`（按名字解析 id） |
| `## 分配 MCP` | 一个 JSON 对象（mcpServers 结构），或「（无）」 | 写临时文件后 `--mcp-config-file` |
| `## 自定义 env` | 每行一个 `KEY # 用途说明`，或「（无）」 | **纯人工配置，agent 不执行任何 env 写操作**（实测 agent 凭据调 CLI env get/set 一律被拒——env 是人工通道）：把「变量名 + 用途」整理成人类可读待配置清单进总体报告人类待办，由人工在 Multica 网页配置；agent 运行时从自身进程环境变量读取 |

前置依赖：4 个业务 skill（lookup-v2/v3、config-auth-v2/v3）应已入库（aicoding-skills-bootstrap 只拉这 4 个）——缺失不阻断创建，走缺失登记。

## 中文传参铁律

`--instructions` / `--description` 等参数**没有** `--xxx-file` 变体；`$(cat file)` 把中文内联进命令行时，PowerShell / cmd / GBK 代码页会把 UTF-8 内容转成乱码入库。**凡含中文的参数值一律经 multica_call.py 传 `@文件`**，禁止 `$(cat)` 内联、禁止命令行直写中文。

执行前先把以下助手脚本写入工作目录 `multica_call.py`：

```python
# 用法：python multica_call.py <子命令...> --instructions @<utf-8 文件路径>
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

### 第 0 步：前置

> 报表分步链顺序：aicoding-skills-bootstrap（只拉 4 个业务 skill）→ **本 skill** →（人工 env 注入）→ aicoding-project-init → aicoding-report-orchestration-bootstrap → aicoding-report-harness-bootstrap。项目在本 skill 之后才创建，未建属正常。

1. `multica runtime list --output json` 取 runtime-id（本工作区需已 setup daemon）
2. `multica agent list --output json` 找到本工作区 Mika 的 UUID，记为 **NEW_MIKA_ID**
3. `multica agent list` 记录现有 agent 名单（幂等基准）
4. 列出本 skill `agents/` 目录全部 `*.md`——文件数 = 待创建数（报表版 = 4），逐个处理

### 第 1 步：逐文件创建

对每个配置文件：

1. **幂等检查**：同名 agent 已存在 → **不创建，改走同步模式（只做三个动作）**：
   - **更新指令**：「## 指令」节（`{{MIKA_ID}}` 替换后）写 utf-8 临时文件，`python multica_call.py agent update <id> --instructions @instr.tmp`——配置文件指令整体覆盖
   - **对齐分配 skill**：`multica agent skills set <id> --skill-ids <按配置文件解析到的全部id>`（set = 替换式对齐，配置文件是权威源）；配置为「（无）」则**不动现有挂载**；缺失 skill 照旧只登记不阻断
   - **对齐分配 MCP**：「## 分配 MCP」非「（无）」时 `multica agent update <id> --mcp-config-file <file>`；「（无）」则不动
   - **其余字段一律不碰**——已存在的 agent 视为本地已有定制
2. **准备指令**：取「## 指令」节全文，`{{MIKA_ID}}` 全部替换为 NEW_MIKA_ID，写 utf-8 临时文件（如 `./instr.tmp`）
3. **创建**：
   ```
   python multica_call.py agent create --name <name> --description @desc.tmp \
     [--model <model>] [--thinking-level <t>] [--service-tier <tier>] \
     --max-concurrent-tasks <n> --visibility workspace \
     --runtime-id <runtime-id> --instructions @instr.tmp
   ```
   记录新 UUID。frontmatter 空字段直接省略参数。
4. **分配 skill**：节内非「（无）」时按 name 解析 id 后 `multica agent skills add <新agent-id> --skill-ids <存在的id列表>`；**缺失的 skill 不阻断、不重试**——记入缺失登记
5. **分配 MCP**：非「（无）」时 JSON 写临时文件，创建时 `--mcp-config-file`；解析不到只记缺失登记
6. **env**：不执行任何 env 读写——逐 key 整理成人类可读清单列入总体报告人类待办

### 第 2 步：总体报告（全部文件处理完后统一输出）

**创建结果表**：agent 名 / 新 UUID（或「已存在 → 同步了 指令/skill/mcp 三项」）/ max-concurrent / 已应用的 skill 数

**缺失内容总体报告**（无缺失也要显式写「无缺失」）：

```
## 缺失内容登记
| agent | 缺失项 | 类型 | 补齐命令 |
|---|---|---|---|
统计：N/4 个 agent 创建（或已存在）；K 项分配缺失
```

**人类待办**（env 配置——只能人工完成；不给命令，变量名与说明可直接复制）：
```
以下 agent 需要配置环境变量（入口：Multica 网页 → 该 agent 详情 → 环境变量；本机 CLI 亦可）：
- Report-Developer：MVN_BIN（本机 mvn 绝对路径）/ JAVA_HOME（JDK 根目录）/ NODE_BIN（node 绝对路径，纯后端可不填）
- Report-DevOps：GITLAB_TOKEN（GitLab project access token，建 MR 用）
配置提示：值从安全渠道获取，不要贴进 issue/评论/文档。
```

**铁律**：任何分配缺失**永远不回滚、不跳过 agent 创建、不中断批处理**。

## 维护约定

- 配置的**上游权威源 = 本仓库 `report-flow/agents/`**（design.md 登记位置）：改动先改上游，再同步拷贝到本 skill `agents/`；在网页/CLI 手工改过 agent 后须回写两处，否则复现漂移
- 敏感值（token/密钥）永不写入配置文件，只写 key + 用途说明
