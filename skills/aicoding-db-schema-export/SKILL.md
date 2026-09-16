---
name: db-schema-export
description: 连活库导出表结构（表/列/索引/主键/外键/注释），生成或重生成 docs/database/ 文档。脚本导出保证结果一致性，不临时手写连接与 SQL。TRIGGER：「导出数据库表结构」「生成/重生成数据库文档」「DDL 执行后刷新表文档」。
---

# db-schema-export：数据库表结构文档导出

**定位**：`docs/database/` 的唯一生成通道——初建（harness-bootstrap 第 2 步）与 DDL 人工执行后的重生成（change 收尾 task）都走本 skill。**禁止**临时手写数据库连接代码或 SQL 导出（方言差异多、结果不一致、配置问题会反复踩坑）。

## 产物与格式权威源

| 产物 | 说明 |
|---|---|
| `docs/database/index.md` | 域清单（域\|表数量\|详情）+ 生成声明 + 已知异常 + 再生成规则 |
| `docs/database/tables/<域>.md` | 每域一文件，每表一节（字段/主键/唯一索引/普通索引/外键） |

- 格式以仓库 `docs/database/tables/_template.md` 为准（仓库无该文件时按本 skill 附录格式）
- 域划分与 `docs/architecture/index.md` §1 业务模块对应表（业务域 ↔ 表前缀）保持一致

## 执行流程

### 第 1 步：确定连接信息

按优先级取值，非敏感参数随后回写 `docs/database/index.md` 生成声明（只写到 `db_type@schema` 级别，不写 host/凭据）：

1. **agent 自定义 env**（值由人类注入）：`DB_TYPE` / `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_SERVICE`（Oracle 服务名）/ `DB_SCHEMA`，密码固定 `DB_PASSWORD`
2. **仓库 `docs/database/index.md` 生成声明**：已有 db_type/schema 则只补问 host/密码
3. 都没有 → 问人类**一次**（数据库类型、host:port、user、schema/service、密码走 env）

硬规则：**密码只从环境变量 `DB_PASSWORD` 读，永不写入脚本参数、命令行、issue 评论或任何文档**。

### 第 2 步：落盘脚本并执行

先把 skill 附带脚本写入 `temp/dump_schema.py`（`temp/` 须在 .gitignore；没有 temp 目录就建），再执行：

```bash
# 驱动（按 db_type 装；Oracle 推荐 oracledb——thin 模式免装 Instant Client）
pip install oracledb                # Oracle（脚本也兼容 cx_Oracle）
pip install psycopg2-binary         # PostgreSQL
pip install mysql-connector-python  # MySQL
pip install pyodbc                  # SQL Server（需 ODBC Driver 17+）

# 密码走环境变量（Windows PowerShell: $env:DB_PASSWORD="..."）
export DB_PASSWORD='...'

python temp/dump_schema.py \
  --db-type <oracle|postgresql|mysql|sqlserver> \
  --host <host> --port <port> \
  --user <user> --password-env DB_PASSWORD \
  --service <oracle服务名>            # 仅 Oracle
  --database <库名>                  # PG/MySQL/SQL Server
  --schema <schema或库名> \
  --output temp/schema_dump.json
```

- **总是全量 dump**（数据字典查询开销小）；重生成时同样全量 dump，但只重写受影响域的文件
- 脚本输出 JSON（表/列/注释/索引/主键/外键 + meta 时间戳），供第 3 步解析

### 第 3 步：解析 JSON 生成 markdown

**域判定**：读现有 `docs/database/index.md` 域清单 + `docs/architecture/index.md` §1 的表前缀映射，逐表按前缀归域；映射不到的进 `_unmapped` 域。

**每域文件** `tables/<域>.md`（全量重写该域；格式见附录）：

- 文件头：域职责 + 表数量 + 表清单（表名|行数估算|说明）
- 每表一节：行数估算（统计信息为近似，标「约」）→ 字段表 → 主键 → 唯一索引 → 普通索引 → 外键

**index.md 刷新**（只动这三处，不动再生成规则等其他节）：

1. 域清单表：各域表数量、新增域加行
2. 生成声明：`db_type@schema` + 本次导出时间
3. 已知异常：导出发现的新异常（如外键 0 条、列名大小写混用）追加；无异常保持

**内容铁律**：字段/约束全部来自 JSON，**禁止手敲或凭记忆补**；注释缺失留空，不得编造业务含义。

### 第 4 步：域映射维护（仅当出现新前缀）

新表前缀映射不到已有域时：先归 `_unmapped` → 问人类确认归属 → 确认后**双处同刷**（`docs/database/index.md` 域清单 + `docs/architecture/index.md` §1 对应表加行）→ 再把该前缀表移入正式域文件。

### 第 5 步：验证与清理

- `docs/database/index.md` 域清单计数与 `tables/<域>.md` 实际表数一致
- `grep -rn "TODO\|FIXME\|待补" docs/database/` 无残留占位
- 删除 `temp/schema_dump.json`（脚本保留可复用，反正 temp/ 不进 git）
- 变更文件 commit + push 到当前 change 的 feature 分支（初建时随 harness-bootstrap 提交）

## 无 DB 连接降级

运行环境连不上库时：请人工在能连库的机器跑第 2 步命令，把 `schema_dump.json` 通过 issue 附件/chat 提供，从第 3 步继续（生成声明的数据源注明「人工提供导出」）。**降级也只是换人跑脚本，仍然禁止手写 SQL 导出**。

## 已知约束与失败处理

| 场景 | 处置 |
|---|---|
| Oracle 连接失败 | 确认 service 名（不是 SID 就用 service_name）；oracledb thin 不支持的老版本库改装 cx_Oracle + Instant Client |
| 权限不足 | 需数据字典只读权限（Oracle `all_*`、PG/MySQL `information_schema`、SQL Server `sys.*`）——找 DBA 授 SELECT |
| 中文注释乱码 | Oracle 设 `NLS_LANG=AMERICAN_AMERICA.AL32UTF8`；MySQL 连接已强制 utf8mb4 |
| 表数 >1000 | 按 schema 拆批跑（`--schema` 逐个） |
| 行数不准 | 数据字典行数是统计估算，文档统一标「约」；精确值需要时人工 count |

## 附录：输出格式（与骨架 tables/_template.md 同源）

```markdown
# {域} 域表详情

> {域职责一句话}。共 {N} 张表。数据源与导出时间见 ../index.md。

## 表清单

| 表名 | 行数估算 | 说明 |
|---|---|---|
| {TABLE} | 约{N} | {表注释} |

### {TABLE_NAME}（{表中文注释}）

- 行数估算：约{N}

#### 字段

| 列名 | 类型 | 长度 | 精度 | 标度 | 允许空 | 默认值 | 注释 |
|---|---|---|---|---|---|---|---|
| {COL} | {TYPE} | {LEN} | {P} | {S} | {Y/N} | {DEF} | {注释} |

#### 主键

- {约束名}（{列}）

#### 唯一索引

- {索引名}（{列}）／ 无则写「（无）」

#### 普通索引

- {索引名}（{列}）／ 无则写「（无）」

#### 外键

- {约束名}（{列} → {引用表}.{引用列}）／ 无外键约束的库统一注明「外键 0 条（关系由应用层维护）」
```
