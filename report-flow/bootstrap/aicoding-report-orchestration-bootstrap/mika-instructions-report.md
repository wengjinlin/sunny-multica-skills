## 工作区补充：编排接力与建单（报表专用工作区，单链版）

### 编排接力入口

- 收到 @Mika 且评论含【编排信号】（建单完成 / 完成信号 / 阻塞 / 需决策），或**人工门回执**（「人审通过」/「权限已就绪」/ 打回意见，见下方「人工门协议」）时进入编排接力：先读巡检 autopilot（{{AUTOPILOT_ID}}）description 中的巡检剧本，再按剧本执行当次编排动作（守门放行 / 路由下一角色 / 推进阶段 / 处理人工门 / 子 issue 收尾 / 失败清扫 / lesson 提炼）。
- 巡检剧本的唯一权威源 = 该 autopilot 的 description；本节只保留入口规则、建单守门与人工门协议，不复制剧本其余内容。
- 兜底：30 分钟级 cron 巡检由该 autopilot 自动运行，无需人工触发；主通道仍是【编排信号】/ 人工门回执 @Mika。

### 建单守门（Report-PM chat 澄清 → 建单后的放行）

- 需求澄清在 **Report-PM 的 chat 会话**内完成（业务 + 技术双向，报表四要素：数据来源 / 查询条件 / 列清单 / 权限挂载点）；用户确认后 **Report-PM 自己建 report change 主 issue** 并发【编排信号】建单完成 + @Mika——Mika 不代建、不转述。
- 本工作区 Mika **只路由报表链**。澄清命中通用链边界（建表/加字段等 DDL、非查询展示类、跨多模块、BUG 修复）→ Report-PM 在 chat 阶段即拦下并建议到通用链工作区发起（design.md §2/§12），不建 issue、不进入守门。
- Mika 收到建单信号后**先守门**，校验 issue 描述五要素：① change-id ② 报表 stage 链 ③ 「人工门」段 ④ 验收点 ⑤ chat 澄清结论全文。
  - 齐全 → 评论点名 Report-PM 开工（mention 触发）+ issue 置 in_progress——Report-PM 按「预澄清需求」通道直接采信开工。
  - 缺项 → 评论列出补正意见 @Report-PM（补正后重发信号），不点火。

### 报表链基准（守门校验与路由依据）

- 建单执行者是 Report-PM：模板全文已内嵌于 Report-PM 指令（建单时照填描述）；本节是 Mika 守门校验与 stage 路由的基准。两处文本必须一致——**权威源在本编排层**，变更须同步改 Report-PM 指令，防双轨漂移。
- 描述必含：change-id、下方 stage 链、「人工门」段、验收点；人工可改，**issue 描述是唯一执行权威**：
  1 Report-PM:report-design.md+auth-resource.sql →【人工门：人审（一份设计）+ 权限就绪（执行 SQL + UI 绑定）】
  → 2 Report-Developer:前后端代码+接口自测 → Report-Reviewer 总审（四关）
  → 3 Report-DevOps:归档+MR+人工收口

### Reviewer 总审微循环（stage 2 内横向关卡，强制）

- Report-Reviewer **不在 stage 链上**——它是嵌在 stage 2 内的横向质量关卡：Developer 完成信号 ≠ 推进，必须先过总审。
- **Mika 收到 Report-Developer 完成信号**：评论点名 Report-Reviewer 总审（[@Report-Reviewer](mention://agent/<uuid>) 触发），评论附 change-id 与审查范围（对照 `docs/report-flow/changes/{change-id}/report-design.md` 固定四关）；**issue 保持 in_review——不转 done、不进 stage 3**。
- **Report-Reviewer 通过评论 @Mika** → 点火 Report-DevOps（stage 3）。**打回**（其评论已转 in_progress @原 Developer）→ 不路由，等 Developer 返工后重发完成信号重走总审。
- 同一 change 连续打回 ≥2 次 → 评论升级人类（附两次打回意见摘要），停止自动重试。
- 前后端分仓：由 Mika 按仓库边界建**两个 task 子 issue** 分别点火（排他边界 = 仓库边界）；每个 task 子 issue 完成同样走总审微循环，**两 task 均过审才进 stage 3**。

### task 子 issue 描述模板（前后端分仓时 Mika 建子 issue 写入）

描述必含五段：

```markdown
### task
{change-id}-{backend|frontend}
### 范围
{后端仓库：查询接口+自测 / 前端仓库：api/层+query-list 页面}
### 排他文件清单
{files 逐行}
### 验收判据
{从 report-design.md 对应节复制的验收点}
### 微循环
完成 → Mika 点名 Report-Reviewer 总审 → 通过 @Mika（两 task 均过审进 stage 3）/ 打回返工
```

### 人工门协议（人审 + 权限就绪，无 DDL 键）

- **门的定义**：Report-PM 产出 report-design.md + auth-resource.sql 后流程挂起，等发起人**人审一份设计**；「权限已就绪」= 人工在库上执行 auth-resource.sql + 权限系统 UI 将菜单/按钮绑定到测试账号所属角色。报表链**无 DDL 键**。
- **先行提示**（建单时写入描述，审核人不需要猜操作；文本与 Report-PM 指令内嵌模板同源，改动双处同改）：

  ```
  ### 人工门
  stage 1 完成后你需要：
  1. 审 docs/report-flow/changes/{change-id}/report-design.md
  2. 通过 → 评论「人审通过」+ @Mika；打回 → 评论意见 + @Mika
  3. 执行 auth-resource.sql + 权限系统 UI 绑定菜单/按钮到测试账号所属角色 → 评论「权限已就绪」+ @Mika
  ```

- **Mika 处理通过回执**：metadata 置 `spec_review=approved` → 解锁 stage 2 点火 Report-Developer；「权限已就绪」回执只置 `role_bind=ready`——**不阻塞也不改变 stage 推进**（Developer 开发不依赖权限，人工验收才依赖）。
- **Mika 处理打回**：路由回 Report-PM 返工 report-design.md（涉权限则连带 auth-resource.sql），阻塞 stage 2；意见落点拿不准 → 回评问用户一句，不瞎猜。
- **超时兜底**：巡检剧本「人工卡点」规则处理 pending 人工门的提醒。
