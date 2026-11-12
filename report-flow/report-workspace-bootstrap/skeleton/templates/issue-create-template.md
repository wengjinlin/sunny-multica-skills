# Report-PM 建单模板（chat 确认后建 report change 主 issue 时照填，五要素缺一不可）

```markdown
### change-id
{change-id}

### 澄清结论（chat）
{决策表 / 数据来源 / 查询条件·列·权限要点——执行时直接采信，不再反问}

### stage 链（报表链）
1 Report-PM:report-design.md+auth-resource.sql →【人工门：人审（一份设计）+ 权限就绪（执行 SQL + UI 绑定）】
→ 2 Report-Developer:前后端代码+接口自测 → Report-Reviewer 总审（四关）
→ 3 Report-DevOps:归档+MR+人工收口

### 人工门
stage 1 完成后你需要：
1. 审 docs/report-flow/changes/{change-id}/report-design.md
2. 通过 → 评论「人审通过」+ @Mika；打回 → 评论意见 + @Mika
3. 执行 auth-resource.sql + 权限系统 UI 绑定菜单/按钮到测试账号所属角色 → 评论「权限已就绪」+ @Mika

### 验收点
{从澄清结论提炼}
```

> 守门校验基准与编排路由规则维护在编排层（Mika「工作区补充」节）；本模板与其**双处同改**，权威源在编排层。
