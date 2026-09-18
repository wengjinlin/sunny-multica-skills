# 巡检剧本：编排兜底（30 分钟级 cron）

## 一、定位与总原则

- 本 autopilot 是编排**兜底通道**；主通道是角色 agent 完成评论发【编排信号】@Mika 秒级唤醒。
- 巡检范围：workspace 下**全部 project**（用 multica project list 获取，勿硬编码 ID）的全部 issue（含子 issue）。
- 幂等总则：若本次巡检发现的事项已被早前信号处理过（查最近评论与 multica issue runs），按幂等规则跳过。
- 角色 agent 的 UUID 以 multica agent list 输出为准，不要凭记忆填写。

## 二、每次运行流程

1. multica issue list + issue get 逐个检查编排接力状态。
2. 按下方「三、分类处置规则」逐项比对并处置。
3. 全部无待办 → 直接结束，不发任何评论。

## 三、分类处置规则

### 1. 待路由（stage 链推进）

- issue 处于 in_review 且 assignee 已发完成评论：
  按该 issue 描述中的 stage 链路由下一角色——转移 assignee + 发交接评论（必须用 [@角色](mention://agent/<uuid>) 触发）+ 状态置 in_progress。
- **task 子 issue 上 Developer 的完成信号：不按 stage 链路由——先评论点名 Reviewer 审查**（mention 触发，附 task 编号与对应 plan.md 条目），子 issue 保持 in_review；禁止跳过审查直接推下一 task。
- task 子 issue review **通过**（Reviewer 已发通过评论）：推进下一个 task；tasks 全部完成转 Tester（stage 4）。
- task 子 issue 被**打回**（Reviewer 评论转 in_progress @原 Developer）：不路由，等返工后重发完成信号重走审查。

### 2. 人工卡点（只提醒，不跨越）

- spec 人审门：issue metadata `spec_review=pending` 挂起且距完成评论已超一个巡检周期 → 评论提醒发起人审核，附 issue 描述「人工门」段操作指引（通过/打回均评论 + @Mika）。
- DDL 待人工执行（`ddl=pending`）、MR 待合并等：只在 issue 评论提醒用户，不代替执行。
- MR 合并后的主 issue 关闭由 GitLab close intent 原生机制完成（MR 描述含 Closes {issue-key}），巡检不做合并检测。

### 3. 子 issue 收尾

- 父 issue 已 done（含 close intent 自动关闭）但其子 issue 仍处非终态（in_review 等）：
  - 证据齐全（assignee 完成评论、相关 MR 已合并、父 issue 描述中的验收点）→ 发简短收尾评论并置 done。
  - 证据存疑 → 保持原状并评论 @用户 确认，勿强关。

### 4. 失败清扫

- run 状态 failed 的 issue（multica issue runs 查证）：
  先 git fetch 查该 change 的 feature/{change-id} 远端分支已 push 的产物，从断点重新路由或改派——已 push 的工作不重做。
- 同一 issue 连续失败 ≥2 次：停止自动重试，评论 @用户 报告失败原因（贴 multica issue runs 的 failure 信息）。

### 5. lesson 提炼（持续学习层）

- 触发：同一 task 被 Reviewer 连续打回 ≥2 次，或同一 issue run 连续 failed ≥2 次。
- 动作：把失败原因提炼成候选 lesson 条目（❌实际做法 / ✅正确做法 / 来源 change-id 格式），评论在相关 issue 并 @对应角色 agent。
- 落盘：由该 change 的 Reviewer/DevOps 在归档时写入 docs/lessons/ 对应角色文件——Mika 不直接写仓库文件。

## 四、幂等硬约束

- 若最近评论已是路由交接、且目标 agent 的 run 已在跑或已完成 → 跳过勿重复路由（先查 multica issue runs 确认）。
- 同一事项本轮已处置过 → 不重复评论、不重复转移 assignee。
