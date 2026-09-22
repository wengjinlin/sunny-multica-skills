---
name: aicoding-orchestration-bootstrap
description: 在新工作区复现编排层（巡检兜底 autopilot + Mika 编排接力入口）。TRIGGER：用户要求「复现/迁移编排层」「建巡检兜底」「配置编排接力」时使用。框架不含剧本内容——巡检剧本维护在本 skill 的 autopilot.md，Mika 入口规则维护在 mika-instructions.md。
---

# aicoding-orchestration-bootstrap：复现编排层

编排层有四个组件，本 skill 各配置一个：

| 组件 | 内容权威源 | 落点 |
|---|---|---|
| 巡检兜底 autopilot | `autopilot.md`（30 分钟 cron，run_only，assignee=Mika） | autopilot 的 description |
| Mika 编排接力入口 | `mika-instructions.md`（`{{AUTOPILOT_ID}}` 占位符） | Mika 自定义 instructions 的「工作区补充」节 |
| 结构文档对账 autopilot | `doc-audit-autopilot.md`（周级 cron，run_only，assignee=DocKeeper） | autopilot 的 description（assignee 的 DocKeeper agent 由 aicoding-agent-bootstrap 创建） |
| 人工测试复盘 autopilot | `retro-autopilot.md`（周级 cron，run_only，assignee=DocKeeper） | autopilot 的 description（执行逻辑在 aicoding-human-test-retro skill，由 aicoding-skills-bootstrap 拉取并挂载 DocKeeper） |

主通道 = 角色 agent 完成评论发【编排信号】@Mika 秒级唤醒；cron autopilot 只是兜底。角色 agent 层（PM/Tech-Lead/…）由 aicoding-agent-bootstrap skill 负责，两个 skill 互补、互不越界：编排逻辑改动只动本 skill，角色交接协议改动只动 aicoding-agent-bootstrap。

## 中文传参铁律

`--description` / `--title` / `--instructions` 等参数**没有** `--xxx-file` 变体；`$(cat file)` 把中文内联进命令行时，PowerShell / cmd / GBK 代码页会把 UTF-8 内容转成乱码入库。**凡含中文的参数值一律经 multica_call.py 传 `@文件`**，禁止 `$(cat)` 内联、禁止命令行直写中文。

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

以 `@` 开头的参数值被替换为该 utf-8 文件全文；UUID / cron 表达式 / mode 等纯 ASCII 参数直接传。临时文件用完即删。

## 执行流程

### 第 0 步：前置

1. `multica runtime list --output json` 确认本工作区 runtime 可用（需已 setup daemon）
2. `multica agent list --output json` 找到本工作区 **Mika** 的 UUID（默认内置 agent，名字固定）
3. `multica autopilot list --output json` 记录现有 autopilot 名单（幂等基准）

### 第 1 步：创建/更新巡检 autopilot

1. `autopilot.md` 全文写 `./ap.tmp`，标题「编排兜底巡检」写 `./title.tmp`（均 utf-8，见「中文传参铁律」）
2. **幂等**：同名 autopilot 已存在 → 取其 ID，只更新剧本：`python multica_call.py autopilot update <id> --description @ap.tmp`，**不碰**触发器/assignee/mode/status；不存在 → 创建：
   ```
   python multica_call.py autopilot create --title @title.tmp --description @ap.tmp \
     --agent Mika --mode run_only --output json
   ```
   记录新 **AUTOPILOT_ID**
3. 触发器：检查该 autopilot 是否已有 schedule 触发器（`autopilot get` + `autopilot runs` 运行时间戳佐证）；没有才加：
   `multica autopilot trigger-add <AUTOPILOT_ID> --kind schedule --cron "*/30 * * * *" --timezone Asia/Shanghai`
   重复添加会造出多个触发器——**先查后加**

### 第 2 步：写入 Mika 编排接力入口

1. `multica agent get <Mika-ID> --output json` 读当前**自定义 instructions 字段**（注意：不是 system_instructions——那是平台管理的角色契约，不可覆盖）
2. `mika-instructions.md` 中 `{{AUTOPILOT_ID}}` 全部替换为 AUTOPILOT_ID
3. **幂等合并**：现有 instructions 已含「## 工作区补充：编排接力」节 → 该节整节替换、其余内容原样保留；没有 → 末尾追加
4. 合并结果写 utf-8 临时文件后回写：`python multica_call.py agent update <Mika-ID> --instructions @instr.tmp`
   ——只动 instructions 字段，其余字段（model/visibility/env 等）一律不碰

### 第 3 步：创建/更新结构文档对账 autopilot

1. `doc-audit-autopilot.md` 全文写 `./dap.tmp`，标题「结构文档对账」写 `./title2.tmp`（均 utf-8）
2. **幂等**：同名 autopilot 已存在 → 只更新剧本（`python multica_call.py autopilot update <id> --description @dap.tmp`）；不存在 → 创建：
   ```
   python multica_call.py autopilot create --title @title2.tmp --description @dap.tmp \
     --agent DocKeeper --mode run_only --output json
   ```
   （DocKeeper agent 须已由 aicoding-agent-bootstrap 创建并分配 aicoding-harness-audit skill；缺失则记入报告待办，不阻断）
3. 触发器：先查后加——`multica autopilot trigger-add <ID> --kind schedule --cron "17 8 * * 1" --timezone Asia/Shanghai`（周一早间，避开整点）

### 第 4 步：创建/更新人工测试复盘 autopilot

1. `retro-autopilot.md` 全文写 `./hrp.tmp`，标题「人工测试复盘」写 `./title3.tmp`（均 utf-8）
2. **幂等**：同名 autopilot 已存在 → 只更新剧本（`python multica_call.py autopilot update <id> --description @hrp.tmp`）；不存在 → 创建：
   ```
   python multica_call.py autopilot create --title @title3.tmp --description @hrp.tmp \
     --agent DocKeeper --mode run_only --output json
   ```
   （依赖 aicoding-human-test-retro skill 已拉取并挂载 DocKeeper——见 agent-bootstrap 的 DocKeeper.md「分配 skill」；缺失则记入报告待办，不阻断）
3. 触发器：先查后加——`multica autopilot trigger-add <ID> --kind schedule --cron "23 8 * * 1" --timezone Asia/Shanghai`（周一早间，与结构文档对账 08:17 错开）

### 第 5 步：报告

- autopilot ×3：新 UUID（或「已存在 → 已同步剧本」）/ cron 表达式 / mode=run_only / assignee
- Mika：instructions 长度前后对比 / 「工作区补充：编排接力」节已写入（含真实 AUTOPILOT_ID）
- 补充说明：角色 agent 层需另跑 aicoding-agent-bootstrap skill；编排逻辑后续修改直接改对应 autopilot 的 description（权威源），改完回写本 skill 的对应模板文件防漂移

## 维护约定

- `autopilot.md` / `mika-instructions.md` / `doc-audit-autopilot.md` / `retro-autopilot.md` 是四个权威源的**离线副本**：在网页/CLI 手工改过服务端后，必须回写对应文件，否则下次复现漂移
- 剧本保持分节结构（定位与总原则 / 运行流程 / 分类处置规则 / 幂等硬约束）——人类要能直接阅读
- 敏感值（token/密钥）永不写入模板
