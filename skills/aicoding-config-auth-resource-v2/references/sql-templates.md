# auth-resource.sql 模板（Vue2 老框架，Oracle，幂等，含表结构对齐段）

> 风格对齐 ddl.sql：注释头 + 分段 + 文末回滚段。占位符 `{change-id}`、`{模块路由前缀}`（如 `sampleLedger`）、`{页面}`、`{组件名}`、`{系统标识}`（目标前端 `.env` 的 `VUE_APP_CURRENT_SYSTEM` 值，**按仓库实际取值，不硬编码**）按实际 change 替换。**业务接口永不写 EVERYONE / AUTH_ROLE_RESOURCE_URL。**
>
> **注释排版硬规则（受限人工通道只认连续平铺语句）**：每段执行 SQL 的注释只写段头——段号 + 说明 + 预期值集中在段头注释里；SQL 语句之间不插注释、语句行尾不挂注释，一个段 = 段头注释块 + 连续平铺的多条 SQL。

## 文件骨架（单文件，段次）

```sql
-- =====================================================================
-- {change-id} 权限资源注册（Vue2 老框架：表结构对齐 + 菜单树 + 接口 + 按钮 + 字段，目标库 dev，地址以环境配置为准）
-- 执行方式：人工执行（与 ddl.sql 同等待遇，agent 不直连数据库）
-- 红线：只含资源注册，不含任何角色授权语句；业务接口一律不加 EVERYONE
-- 幂等：结构段 PL/SQL 存在性判块，注册段全部 MERGE，可重复执行
-- 回滚：按文末回滚段执行 DELETE
-- =====================================================================

-- -1. 表结构对齐观测（人工执行后把输出贴回判读）：
--     五表现有列数 + 现有列名清单，与段头注释所列期望清单比对，缺表/缺列才执行后续 CREATE/ALTER
SELECT table_name, COUNT(*) AS col_cnt FROM user_tab_columns
 WHERE table_name IN ('AUTH_RES_MENU','AUTH_MODULE_URL','AUTH_RES_BUTTON','AUTH_RES_FIELD','AUTH_ROLE_RESOURCE_URL') GROUP BY table_name;
SELECT table_name, column_name, data_type, data_length FROM user_tab_columns
 WHERE table_name IN ('AUTH_RES_MENU','AUTH_MODULE_URL','AUTH_RES_BUTTON','AUTH_RES_FIELD') ORDER BY table_name, column_id;

<缺表 CREATE TABLE 幂等块 × 每缺表>
<缺列 ALTER TABLE 幂等块 × 每缺列>
<无差异时：本段仅保留上方观测 SELECT + 注释「结构比对无差异，无需 DDL」>

-- 0. 前置观测（人工执行后把输出贴回判读）：
--    前 4 查计数应 0 行，非 0 先判读再继续；
--    后 4 查为惯例观测：菜单根行 C_TYPE/C_MODNUMB/C_SYSTEM 形态（目录行定值全模块统一）、
--    现有『新增』按钮行惯例列、现有字段行惯例、菜单行 C_ICON 取值体系（baseicon-/el-icon-/svg 名）
SELECT COUNT(*) FROM AUTH_RES_MENU   WHERE C_URL LIKE '/{模块路由前缀}%';
SELECT COUNT(*) FROM AUTH_MODULE_URL WHERE C_URL LIKE '/{模块路由前缀}/%';
SELECT COUNT(*) FROM AUTH_RES_BUTTON WHERE N_PARKEYID IN (SELECT ID FROM AUTH_RES_MENU WHERE C_URL LIKE '/{模块路由前缀}%');
SELECT COUNT(*) FROM AUTH_RES_FIELD  WHERE N_PARKEYID IN (SELECT ID FROM AUTH_RES_MENU WHERE C_URL LIKE '/{模块路由前缀}%');
SELECT ID, C_TYPE, C_VIEWPATH, C_URL, C_MODNUMB, C_ICON, C_SYSTEM FROM AUTH_RES_MENU WHERE N_PARKEYID = 0;
SELECT * FROM AUTH_RES_BUTTON WHERE C_NAME = '新增' AND ROWNUM <= 3;
SELECT * FROM AUTH_RES_FIELD WHERE ROWNUM <= 3;
SELECT C_MODNAME, C_ICON FROM AUTH_RES_MENU WHERE C_ICON IS NOT NULL AND ROWNUM <= 10;

-- 1. 菜单树：一级目录行（C_VIEWPATH='Layout'，N_PARKEYID=0；C_TYPE 取第 0 段观测值）
<目录 MERGE>

-- 2. 菜单树：页面行（C_VIEWPATH 直读 views，N_PARKEYID 挂目录行）
<页面 MERGE × 每页面>

-- 3. 接口登记：AUTH_MODULE_URL（N_MODULEID 子查询挂页面行；C_TYPE 1=查询 2=按钮写接口）
<接口 MERGE × 每接口>

-- 4. 按钮资源：AUTH_RES_BUTTON（工具栏无 C_SUB_AREA；操作列 C_SUB_AREA='columnTable'；C_ICON 按固定映射）
<按钮 MERGE × 每按钮>

-- 5. 字段资源：AUTH_RES_FIELD（searchForm=查询表单 / searchTable=表格列，按 design.md 字段清单）
<字段 MERGE × 每字段>

-- 6. API 放行（本段无 SQL）——注释说明放行走权限系统 UI 真实角色绑定
<放行说明注释>

-- =====================================================================
-- 验证 SELECT（人工执行后把输出贴回 issue，agent 判读；预期行数写注释）
-- =====================================================================
<验证 SELECT>

-- =====================================================================
-- 回滚（按需人工执行，注释形式 DELETE，顺序：字段 → 按钮 → 接口 → 菜单）
-- =====================================================================
```

## 表结构对齐幂等块（第 -1 段，v2 新增）

**生成规则**：以 [auth-tables.md](auth-tables.md) 各表「列结构」节为所需结构基准（源=平台同构库活库导出）。第 -1 段观测输出贴回后比对：**缺整表 → 生成 CREATE TABLE 幂等块；缺列 → 生成 ALTER TABLE ADD 幂等块**；类型/长度不一致**不生成变更**（记入交办评论由发起人决策，本技能禁 MODIFY/DROP）。比对无差异时本段只留观测 SELECT 与结论注释。

缺表块（以 AUTH_RES_FIELD 为例，其余表照 auth-tables.md 列结构展开）：

```sql
DECLARE v_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cnt FROM user_tables WHERE table_name = 'AUTH_RES_FIELD';
  IF v_cnt = 0 THEN
    EXECUTE IMMEDIATE 'CREATE TABLE AUTH_RES_FIELD (ID NUMBER NOT NULL, C_LABEL VARCHAR2(200), N_PARKEYID NUMBER, C_CRENUMB VARCHAR2(100), D_CREDATE DATE DEFAULT sysdate, C_AREA VARCHAR2(100), C_FIELDTYPE VARCHAR2(100), C_PROP VARCHAR2(100), C_SELTYPE VARCHAR2(100), C_SELVAL VARCHAR2(200), C_SIGN VARCHAR2(50), C_SHOW VARCHAR2(50), N_ORDER NUMBER, C_SYSTEM VARCHAR2(100), N_I18NDATA NUMBER DEFAULT 0, TS DATE)';
    EXECUTE IMMEDIATE 'ALTER TABLE AUTH_RES_FIELD ADD CONSTRAINT PK_AUTH_RES_FIELD PRIMARY KEY (ID)';
    EXECUTE IMMEDIATE 'CREATE INDEX IDX_AUTH_RES_FIELD ON AUTH_RES_FIELD (N_PARKEYID)';
  END IF;
END;
/
```

缺列块：

```sql
DECLARE v_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cnt FROM user_tab_columns WHERE table_name = 'AUTH_RES_MENU' AND column_name = 'C_TEMPLATETYPE';
  IF v_cnt = 0 THEN
    EXECUTE IMMEDIATE 'ALTER TABLE AUTH_RES_MENU ADD C_TEMPLATETYPE VARCHAR2(50)';
  END IF;
END;
/
```

要点：一个块一个对象（表/列），独立判存在；注释只写段头；块间连续平铺；`/` 结束 PL/SQL 块。

## 一级目录 MERGE

```sql
MERGE INTO AUTH_RES_MENU t
USING (SELECT '/{模块路由前缀}' AS c_url FROM DUAL) s
ON (t.C_URL = s.c_url AND t.C_TYPE = '{第0段观测的目录行C_TYPE}')
WHEN NOT MATCHED THEN
  INSERT (C_MODNUMB, C_MODNAME, C_MODDESC, N_PARKEYID, C_TYPE, C_URL, C_VIEWPATH, C_VIEWNAME, C_SHOW, C_SIGN, C_ICON, N_ORDER, C_AUTH, C_TEMPLATETYPE, C_SYSTEM)
  VALUES ('{第0段观测的C_MODNUMB形态}', '{模块中文名}', '{模块中文名}', 0, '{目录行C_TYPE}', s.c_url, 'Layout', NULL, '0', '1', '{观测对齐的图标}', 0, '1', NULL, '{系统标识}');
```

要点：目录行 C_VIEWNAME 留空、C_TEMPLATETYPE 留空（模板类型属页面行）；**C_SHOW='0' 是显示**；C_TYPE 与 C_MODNUMB 以第 0 段观测为准再定值；老框架 C_MODNUMB 无 UUID 惯例约束（存在 'XTGL' 短代码形态），**不照抄 v3 的 SYS_GUID() 写法，观测后按现库同类根行形态填**；C_SYSTEM 用 `{系统标识}` 占位（取目标前端 `.env` 的 `VUE_APP_CURRENT_SYSTEM`，第 0 段现库观测复核）。

## 页面行 MERGE（每页面一份）

```sql
MERGE INTO AUTH_RES_MENU t
USING (SELECT '/{模块路由前缀}/{页面}' AS c_url FROM DUAL) s
ON (t.C_URL = s.c_url AND t.C_TYPE = '1')
WHEN NOT MATCHED THEN
  INSERT (C_MODNUMB, C_MODNAME, C_MODDESC, N_PARKEYID, C_TYPE, C_URL, C_VIEWPATH, C_VIEWNAME, C_SHOW, C_SIGN, C_ICON, N_ORDER, C_AUTH, C_TEMPLATETYPE, C_SYSTEM)
  VALUES ('{C_MODNUMB形态}', '{页面中文名}', '{页面中文名}',
          (SELECT ID FROM AUTH_RES_MENU WHERE C_URL = '/{模块路由前缀}' AND N_PARKEYID = 0),
          '1', s.c_url, '/{views下相对路径不含.vue}', '{组件name}', '0', '1', '{图标}', 0, '1', '{列表页则0，否则NULL}', '{系统标识}');
```

要点：`C_VIEWPATH` 以 `/` 开头、不含 .vue、从 `src/views/` 起算（require 直读，错路径点菜单无响应）；`C_VIEWNAME` = 组件 `name`（keepAlive 唯一）；查询列表页 `C_TEMPLATETYPE='0'`；父行定位用 N_PARKEYID=0 条件（目录行唯一）。

## 接口登记 MERGE（AUTH_MODULE_URL，每接口一份）

```sql
MERGE INTO AUTH_MODULE_URL t
USING (SELECT '/{模块路由前缀}/{页面}/selectForPage' AS c_url FROM DUAL) s
ON (t.C_URL = s.c_url)
WHEN NOT MATCHED THEN
  INSERT (N_MODULEID, C_URL, C_TYPE, C_DESC)
  VALUES ((SELECT ID FROM AUTH_RES_MENU WHERE C_URL = '/{模块路由前缀}/{页面}' AND C_TYPE = '1'),
          s.c_url, '1', '{页面中文名}-分页查询');
```

`C_TYPE='2'` 用于按钮写接口；接口 URL 以 design.md 接口清单为准（Controller 映射+方法名）。

## 按钮登记 MERGE（AUTH_RES_BUTTON，每按钮一份）

```sql
MERGE INTO AUTH_RES_BUTTON t
USING (SELECT (SELECT ID FROM AUTH_RES_MENU WHERE C_URL = '/{模块路由前缀}/{页面}' AND C_TYPE = '1') AS menu_id FROM DUAL) s
ON (t.N_PARKEYID = s.menu_id AND t.C_NAME = '{按钮中文名}')
WHEN NOT MATCHED THEN
  INSERT (C_NAME, N_PARKEYID, C_AREA, C_STOREMETHOD, C_SUB_AREA, C_ICON, C_SIGN, N_ORDER, C_AUTH, C_SYSTEM)
  VALUES ('{按钮中文名}', s.menu_id, 'searchTable', '{handle}', '{操作列则columnTable，工具栏则NULL}', '{按固定映射或观测对齐图标}', '1', 0, '1', '{系统标识}');
```

要点：

- 判重键 = `N_PARKEYID + C_NAME`；父行 ID 子查询放 USING 子句。
- **handle 写 `C_STOREMETHOD`**（initButtonItem 实证 `handle: cStoremethod`），**不写 C_CALLMETHOD**。handle 必须与 design.md 页面分发串一致：新增 `add`、查询 `search`、重置 `reset`、删除 `del`、导入 `daoru/show`、导出 `daochu/show`、自定义 `模块/动作`。
- 工具栏按钮不写 C_SUB_AREA（list.js 过滤 `!cSubArea`）；操作列按钮 `C_SUB_AREA='columnTable'`。
- `C_AREA='searchTable'`（一手实证拼写）。
- **`C_ICON` 按固定映射填（硬规范，不做语义匹配、不观测）**：

| 操作 | handle（固定映射项） | 图标 |
|---|---|---|
| 新增 | `add` | `sunnyfont baseicon-add` |
| 修改 | 待实证 | `sunnyfont baseicon-update` |
| 删除 | `del` | `sunnyfont baseicon-del` |
| 导入 | `daoru/show` | `sunnyfont baseicon-import` |
| 导出 | `daochu/show` | `sunnyfont baseicon-export` |

- 映射表之外的操作（启用/禁用等）图标按现库同类行观测对齐；C_CLASS 等惯例列以第 0 段现有『新增』行观测对齐补齐。

## 字段资源 MERGE（AUTH_RES_FIELD，每字段一份）

```sql
MERGE INTO AUTH_RES_FIELD t
USING (SELECT (SELECT ID FROM AUTH_RES_MENU WHERE C_URL = '/{模块路由前缀}/{页面}' AND C_TYPE = '1') AS menu_id FROM DUAL) s
ON (t.N_PARKEYID = s.menu_id AND t.C_PROP = '{后端参数key}' AND t.C_AREA = '{searchForm或searchTable}')
WHEN NOT MATCHED THEN
  INSERT (C_LABEL, N_PARKEYID, C_AREA, C_FIELDTYPE, C_PROP, C_SELTYPE, C_SELVAL, C_SIGN, C_SHOW, C_REQUIRED, N_ORDER, C_SYSTEM)
  VALUES ('{字段中文名}', s.menu_id, '{searchForm或searchTable}', '{组件类型}', '{后端参数key}', '{下拉类必填，否则NULL}', '{下拉取值}', '1', '0', '{需校验则0否则NULL}', {序号}, '{系统标识}');
```

要点：

- 判重键 = `N_PARKEYID + C_PROP + C_AREA`（同字段可同时出表单+表格两行）。
- `C_FIELDTYPE` 与 design.md 字段清单一致（Input/Select/date/datetime/year/Cascader/spanselect…）；下拉类（Select/spanselect/Cascader）`C_SELTYPE`+`C_SELVAL` 必填（0:数据字典 1:selectOption 2:工厂 3:自定义下拉 4:其它权限），无实证值问 PM 不猜。
- **C_SHOW 同反向语义：0=显示**；未实证列（C_META/C_WIDTH/N_LG/C_DYNAMIC_*）留空，观测现有行有惯例值则对齐。
- 一个查询列表页通常 = 表单字段行 N + 表格列行 M（design.md 字段清单定）。

## 放行说明段（无 SQL，固定注释模板）

```sql
-- 6. API 放行（本段无 SQL）
--    业务模块接口一律不加 EVERYONE（EVERYONE 仅基础框架接口使用）。
--    放行方式：发起人在权限系统 UI 给真实角色绑定上述菜单+接口（人工操作，本文件永不生成授权语句）。
--    角色绑定前调用接口将报 SEC-00021，属预期；绑定后由平台生成 AUTH_ROLE_RESOURCE_URL 缓存行。
```

## 标准换算（design.md → 资源行）

| design.md 内容 | 产物 |
|---|---|
| 路由一条 `/a/b`（查询列表页，组件 `views/a/b.vue` name `BQuery`） | 菜单页面行 1（C_VIEWPATH=`/a/b`，C_VIEWNAME=`BQuery`，C_TEMPLATETYPE='0'）+ AUTH_MODULE_URL 查询行 1（C_TYPE=1）+ 字段行 N+M |
| 该页有 add 按钮且 Controller 有 insert | + AUTH_MODULE_URL 写接口行 1（C_TYPE=2）+ AUTH_RES_BUTTON 行 1（C_STOREMETHOD='add'，C_ICON='sunnyfont baseicon-add'） |
| 操作列按钮（行内） | + AUTH_RES_BUTTON 行（C_SUB_AREA='columnTable'） |
| 只读页（无按钮无字段消费） | 仅查询接口相关行 |
| 新业务域一级目录 | 目录行 1（C_VIEWPATH='Layout'，N_PARKEYID=0） |
| Controller 其它写方法 | 与 insert 同法，行数与接口一一对应写进验证注释 |
| 目标库缺权限表/缺列 | 第 -1 段幂等 CREATE TABLE / ALTER TABLE ADD 块 |

**任何形态都不产 AUTH_ROLE_RESOURCE_URL 行**（业务接口不放 EVERYONE，放行走 UI 真实角色绑定）。

## 验证与回滚（骨架）

```sql
-- 验证 SELECT（人工执行后把输出贴回 issue，agent 判读）：
-- 预期：菜单行 N+1（含目录）；AUTH_MODULE_URL 行 M；按钮行 K；字段行 F；末查 COUNT 预期 0（UI 绑定角色后才会非 0）
SELECT ID, C_MODNUMB, C_MODNAME, C_URL, C_TYPE, C_VIEWPATH, C_VIEWNAME, C_SHOW, C_ICON, C_TEMPLATETYPE, N_PARKEYID
  FROM AUTH_RES_MENU WHERE C_URL LIKE '/{模块路由前缀}%' ORDER BY N_PARKEYID, C_URL;
SELECT ID, N_MODULEID, C_URL, C_TYPE, C_DESC FROM AUTH_MODULE_URL WHERE C_URL LIKE '/{模块路由前缀}/%' ORDER BY C_URL;
SELECT ID, C_NAME, N_PARKEYID, C_AREA, C_STOREMETHOD, C_SUB_AREA, C_ICON, C_SIGN, C_AUTH
  FROM AUTH_RES_BUTTON WHERE N_PARKEYID IN (SELECT ID FROM AUTH_RES_MENU WHERE C_URL LIKE '/{模块路由前缀}%');
SELECT ID, C_LABEL, C_PROP, C_AREA, C_FIELDTYPE, C_SELTYPE, C_SELVAL, N_ORDER
  FROM AUTH_RES_FIELD WHERE N_PARKEYID IN (SELECT ID FROM AUTH_RES_MENU WHERE C_URL LIKE '/{模块路由前缀}%') ORDER BY C_AREA, N_ORDER;
SELECT COUNT(*) AS cnt FROM AUTH_ROLE_RESOURCE_URL WHERE C_URL LIKE '/{模块路由前缀}/%';
-- 回滚（按需人工执行，注释形式 DELETE，顺序：字段 → 按钮 → 接口 → 菜单）
-- DELETE FROM AUTH_RES_FIELD  WHERE N_PARKEYID IN (SELECT ID FROM AUTH_RES_MENU WHERE C_URL LIKE '/{模块路由前缀}%');
-- DELETE FROM AUTH_RES_BUTTON WHERE N_PARKEYID IN (SELECT ID FROM AUTH_RES_MENU WHERE C_URL LIKE '/{模块路由前缀}%');
-- DELETE FROM AUTH_MODULE_URL WHERE C_URL LIKE '/{模块路由前缀}/%';
-- DELETE FROM AUTH_RES_MENU   WHERE C_URL LIKE '/{模块路由前缀}%';
```

（第 -1 段建出的表不进回滚段——表结构是平台基座，回滚只清本 change 注册的数据行。）

## 完整实例

首个使用本技能的 change 产出后，将实例路径回填至此：`{change 目录}/auth-resource.sql`。
