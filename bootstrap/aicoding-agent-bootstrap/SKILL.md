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
| `## 指令` | instructions 全文；`{{MIKA_ID}}` 为占位符 | 写 utf-8 临时文件，经 multica_call.py 传 `--instructions @instr.tmp`（见「中文传参铁律」） |
| `## 分配 skill` | 每行一个 skill 名，或「（无）」 | `multica agent skills add`（按名字解析 id） |
| `## 分配 MCP` | 一个 JSON 对象（mcpServers 结构），或「（无）」 | 写临时文件后 `--mcp-config-file` |
| `## 自定义 env` | 每行一个 `KEY # 用途说明`，或「（无）」 | **纯人工配置，agent 不执行任何 env 写操作**（实测 agent 凭据调 CLI env get/set 一律被拒，连自己的 env 也不行——env 是人工通道）：把「变量名 + 用途」整理成人类可读待配置清单进总体报告人类待办，由人工在 Multica 网页 agent 设置（或人工本机 CLI）配置；agent 运行时从自身进程环境变量读取 |

## 中文传参铁律（两起实测事故铸成，逐条强制）

`--instructions` / `--description` 等参数**没有** `--xxx-file` 变体；`$(cat file)` 把中文内联进命令行时，PowerShell / cmd / GBK 代码页会把 UTF-8 内容转成乱码入库（**事故一**：agent instructions 整段乱码）。**凡含中文的参数值一律经 multica_call.py 传 `@文件`**，禁止 `$(cat)` 内联、禁止命令行直写中文。

**事故二**（2026-09-22 实测，另一工作区）：裸命令 `python` 解析到 pyenv-win 的 `python.bat` shim，参数经 cmd.exe 转发时被 GBK 转码 + 换行截断，7 个 agent 的 instructions 只剩第一行入库，且执行者自写批量脚本的「逐字节校验」因 expected 与 got 同源而假阳性通过。由此追加三条铁律：

1. **解释器铁律**：先探测**真实 python.exe 绝对路径**（记为 **PY**）再用。探测法任选：`py -c "import sys;print(sys.executable)"`、PowerShell `Get-Command python.exe` 取 Source、或直查常见安装目录（如 `%LOCALAPPDATA%\Programs\Python\Python3xx\python.exe`）。**路径含 `pyenv-win\shims` 的解释器一律禁用**（.bat shim 经 cmd 中转必转码截断）；后续所有调用一律 `"<PY>" multica_call.py ...` / `"<PY>" verify_instructions.py ...`，不再用裸 `python`。探测失败 → 总体报告记人类待办（说明需安装/定位 python），涉及中文传参的 create/update 本轮不执行。
2. **禁止自写批量驱动脚本**：逐个 agent 依次调用 multica_call.py；不为批量另写驱动脚本、不另造传参方式、不把多个 agent 的写入塞进一个自造脚本（事故二的截断与假阳性校验均出在执行者自写脚本里）。
3. **写后强制回读校验**：每个 agent 的 create/update 完成后，必须用 verify_instructions.py **独立回读服务端**，与**从配置文件重新解析出的指令全文**（`{{MIKA_ID}}` 替换后）逐字符比对；**禁止复用写入时的变量做 expected**（同源比对必出假阳性）。输出 `VERIFY FAIL` → 该 agent 记失败进总体报告，不得宣称完成、不得跳过校验继续下一个。

执行前先把以下两个助手脚本**原样照抄**写入工作目录（不改动、不简化）：

`multica_call.py`：

```python
# 用法：<PY> multica_call.py <子命令...> --instructions @<utf-8 文件路径>
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

`verify_instructions.py`：

```python
# 用法：<PY> verify_instructions.py <agent-id> <expected全文的utf-8文件路径>
import json, subprocess, sys
r = subprocess.run(['multica', 'agent', 'get', sys.argv[1], '--output', 'json'],
                   capture_output=True, encoding='utf-8')
got = json.loads(r.stdout)['instructions']
exp = open(sys.argv[2], 'rb').read().decode('utf-8').strip()
ok = got.strip() == exp
print('VERIFY', 'PASS' if ok else 'FAIL', 'got_len', len(got), 'exp_len', len(exp))
if not ok:
    print('GOT_HEAD:', got[:60].replace('\n', '\\n'))
    print('EXP_HEAD:', exp[:60].replace('\n', '\\n'))
```

以 `@` 开头的参数值被替换为该 utf-8 文件全文；UUID / URL / 数字等纯 ASCII 参数直接传。校验用的 expected 文件与 instr.tmp 在**全部 agent 校验通过后**再清理（提前删除会让后续校验无 expected 可比）。

## 执行流程

### 第 0 步：前置

> 安装链顺序：aicoding-importing-skills（含 **superpowers 系列导入**，GitHub 源 obra/superpowers——Tech-Lead/Developer 的 plan/TDD 能力依赖，须先于本 skill 导入；**aicoding-browser-qa**（Tester）与 **aicoding-harness-audit**（DocKeeper）也在此步导入）→ **本 skill** →（人工 env 注入，如 GITLAB_TOKEN）→ aicoding-project-init → aicoding-orchestration-bootstrap → aicoding-harness-bootstrap。项目在本 skill 之后才创建，未建属正常。

1. **探测 python 解释器（记为 PY）**：按「中文传参铁律」第 1 条取得真实 python.exe 绝对路径并通过 shims 禁用检查
2. `multica runtime list --output json` 取 runtime-id（本工作区需已 setup daemon）
3. `multica agent list --output json` 找到本工作区 Mika 的 UUID，记为 **NEW_MIKA_ID**
4. `multica agent list` 记录现有 agent 名单（幂等基准）
5. **项目状态探测（非阻断）**：`multica project list --output json` 看项目是否已建——未建属**正常**：安装链里项目由后续 aicoding-project-init 创建，且其验证环节要用本 skill 建出的 DevOps agent；报告只提示「下一步：跑 aicoding-project-init」，**不阻断**（铁律：不中断批处理）
6. 列出本 skill `agents/` 目录全部 `*.md` —— 文件数 = 待创建数，逐个处理

### 第 1 步：逐文件创建

对每个配置文件：

1. **幂等检查**：同名 agent 已存在 → **不创建，改走同步模式（只做三个动作）**：
   - **更新指令**：「## 指令」节（`{{MIKA_ID}}` 替换后）写 utf-8 临时文件，`"<PY>" multica_call.py agent update <id> --instructions @instr.tmp`——配置文件指令整体覆盖；**更新后立即 `"<PY>" verify_instructions.py <id> <instr.tmp 路径>` 回读校验**（铁律 3）
   - **对齐分配 skill**：`multica agent skills set <id> --skill-ids <按配置文件解析到的全部id>`（set = 替换式对齐，配置文件是权威源）；配置为「（无）」则**不动现有挂载**（避免误清手工配置）；缺失 skill 照旧只登记不阻断
   - **对齐分配 MCP**：「## 分配 MCP」非「（无）」时 `multica agent update <id> --mcp-config-file <file>`；「（无）」则不动
   - **其余字段一律不碰**：description / model / thinking_level / service_tier / max_concurrent_tasks / visibility / env 保持现状——已存在的 agent 视为本地已有定制，同步仅限上述三项
2. **准备指令**：取「## 指令」节全文，`{{MIKA_ID}}` 全部替换为 NEW_MIKA_ID，写 utf-8 临时文件（如 `./instr.tmp`）
3. **创建**：
   ```
   "<PY>" multica_call.py agent create --name <name> --description @desc.tmp \
     [--model <model>] [--thinking-level <t>] [--service-tier <tier>] \
     --max-concurrent-tasks <n> --visibility workspace \
     --runtime-id <runtime-id> --instructions @instr.tmp
   ```
   记录新 UUID。frontmatter 空字段直接省略参数；description 中文时写 `@desc.tmp`，纯 ASCII 可直传该值。**创建成功后立即 `"<PY>" verify_instructions.py <新UUID> <instr.tmp 路径>` 回读校验**（铁律 3），FAIL 记失败进总体报告。
4. **分配 skill**：节内非「（无）」时：
   - `multica skill list --output json` 按 name 解析出各 skill 的 id
   - 存在的：`multica agent skills add <新agent-id> --skill-ids <存在的id列表>`
   - **缺失的 skill：不阻断、不重试、不中止后续文件处理**——仅记入缺失登记（agent 名 + skill 名），留待总体报告
5. **分配 MCP**：节内非「（无）」时：JSON 写临时文件，创建时加 `--mcp-config-file <file>`（若 agent 已建则 `multica agent update <id> --mcp-config-file <file>`）；若配置为引用式（引用 workspace 级 MCP 名）且解析不到，**同样只记缺失登记，agent 保留已创建状态**
6. **env**：节内非「（无）」时：**不执行任何 env 读写操作**（agent 无权——实测 CLI env get/set 均返回无权限，env 是人工通道）——逐 key 整理成人类可读清单（变量名 + 用途说明），列入第 2 步总体报告的人类待办，由人工自行配置

### 第 2 步：总体报告（全部文件处理完后统一输出，缺失内容只在这里收口）

**创建结果表**：agent 名 / 新 UUID（或「已存在 → 同步了 指令/skill/mcp 三项」）/ max-concurrent / 已应用的 skill 数 / **回读校验 PASS/FAIL**

**缺失内容总体报告**（核心交付，无缺失也要显式写「无缺失」）：

```
## 缺失内容登记
| agent | 缺失项 | 类型 | 补齐命令 |
|---|---|---|---|
| PM | aicoding-config-auth-resource-v2 | skill | multica skill import <zip或URL> 后：multica agent skills add <该agent的UUID> --skill-ids <补导后的id> |
| ... | ... | mcp | multica agent update <UUID> --mcp-config-file <file> |

统计：N/M 个 agent 创建（或已存在）；K 项分配缺失（skill X 项 / mcp Y 项）；回读校验 FAIL Z 个（如有）
```

**人类待办**（env 配置——只能人工完成；输出用人话格式，**不给命令**，变量名与说明可直接复制）：
```
以下 agent 需要配置环境变量（入口：Multica 网页 → 该 agent 详情 → 环境变量；本机 CLI 亦可）：
- {agent 名}：{KEY}（{用途说明}）
配置提示：值从安全渠道获取，不要贴进 issue/评论/文档；agent 只在自己的运行进程中读取这些变量。
```

**铁律**：任何分配缺失**永远不回滚、不跳过 agent 创建、不中断批处理**——agent 先建出来，缺的挂载留给总体报告和补齐命令。回读校验 FAIL 同样不回滚已建 agent，只如实登记。`{{MIKA_ID}}` 替换抽查提醒同上。

## 维护约定

- 新增角色：复制最接近的现有配置文件改内容；删除角色：删文件
- 配置文件即**唯一权威源**——在 multica 网页/CLI 手工改过 agent 后，须回写对应文件，否则下次复现漂移
- 敏感值（token/密钥）永不写入配置文件，只写 key + 用途说明
