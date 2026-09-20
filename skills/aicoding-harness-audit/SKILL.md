---
name: aicoding-harness-audit
description: 结构文档增量对账：从上次同步基线到 origin/master 的变更 diff 映射到应更新的 harness 结构文档（模块表/架构字典/隐性约定/术语表/能力清单），可自动项走 MR 更新，DDL 与存疑项提醒人工。TRIGGER：「文档对账」「结构文档同步」「harness 审计」。
---

# aicoding-harness-audit：结构文档增量对账

**定位**：文档漂移的第二道防线。第一道是变更随行（docs/index.md 维护规则 1：文档在同一个 change 内更新）——本 skill 只抓漏网，不代替变更随行。
**执行者**：DocKeeper agent（周级 autopilot 触发或人工建 issue）。
**对账对象**：已合并进 `origin/master` 的变更——在途 feature 分支不算漂移。

## 执行流程

### 第 0 步：前置

1. `multica repo checkout <url>`（或确认仓库已在本工作区），`git fetch origin`
2. MR 目标分支以仓库 `AGENTS.md` §4 为准

### 第 1 步：读基线

- 读 `docs/index.md`「结构文档同步状态」节的基线 commit
- **无该节或无基线值**：登记基线 = 当前 `origin/master` HEAD（写入该节，随本次产出一起 commit），本次收工——首次登记不追溯全量核对（存量仓库如需全量核对，由人另行发起 harness-bootstrap 对齐模式）

### 第 2 步：差异清单

```
git log --name-only --oneline <基线>..origin/master
```

变更文件按下表分类；无映射命中的变更（纯方法体修改等）不产生对账项。

### 第 3 步：分类对账（映射表）

| 变更信号 | 对账目标 | 方式 |
|---|---|---|
| `pom.xml` / `package.json` 变更、新模块目录 | `CLAUDE.md` §2 模块结构表、`docs/help/index.md` 能力清单 | 机械对照，**自动改** |
| controller / service / entity / mapper 新增或改名 | `docs/architecture/index.md` §1 模块定位字典 | 半自动：生成候选行进「待人工确认清单」，明显项（新业务包对应新表前缀）可直接改 |
| 新缩写 / 拼音命名出现 | `docs/architecture/implicit-contracts.md` 对照表 | 扫描提示，人确认 |
| DDL / 表结构文件变更 | `docs/database/`（按其「再生成规则」走 aicoding-db-schema-export） | **只提醒**——连库导出须人工在能连库环境执行，本 skill 不代跑 |
| 字典表 / 枚举类变更 | `docs/product/index.md` 术语表 / 状态机 | 提醒，人确认 |

### 第 4 步：产出（有可自动项时）

1. 建 `feature/doc-audit-{yyyymmdd}` 分支（基于 `origin/master`）
2. 更新对账目标文档 + **同 commit 更新 `docs/index.md` 基线节**（新基线 = 本次对账到的 master HEAD）
3. `git push origin feature/doc-audit-{yyyymmdd}`
4. GitLab API 建 MR（写 JSON body 文件——form 编码中文会 500；`PRIVATE-TOKEN: $GITLAB_TOKEN`；API base 与 project-id 从项目上下文获取，不写死）
5. 评论贴对账报告：改动清单 / 依据的变更信号 / MR 链接 / 待人工确认清单

### 第 5 步：无差异收工

- 差异为空或全部落在提醒项：autopilot 场景**静默结束不发评论**；issue 触发场景回复对账结论即可

## 幂等

- 已存在未合并的 `doc-audit-*` 分支 / MR → 不重复建：新发现的差异并入对账报告评论，基线不前移（等 MR 合并后下次对账自然收口）
- 基线节缺失但仓库已有 doc-audit MR → 先报告矛盾，不擅自登记基线

## 铁律

- 只改 `docs/` 与 `CLAUDE.md` 文档节（§2 模块表）；**禁碰任何代码**
- MR 由人合并，禁直推保护分支（清单见 AGENTS.md §4）
- 存疑项一律进「待人工确认清单」，不猜
- `$GITLAB_TOKEN` 禁止打印、写入文件/评论/commit；变量为空则评论报告 env 未配置，不硬编绕路
