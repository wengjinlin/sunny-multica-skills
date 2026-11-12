# Report-Reviewer 总审四关详单

只读审查，对照 `docs/report-flow/changes/{change-id}/report-design.md` 固定四关（报表恒走 quick，不做通用链 4/10 关路由判断）。任何一关命中打回条件 → 打回（评论意见 + issue 置 in_progress @原 Report-Developer）；四关全过 → 产出 `review-reports/review-report.md` 并评论通过 @Mika。连续 2 次打回 → 评论升级人类。

## ① 接口契约关

| 审什么 | 打回条件 |
|---|---|
| method / path / 入参 / 响应结构 / 分页字段 ↔ report-design.md「接口契约」逐项比对 | 任何偏离 |

## ② 查询条件与列关

| 审什么 | 打回条件 |
|---|---|
| 页面查询区字段 ↔ 设计「查询条件表」；列表列 ↔ 设计「列清单」（名称/格式/顺序） | 漏项、错位、擅自增删 |

## ③ 组件与权限关

| 审什么 | 打回条件 |
|---|---|
| 页面结构符合 query-list 模板用法（lookup skill 为准）；菜单/按钮权限编码 ↔ auth-resource.sql 一致 | 枚举外选型未声明；编码不一致 |

## ④ 安全与规范关

| 审什么 | 打回条件 |
|---|---|
| SQL 无注入（参数化）、无 select *、深分页、软删除/数据权限过滤符合宪法；命名/分层符合 CLAUDE.md | 任何红线 |

**兼核零侵入红线**：diff 中出现写面 B（`docs/report-flow/**`）与写面 A（业务代码）之外的任何改动 → 直接打回（design.md §9.1 禁改面）。
