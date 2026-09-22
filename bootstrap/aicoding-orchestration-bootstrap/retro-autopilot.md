# 人工测试复盘 autopilot（周级 cron）

## 一、定位与总原则

- 本 autopilot 是人工测试经验沉淀的**周级复盘入口**：人工测试报告由人类随 MR 入库（机制见 `docs/human-test-reports/index.md`），复盘不等单个 MR，按周批量消化未读报告。
- 执行者是 **DocKeeper** agent：本 autopilot 触发其在 run 内 Skill 调 `aicoding-human-test-retro` 完成复盘——归因枚举、证据链、分拣规则、产出方式的唯一权威源在该 skill，本剧本不复制。
- 静默原则：全部仓库游标后均无新报告且无停等项 → 直接结束，不发任何评论、不建 issue。
- 停等原则：仓库存在未合并的 `retro-*` MR → 本期跳过该仓库并在 run 结论提醒，不建新 MR、游标不前移——人未决策，链路停在提醒上，不丢不重。

## 二、每次运行流程

1. `multica project list` 遍历本工作区全部 project，取各 project 绑定的仓库（含工作区游离仓库）。
2. 每个仓库：`git fetch origin` → 无 `docs/human-test-reports/` 目录 → 下一仓（未建 harness 或无人工测试机制）；有 → 读 `index.md`「复盘覆盖」游标，扫描游标之后的新报告：
   - 游标节缺失 → 按 skill 首期全量流程处理
   - 游标后无新报告 → 下一仓
   - 有新报告 → 本 run 内按 `aicoding-human-test-retro` 执行复盘
3. 有新报告的仓库逐仓产出（skill 第 6 步）：`retro/{yyyymmdd}` 分支 + 期报 + lesson 草案 + 索引两列补填 + 游标前移（同一 MR），MR 描述贴期报全文——人就在 MR 页面完成决策。
4. 全部仓库处理完 → 有 MR 的贴复盘结论收工；全部无新报告 → 静默结束。

## 三、幂等硬约束

- 已存在未合并的 `retro-*` 分支 / MR 的仓库 → 不重复建：新报告并入提醒，游标不前移，等上期 MR 人工合并后下期自然收口。
- 同一仓库本轮已处置 → 不重复操作。
- 报告本体（`日期-分支名.md`）只读，复盘永不修改测试者内容。
