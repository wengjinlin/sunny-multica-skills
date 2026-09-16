## 工作区补充：编排接力与建单（本工作区定制）

### 编排接力入口

- 收到 @Mika 且评论含【编排信号】（完成信号 / 阻塞 / 需决策），或**人工门回执**（「人审通过」/「DDL 已执行」/ 打回意见，见下方「人工门协议」）时进入编排接力：先读巡检 autopilot（{{AUTOPILOT_ID}}）description 中的巡检剧本，再按剧本执行当次编排动作（路由下一角色 / 推进阶段 / 处理人工门 / 子 issue 收尾 / 失败清扫 / lesson 提炼）。
- 巡检剧本的唯一权威源 = 该 autopilot 的 description；本节只保留入口规则与人工门协议，不复制剧本其余内容。
- 兜底：30 分钟级 cron 巡检由该 autopilot 自动运行，无需人工触发；主通道仍是【编排信号】/ 人工门回执 @Mika。

### chat 澄清结果建单

- 用户在 chat 中要求把澄清结果开成 change 时：从 chat 上下文提取**双份结构化结论**合流注入 issue 描述——**业务结论**来自 PM（决策表 / 做什么·不做什么 / 业务包归属 / 建议 change-id），**技术结论**来自 Architect（表结构倾向 / 接口风格 / 复用决策 / 组件选型，若有）；技术结论同时作为 stage 2 的预澄清输入。
- 按下述默认链建 change 主 issue（stage 1 assign PM，描述同时写明验收点与「人工门」段）。

### 默认链模板（建 change 主 issue 时写入描述）

- 描述必含：change-id、下方 stage 链（含定制点如人审门）、「人工门」段、验收点；人工可改，**issue 描述是唯一执行权威**：
  1 PM:proposal → 2 Architect:specs+design（+ddl.sql）→ 【人工门：人审 + DDL 执行】→ 3 Tech-Lead:tasks（含排他文件清单）→ 4 Developer:代码（可多实例并行）→ 5 Tester:测试报告 → 6 DevOps:发布记录
- 仓库 AGENTS.md 不再维护链序（stage 编号 ↔ 角色字典见其 §3 速查表）。

### 人工门协议（spec 人审 + DDL 执行）

- **门的定义**：Architect 产出 specs/design（+ddl.sql）后流程挂起，等发起人人审；含建表时 Developer 动工前 DDL 必须已被人工执行（表结构不存在 TDD 失败测试跑不了）。
- **先行提示**（建单时写入描述，审核人不需要猜操作）：

  ```
  ## 人工门
  stage 2 完成后你需要：
  1. 审 proposal.md + specs.md + design.md（+ ddl.sql 如有）
  2. 通过 → 评论「人审通过」+ @Mika（含 DDL 则在库上执行后一并评论「DDL 已执行」）
  3. 打回 → 评论打回意见 + @Mika（不用指定回给哪个 agent，路由由 Mika 判断）
  ```

- **Mika 处理通过回执**：metadata 置 `spec_review=approved`（含 DDL 再置 `ddl=executed`）→ 解锁 stage≥3 子 issue → 点火 Tech-Lead。
- **Mika 处理打回**（按意见落点路由，人只 @ 了 Mika 一个）：
  - 业务边界层（做什么/不做什么错了）→ 路由回 PM re-proposal，阻塞 stage≥2 全部子 issue
  - 技术层（表结构/接口/组件选型错了）→ 路由回 Architect re-specs/re-design（含改 ddl.sql），阻塞 stage≥3
  - 混合（工件全打回）→ **从最上游串联返工**：先 PM 重定边界 → Architect 按新 proposal 重做（复用 AGENTS.md §6 变更联动机制），下游全阻塞
  - 意见落点拿不准 → 回评问用户一句，不瞎猜
- **超时兜底**：巡检剧本「人工卡点」规则处理 pending 人工门的提醒。
