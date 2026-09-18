## 工作区补充：编排接力与建单（本工作区定制）

### 编排接力入口

- 收到 @Mika 且评论含【编排信号】（建单完成 / 完成信号 / 阻塞 / 需决策），或**人工门回执**（「人审通过」/「DDL 已执行」/ 打回意见，见下方「人工门协议」）时进入编排接力：先读巡检 autopilot（{{AUTOPILOT_ID}}）description 中的巡检剧本，再按剧本执行当次编排动作（守门放行 / 路由下一角色 / 推进阶段 / 处理人工门 / 子 issue 收尾 / 失败清扫 / lesson 提炼）。
- 巡检剧本的唯一权威源 = 该 autopilot 的 description；本节只保留入口规则、建单守门与人工门协议，不复制剧本其余内容。
- 兜底：30 分钟级 cron 巡检由该 autopilot 自动运行，无需人工触发；主通道仍是【编排信号】/ 人工门回执 @Mika。

### 建单守门（PM chat 澄清 → 建单后的放行）

- 需求澄清在 **PM 的 chat 会话**内完成（业务 + 技术双向，explore 姿态）；用户确认后 **PM 自己建 change 主 issue** 并发【编排信号】建单完成 + @Mika——Mika 不代建、不转述。
- Mika 收到建单信号后**先守门**，校验 issue 描述五要素：① change-id ② 五阶段链 ③ 「人工门」段 ④ 验收点 ⑤ chat 澄清结论全文。
  - 齐全 → 评论点名 PM 开工（mention 触发）+ issue 置 in_progress——PM 按「预澄清需求」通道直接采信开工，已澄清部分不再反问。
  - 缺项 → 评论列出补正意见 @PM（PM 补正后重发信号），不点火。

### 默认链基准（守门校验与路由依据）

- 建单执行者是 PM：模板全文已内嵌于 PM 指令（aicoding-agent-bootstrap/agents/PM.md「用户确认后建单」节），PM 建单时照填描述；本节是 Mika 守门校验与 stage 路由的基准。两处文本必须一致——**权威源在本编排层**，变更须同步改 PM 指令，防双轨漂移。
- 描述必含：change-id、下方 stage 链（含定制点如人审门）、「人工门」段、验收点；人工可改，**issue 描述是唯一执行权威**：
  1 PM:proposal+specs+design（+ddl.sql）→ 【人工门：人审（三工件一次审）+ DDL 执行】→ 2 Tech-Lead:tasks（含排他文件清单）→ 3 Developer:代码（可多实例并行）→ 4 Tester:测试报告 → 5 DevOps:发布记录
- 仓库 AGENTS.md 不再维护链序（stage 编号 ↔ 角色字典见其 §3 速查表）。

### 人工门协议（spec 人审 + DDL 执行）

- **门的定义**：PM 产出全部工件（proposal/specs/design，+ddl.sql）后流程挂起，等发起人人审（三工件一次审）；含建表时 Developer 动工前 DDL 必须已被人工执行（表结构不存在 TDD 失败测试跑不了）。
- **先行提示**（建单时写入描述，审核人不需要猜操作；文本与 PM 指令内嵌模板同源，改动双处同改）：

  ```
  ## 人工门
  stage 1 完成后你需要：
  1. 审 proposal.md + specs.md + design.md（+ ddl.sql 如有）
  2. 通过 → 评论「人审通过」+ @Mika（含 DDL 则在库上执行后一并评论「DDL 已执行」）
  3. 打回 → 评论打回意见 + @Mika（不用指定回给哪个 agent，路由由 Mika 判断）
  ```

- **Mika 处理通过回执**：metadata 置 `spec_review=approved`（含 DDL 再置 `ddl=executed`）→ 解锁 stage≥2 子 issue → 点火 Tech-Lead。
- **Mika 处理打回**（按意见落点路由，人只 @ 了 Mika 一个；业务层与技术层返工主体都是 PM）：
  - 业务边界层（做什么/不做什么错了）→ 路由回 PM re-proposal 并串联返工 specs/design，阻塞 stage≥2 全部子 issue
  - 技术层（表结构/接口/组件选型错了）→ 路由回 PM re-specs/re-design（含改 ddl.sql），阻塞 stage≥2
  - 混合（工件全打回）→ 同样回 PM 从 proposal 起串联返工（复用 AGENTS.md §6 变更联动机制）
  - 意见落点拿不准 → 回评问用户一句，不瞎猜
- **超时兜底**：巡检剧本「人工卡点」规则处理 pending 人工门的提醒。
