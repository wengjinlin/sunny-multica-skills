# 结构文档对账 autopilot（周级 cron）

## 一、定位与总原则

- 本 autopilot 是结构文档漂移的**兜底巡检**（周级）；主防线是变更随行（各 change 内同步更新文档，见 docs/index.md 维护规则 1）。
- 执行者是 **DocKeeper** agent：本 autopilot 触发其在 run 内 Skill 调 `aicoding-harness-audit` 完成对账——对账映射表、幂等规则、产出方式的唯一权威源在该 skill，本剧本不复制。
- 对账对象是已合并进 `origin/master` 的变更；在途 feature 分支不算漂移，不催不检。
- 静默原则：全部仓库无差异 → 直接结束，不发任何评论、不建 issue。

## 二、每次运行流程

1. `multica project list` 遍历本工作区全部 project，取各 project 绑定的仓库（含工作区游离仓库）。
2. 每个仓库：`git fetch origin` → 读 `docs/index.md`「结构文档同步状态」节基线 → 与 `origin/master` HEAD 比对：
   - 基线缺失 → 本仓库按 skill 首次登记流程处理
   - 基线 = HEAD → 无漂移，下一仓
   - 基线落后 → 本 run 内按 `aicoding-harness-audit` 执行对账
3. 有差异的仓库逐仓产出（skill 第 4 步）：`feature/doc-audit-{yyyymmdd}` 分支 + MR + 基线前移（同一 MR）+ 对账报告。
4. 全部仓库处理完 → 有 MR 的贴报告收工；全部无差异 → 静默结束。

## 三、幂等硬约束

- 已存在未合并的 `doc-audit-*` 分支 / MR 的仓库 → 不重复建：差异并入已有 MR 或报告评论，基线不前移。
- 同一仓库本轮已处置 → 不重复操作。
- DDL 变更信号只提醒人工（连库导出走 aicoding-db-schema-export，须能连库环境），本 autopilot 不代跑、不因它建分支。
