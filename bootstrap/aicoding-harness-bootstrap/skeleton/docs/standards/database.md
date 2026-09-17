# 数据库与 SQL 规范

> 建表/改表/SQL/数据访问层变更须遵循；Reviewer 按「Mapper/SQL 变更检查清单」把关。
> 表结构现状见 `../database/index.md`；状态值/软删除/公共字段的**实际现状 vs 规范差异**见 `../architecture/implicit-contracts.md`。

## 命名规范

{{DB_NAMING_RULES}}

<!-- 分析指引：表名/列名/序列/索引/触发器命名规则（含字段前缀约定，如 c/n/d/b/ts——有才写）；新表新字段必须遵循，老表历史命名在 implicit-contracts.md 声明差异 -->

## 建表规范

{{DB_TABLE_DESIGN}}

<!-- 分析指引：主键策略（序列/自增/雪花 + 对应 Java 类型）、必含公共字段清单、软删除字段约定、索引数量上限与复合索引顺序；**PM 生成 ddl.sql 的依据**，须与 CLAUDE.md 建表规范互链 -->

## SQL 编写规范

{{DB_SQL_RULES}}

<!-- 分析指引：预编译参数强制、动态 SQL 的白名单例外、SELECT * 禁令、ORDER BY 要求、分页方式、批量操作上限、性能红线表（全表扫描/无 WHERE 写操作/全模糊/大事务等——逐条红线附处置） -->

## 事务规范

{{DB_TRANSACTION_RULES}}

<!-- 分析指引：事务注解参数（rollbackFor/timeout）、事务边界所在层、事务内禁止的操作（远程调用/大事务）、自调用失效等已知坑、跨服务事务策略 -->

## Mapper / SQL 变更检查清单

- [ ] {{DB_REVIEW_ITEM}}

<!-- 分析指引：每次改 SQL 的核对项：涉及表名（对照 ../database/tables/）/ 操作类型 / WHERE 条件列与索引命中 / 影响行数估算 / N+1 风险 / 兼容性（存量数据）/ 验证方法 / 是否动公共字段；Reviewer 的数据关卡引用本清单 -->

## 受保护目录与 DDL 流程

{{DB_MIGRATION_RULES}}

<!-- 分析指引：DDL 审核与人工执行流程——对接本 harness 人工门：PM 产 `openspec/changes/{change-id}/ddl.sql` → 人审通过 → **人工在库上执行** → 评论回执 @Mika → 重生成 ../database/ 受影响域文档；另含脚本命名与回滚要求；本节与 AGENTS.md §6 变更联动表同源 -->
