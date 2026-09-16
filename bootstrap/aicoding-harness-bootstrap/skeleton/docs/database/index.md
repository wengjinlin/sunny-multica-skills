# 数据库表清单

> 全库表结构的唯一入口：按域清单在本文件，每表字段详情在 `tables/<域>.md`。
> 本目录由数据字典导出**生成**，禁止手改内容——表结构变更后按「再生成规则」执行。

## 域清单

| 域 | 表数量 | 详情 |
|---|---|---|
| {{DOMAIN_TABLE_ROW}} | {{...}} | `tables/{{...}}.md` |

<!-- 分析指引：按表名前缀分域，业务域与 product/index.md、architecture/index.md 对齐；无法归属的表进 `_unmapped` 域（前缀杂项），并在「已知异常」注明构成 -->

## 生成声明

- 数据源：{{DB_EXPORT_SOURCE}}
- 导出时间：{{DB_EXPORT_TIME}}
- 生成方式：**aicoding-db-schema-export** skill（固定脚本连库导出，禁止临时手写 SQL）→ 按 `tables/_template.md` 格式化

<!-- 分析指引：记录导出自哪个库/schema（db_type@schema 级别，不写 host/凭据）与时间戳；行数估算是统计信息近似值，精确值以 EXPLAIN / 实际 count 为准；人工回传导出的在数据源处注明「人工提供」 -->

## 再生成规则（DDL 执行后）

1. **触发**：change 含 `openspec/changes/{change-id}/ddl.sql` 且人工已执行（issue metadata `ddl=executed`）
2. **义务**：Tech-Lead 在 tasks.md 显式安排「重生成 `docs/database/` 受影响域」task，Developer 执行——文档不随 change 更新视为 task 未完成
3. **动作**：跑 **aicoding-db-schema-export** skill（全量 dump）→ 按 `tables/_template.md` 重写 ddl.sql 涉及域的 `tables/<域>.md` → 刷新本文件域清单计数、导出时间与「已知异常」→ commit + push 到本 change 的 feature 分支

## 已知异常

{{DB_KNOWN_ISSUES}}

<!-- 分析指引：导出时发现的数据字典异常（如外键约束统计为 0、列名大小写混用、公共字段缺失的老表清单）；无则写「（无）」；此类异常同步摘要到 implicit-contracts.md「实际现状」相关条款 -->
