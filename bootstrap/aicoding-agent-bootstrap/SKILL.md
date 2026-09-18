---
name: aicoding-agent-bootstrap
description: 在新工作区批量复现角色 agent 的创建与配置。TRIGGER：用户要求「复现/迁移/批量创建 agent」「按 agents 目录建 agent」「部署 agent 层」时使用。框架本身不含 agent 内容——每个 agent 的配置维护在本 skill 的 agents/ 目录下，一个文件一个 agent，文件数即创建数。
---

# aicoding-agent-bootstrap：按配置文件批量创建 agent

本 skill 是**创建框架**：读取 `agents/` 目录下的配置文件，逐个创建 agent 并应用全部配置。agent 内容不写死在框架里——增删角色 = 增删 `agents/*.md` 文件。

## 配置文件格式（agents/*.md）

每个文件分两部分：

**frontmatter（标量设置 → agent create 参数）**

| 字段 | 对应参数 | 空 值含义 |
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
| `## 指令` | instructions 全文；`{{MIKA_ID}}` 为占位符 | 写临时文件后传 `--instructions`（禁命令行内联中文） |
| `## 分配 skill` | 每行一个 skill 名，或「（无）」 | `multica agent skills add`（按名字解析 id） |
| `## 分配 MCP` | 一个 JSON 对象（mcpServers 结构），或「（无）」 | 写临时文件后 `--mcp-config-file` |
| `## 自定义 env` | 每行一个 `KEY # 用途说明`，或「（无）」 | **人类待办**——agent 无权执行 `multica agent env set` |

## 执行流程

### 第 0 步：前置

> 安装链顺序：aicoding-importing-skills（含 **superpowers 系列导入**，GitHub 源 obra/superpowers——Tech-Lead/Developer 的 plan/TDD 能力依赖，须先于本 skill 导入）→ **本 skill** →（人工 env 注入，如 GITLAB_TOKEN）→ aicoding-project-init → aicoding-orchestration-bootstrap → aicoding-harness-bootstrap。项目在本 skill 之后才创建，未建属正常。

1. `multica runtime list --output json` 取 runtime-id（本工作区需已 setup daemon）
2. `multica agent list --output json` 找到本工作区 Mika 的 UUID，记为 **NEW_MIKA_ID**
3. `multica agent list` 记录现有 agent 名单（幂等基准）
4. **项目状态探测（非阻断）**：`multica project list --output json` 看项目是否已建——未建属**正常**：安装链里项目由后续 aicoding-project-init 创建，且其验证环节要用本 skill 建出的 DevOps agent；报告只提示「下一步：跑 aicoding-project-init」，**不阻断**（铁律：不中断批处理）
5. 列出本 skill `agents/` 目录全部 `*.md` —— 文件数 = 待创建数，逐个处理

### 第 1 步：逐文件创建

对每个配置文件：

1. **幂等检查**：同名 agent 已存在 → **不创建，改走同步模式（只做三个动作）**：
   - **更新指令**：「## 指令」节（`{{MIKA_ID}}` 替换后）写临时文件，`multica agent update <id> --instructions "$(cat instr.tmp)"`——配置文件指令整体覆盖
   - **对齐分配 skill**：`multica agent skills set <id> --skill-ids <按配置文件解析到的全部id>`（set = 替换式对齐，配置文件是权威源）；配置为「（无）」则**不动现有挂载**（避免误清手工配置）；缺失 skill 照旧只登记不阻断
   - **对齐分配 MCP**：「## 分配 MCP」非「（无）」时 `multica agent update <id> --mcp-config-file <file>`；「（无）」则不动
   - **其余字段一律不碰**：description / model / thinking_level / service_tier / max_concurrent_tasks / visibility / env 保持现状——已存在的 agent 视为本地已有定制，同步仅限上述三项
2. **准备指令**：取「## 指令」节全文，`{{MIKA_ID}}` 全部替换为 NEW_MIKA_ID，写 utf-8 临时文件（如 `./instr.tmp`）
3. **创建**：
   ```
   multica agent create --name <name> --description <description> \
     [--model <model>] [--thinking-level <t>] [--service-tier <tier>] \
     --max-concurrent-tasks <n> --visibility workspace \
     --runtime-id <runtime-id> --instructions "$(cat instr.tmp)"
   ```
   记录新 UUID。frontmatter 空字段直接省略参数。
4. **分配 skill**：节内非「（无）」时：
   - `multica skill list --output json` 按 name 解析出各 skill 的 id
   - 存在的：`multica agent skills add <新agent-id> --skill-ids <存在的id列表>`
   - **缺失的 skill：不阻断、不重试、不中止后续文件处理**——仅记入缺失登记（agent 名 + skill 名），留待总体报告
5. **分配 MCP**：节内非「（无）」时：JSON 写临时文件，创建时加 `--mcp-config-file <file>`（若 agent 已建则 `multica agent update <id> --mcp-config-file <file>`）；若配置为引用式（引用 workspace 级 MCP 名）且解析不到，**同样只记缺失登记，agent 保留已创建状态**
6. **env**：节内非「（无）」时：记入人类待办清单，不代替执行

### 第 2 步：总体报告（全部文件处理完后统一输出，缺失内容只在这里收口）

**创建结果表**：agent 名 / 新 UUID（或「已存在 → 同步了 指令/skill/mcp 三项」）/ max-concurrent / 已应用的 skill 数

**缺失内容总体报告**（核心交付，无缺失也要显式写「无缺失」）：

```
## 缺失内容登记
| agent | 缺失项 | 类型 | 补齐命令 |
|---|---|---|---|
| PM | aicoding-config-auth-resource-v2 | skill | multica skill import <zip或URL> 后：multica agent skills add <该agent的UUID> --skill-ids <补导后的id> |
| ... | ... | mcp | multica agent update <UUID> --mcp-config-file <file> |

统计：N/M 个 agent 创建（或已存在）；K 项分配缺失（skill X 项 / mcp Y 项）
```

**人类待办**（env 注入，逐条给出可复制命令）：
```
multica agent env set <新agent的UUID> --custom-env-file <文件>
# 文件内容：{"<KEY>": "<值>"}   # 值从安全渠道获取，不入库不入评论
```

**铁律**：任何分配缺失**永远不回滚、不跳过 agent 创建、不中断批处理**——agent 先建出来，缺的挂载留给总体报告和补齐命令。`{{MIKA_ID}}` 替换抽查提醒同上。

## 维护约定

- 新增角色：复制最接近的现有配置文件改内容；删除角色：删文件
- 配置文件即**唯一权威源**——在 multica 网页/CLI 手工改过 agent 后，须回写对应文件，否则下次复现漂移
- 敏感值（token/密钥）永不写入配置文件，只写 key + 用途说明
