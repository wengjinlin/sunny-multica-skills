# 巡检剧本：编排兜底（报表工作区，30 分钟级 cron）

## 一、定位与总原则

- 本 autopilot 是编排**兜底通道**；主通道是角色 agent 完成评论发【编排信号】@Mika 秒级唤醒。
- 本工作区为报表专用独立工作区：Mika 只路由报表链（3 stage，角色全为 Report-*）。
- 巡检范围：workspace 下**全部 project**（用 multica project list 获取，勿硬编码 ID）的全部 issue（含子 issue）。
- 幂等总则：若本次巡检发现的事项已被早前信号处理过（查最近评论与 multica issue runs），按幂等规则跳过。
- 角色 agent 的 UUID 以 multica agent list 输出为准，不要凭记忆填写。

## 二、每次运行流程

1. multica issue list + issue get 逐个检查编排接力状态。
2. 按下方「三、分类处置规则」逐项比对并处置。
3. 全部无待办 → 直接结束，不发任何评论。

## 三、分类处置规则

### 1. 待路由（报表 stage 链推进）

- issue 处于 in_review 且 assignee 已发完成评论：按该 issue 描述中的报表 stage 链路由下一 Report-* 角色——转移 assignee + 发交接评论（必须用 [@角色](mention://agent/<uuid>) 触发）+ 状态置 in_progress。
- **Report-Developer（或其 task 子 issue）的完成信号：不按 stage 链路由——先评论点名 Report-Reviewer 总审**（mention 触发，附 change-id 与审查范围 = `docs/report-flow/changes/{change-id}/report-design.md` 固定四关），issue 保持 in_review；禁止跳过总审直接进 stage 3。
- 总审**通过**（Report-Reviewer 已发通过评论）：点火 Report-DevOps（stage 3）。前后端分仓的 task 子 issue：两 task 均过审才转 stage 3。
- 总审被**打回**（Report-Reviewer 评论转 in_progress @原 Developer）：不路由，等返工后重发完成信号重走总审。
- 同一 change 连续打回 ≥2 次：停止自动重试，评论升级人类（附两次打回意见摘要）。

### 2. 人工卡点（只提醒，不跨越）

- spec 人审门：issue metadata `spec_review=pending` 挂起且距完成评论已超一个巡检周期 → 评论提醒发起人审 `docs/report-flow/changes/{change-id}/report-design.md`（重点偏离声明段），附 issue 描述「人工门」段操作指引（通过/打回均评论 + @Mika）。
- 权限就绪门（`role_bind=pending`，每个含 auth-resource.sql 的 change 都有）：超一个巡检周期未回执「权限已就绪」→ 评论提醒发起人在库上执行该 SQL 并到权限系统 UI 将菜单/按钮绑定到测试账号所属角色。**只提醒，不阻塞任何 stage 推进**（Developer 开发不依赖权限，MR 阶段人工收口才依赖）。
- 报表链**无 DDL 键**——不存在 DDL 待执行事项。
- MR 待合并：只在 issue 评论提醒用户，不代替执行、不做合并检测。合并后的主 issue 关闭由 GitLab close intent 原生机制完成（MR 描述含 Closes {issue-key}）。

### 3. 子 issue 收尾

- 父 issue 已 done（含 close intent 自动关闭）但其子 issue（前后端分仓的 task 子 issue）仍处非终态（in_review 等）：
  - 证据齐全（assignee 完成评论、相关 MR 已合并、父 issue 描述中的验收点）→ 发简短收尾评论并置 done。
  - 证据存疑 → 保持原状并评论 @用户 确认，勿强关。

### 4. 失败清扫

- run 状态 failed 的 issue（multica issue runs 查证）：先 git fetch 查该 change 的 feature/{change-id} 远端分支已 push 的产物，从断点重新路由或改派——已 push 的工作不重做。
- 同一 issue 连续失败 ≥2 次：停止自动重试，评论 @用户 报告失败原因（贴 multica issue runs 的 failure 信息）。

### 5. lesson 提炼（持续学习层 · 轻量）

- 触发（硬门，满足其一才提炼）：同一 change 被 Report-Reviewer 连续打回 ≥2 次，或同一 issue run 连续 failed ≥2 次。通过的审查、单次打回、单次失败一律不提炼。
- 动作：提炼即评论——把候选条目（❌实际做法 / ✅正确做法 / 来源 change-id）直接评论在相关 issue 并 @对应 Report-* 角色；不为 lesson 落盘单独开 issue、不开落盘 review unit、不维护任何 lesson metadata 键（git log 即台账）。
- 落盘：Report-DevOps 单点批量——随该 change feature 分支的下一次 commit 一次性 append 进 `docs/report-flow/lessons/{Report-角色}.md`（报表自持目录，**不动通用链 docs/lessons/**）；巡检发现未落条目时在既有 issue 评论 @Report-DevOps 提醒批量落盘（一个 commit），不建新单。
- 格式：三行（`- [日期] [change-id] 一句话` + ❌/✅ 两行）；条目间引用写「文件 + 条目标题短语」。

## 四、幂等硬约束

- 若最近评论已是路由交接、且目标 agent 的 run 已在跑或已完成 → 跳过勿重复路由（先查 multica issue runs 确认）。
- 同一事项本轮已处置过 → 不重复评论、不重复转移 assignee。
