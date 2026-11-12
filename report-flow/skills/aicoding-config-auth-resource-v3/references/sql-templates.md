# auth-resource.sql 模板（Oracle，幂等）

> 风格对齐 `openspec/changes/{change-id}/ddl-oracle.sql`：注释头 + 分段 + 文末回滚段。占位符 `{change-id}`、`{模块路由前缀}`（如 `ckgl`）、`{页面}`、`{组件名}` 按实际 change 替换。**业务接口永不写 EVERYONE / AUTH_ROLE_RESOURCE_URL。**
>
> **注释排版硬规则（受限人工通道只认连续平铺语句）**：每段执行 SQL 的注释**只写段头**——段号 + 说明 + 预期值集中在段头注释里；**SQL 语句之间不插注释、语句行尾不挂注释**，一个段 = 段头注释块 + 连续平铺的多条 SQL。

## 文件骨架（六段）

```sql
-- =====================================================================
-- {change-id} 权限资源注册（菜单树 + 接口登记 + 按钮登记，目标库 dev，地址以环境配置为准）
-- 执行方式：人工执行（与 ddl-oracle.sql 同等待遇，agent 不直连数据库）
-- 红线：只含资源注册，不含任何角色授权语句；业务接口一律不加 EVERYONE
-- 幂等：全部 MERGE，可重复执行
-- 回滚：按文末回滚段执行 DELETE
-- =====================================================================

-- 0. 前置观测（人工执行后把输出贴回判读）：
--    前 3 查计数应 0 行，非 0 先判读再继续；第 4 查应 0 且执行后仍 0
--    后 3 查为惯例观测：C_AREA 拼写核对、『新增』行核对 C_STOREMETHOD 承载与惯例列、C_ICON 取值惯例（供第 4 段与图标对齐）
SELECT COUNT(*) FROM AUTH_RES_MENU          WHERE C_URL LIKE '/{模块路由前缀}%';
SELECT COUNT(*) FROM AUTH_MODULE_URL        WHERE C_URL LIKE '/{模块路由前缀}/%';
SELECT COUNT(*) FROM AUTH_RES_BUTTON        WHERE N_PARKEYID IN (SELECT ID FROM AUTH_RES_MENU WHERE C_URL LIKE '/{模块路由前缀}%');
SELECT COUNT(*) FROM AUTH_ROLE_RESOURCE_URL WHERE C_URL LIKE '/{模块路由前缀}/%';
SELECT DISTINCT C_AREA FROM AUTH_RES_BUTTON;
SELECT ... FROM AUTH_RES_BUTTON b JOIN AUTH_RES_MENU m ... WHERE b.C_NAME='新增';
SELECT C_MODNAME, C_ICON FROM AUTH_RES_MENU WHERE C_ICON IS NOT NULL AND ROWNUM <= 10;

-- 1. 菜单树：一级目录行（C_VIEWPATH='Layout'，N_PARKEYID=0）
<目录 MERGE>

-- 2. 菜单树：页面行（C_TYPE='1'，C_VIEWPATH 直读 views，N_PARKEYID 挂目录行）
<页面 MERGE × 每页面>

-- 3. 接口登记：AUTH_MODULE_URL（N_MODULEID 子查询挂页面行；C_TYPE 1=查询 2=按钮写接口）
<接口 MERGE × 每接口>

-- 4. 按钮资源：AUTH_RES_BUTTON（查询列表页按钮；N_PARKEYID 挂页面行）
<按钮 MERGE × 每按钮>

-- 5. API 放行（本段无 SQL）——注释说明放行走权限系统 UI 真实角色绑定
<放行说明注释>

-- =====================================================================
-- 验证 SELECT（人工执行后把输出贴回 issue，agent 判读；预期行数写注释）
-- =====================================================================
<验证 SELECT>

-- =====================================================================
-- 回滚（按需人工执行，注释形式 DELETE，顺序：按钮 → 接口 → 菜单）
-- =====================================================================
```

## 一级目录 MERGE

```sql
MERGE INTO AUTH_RES_MENU t
USING (SELECT RAWTOHEX(SYS_GUID()) AS guid, '/{模块路由前缀}' AS c_url FROM DUAL) s
ON (t.C_URL = s.c_url AND t.C_TYPE = '1')
WHEN NOT MATCHED THEN
  INSERT (C_MODNUMB, C_MODNAME, C_MODDESC, N_PARKEYID, C_TYPE, C_URL, C_VIEWPATH, C_VIEWNAME, C_SHOW, C_SIGN, C_ICON, N_ORDER, C_AUTH, C_SYSTEM)
  VALUES (LOWER(SUBSTR(s.guid,1,8)  ||'-'|| SUBSTR(s.guid,9,4)  ||'-'||
          SUBSTR(s.guid,13,4) ||'-'|| SUBSTR(s.guid,17,4) ||'-'||
          SUBSTR(s.guid,21,12)),
          '{模块中文名}', '{模块中文名}', 0, '1', s.c_url, 'Layout', NULL, '0', '1', '{菜单图标}', 0, '1', 'ECQ');
```

要点：`SYS_GUID()` 必须在 USING 子句**调用一次**（`RAWTOHEX(SYS_GUID()) AS guid`），INSERT 内只做 SUBSTR 格式化——调多次会拼出拼接怪 UUID。目录行 C_VIEWNAME 留空；**C_SHOW='0' 是显示**；**C_ICON 必须显式出现在 INSERT 列表**——取值 lucide 体系（`lucide:<icon-name>`），菜单/页面行**按语义匹配**选图标（如 `lucide:warehouse`）；无合适语义可 NULL（为空时前端有随机图标兜底）。

## 页面行 MERGE（每页面一份）

```sql
MERGE INTO AUTH_RES_MENU t
USING (SELECT RAWTOHEX(SYS_GUID()) AS guid, '/{模块路由前缀}/{页面}' AS c_url FROM DUAL) s
ON (t.C_URL = s.c_url AND t.C_TYPE = '1')
WHEN NOT MATCHED THEN
  INSERT (C_MODNUMB, C_MODNAME, C_MODDESC, N_PARKEYID, C_TYPE, C_URL, C_VIEWPATH, C_VIEWNAME, C_SHOW, C_SIGN, C_ICON, N_ORDER, C_AUTH, C_SYSTEM)
  VALUES (LOWER(SUBSTR(s.guid,1,8)  ||'-'|| SUBSTR(s.guid,9,4)  ||'-'||
          SUBSTR(s.guid,13,4) ||'-'|| SUBSTR(s.guid,17,4) ||'-'||
          SUBSTR(s.guid,21,12)),
          '{页面中文名}', '{页面中文名}',
          (SELECT ID FROM AUTH_RES_MENU WHERE C_URL = '/{模块路由前缀}' AND C_TYPE = '1'),
          '1', s.c_url, '/{模块路由前缀}/{组件文件名}', '{组件name}', '0', '1', '{菜单图标}', 0, '1', 'ECQ');
```

要点：`C_VIEWPATH` 必须是从 `views/` 起算的相对路径（如 `/ckgl/RkQuery`，不含 .vue）；`C_VIEWNAME` = 组件 `defineOptions` name（keepAlive 唯一）；**`C_SHOW='0'` 是显示**；`C_ICON` 同目录行要点（显式写列，lucide 语义匹配或 NULL）。

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

`C_TYPE='2'` 用于按钮写接口（`/insert` 等）；`C_DESC` 中文描述。接口 URL 拼法 = `@RequestMapping` 值 + `/` + 方法名（本库惯例：selectForPage / insert）。

## 按钮登记 MERGE（AUTH_RES_BUTTON，每按钮一份）

```sql
MERGE INTO AUTH_RES_BUTTON t
USING (SELECT (SELECT ID FROM AUTH_RES_MENU WHERE C_URL = '/{模块路由前缀}/{页面}' AND C_TYPE = '1') AS menu_id FROM DUAL) s
ON (t.N_PARKEYID = s.menu_id AND t.C_NAME = '{按钮中文名}')
WHEN NOT MATCHED THEN
  INSERT (C_NAME, N_PARKEYID, C_AREA, C_STOREMETHOD, C_ICON, C_SIGN, N_ORDER, C_AUTH, C_SYSTEM)
  VALUES ('{按钮中文名}', s.menu_id, 'searchTable', '{按钮code}', '{按钮图标}', '1', 0, '1', 'ECQ');
```

要点：

- 按钮行没有 URL 列，判重键 = `N_PARKEYID + C_NAME`；父行 ID 子查询放 USING 子句（MERGE 的 ON 不能直接写子查询）。
- `C_AREA`：查询列表页工具栏区域——取值以第 0 段 `SELECT DISTINCT C_AREA` 实际输出为准（模板按 `searchTable` 写，若现库为其它拼写则替换）。
- **按钮 code 写 `C_STOREMETHOD`**（前端实证：`params.button.code` 映射 `cStoremethod`，页面按 `=== 'add'` 分发）。**不要写 C_CALLMETHOD**——那是调后端方法列（导出方法配置/导入后台接口），新增/修改类按钮留空。
- code 取值：新增 = `add`（前端代码实证）；修改/启用/禁用/导入/导出无本地实证——观测现库同类按钮行对齐，无参照列封闭式问题问发起人，不猜。
- **`C_ICON` 按固定映射填（硬规范，不语义匹配）**：

| 操作 | code（待实证项除外） | 图标 |
|---|---|---|
| 新增 | `add` | `lucide:copy-plus` |
| 修改 | 待确认 | `lucide:pencil-sparkles` |
| 启用 | 待确认 | `lucide:power` |
| 禁用 | 待确认 | `lucide:power-off` |
| 导入 | 待确认 | `lucide:folder-up` |
| 导出 | 待确认 | `lucide:folder-down` |

- 未实证列（C_VALID/C_CLASS/C_TEMPLATETYPE）留空；现有『新增』行有非空惯例值则对齐补齐。文件注释头写明 C_AREA 拼写核对项。

## 放行说明段（无 SQL，固定注释模板）

```sql
-- 5. API 放行（本段无 SQL）
--    业务模块接口一律不加 EVERYONE（EVERYONE 仅基础框架接口使用）。
--    放行方式：发起人在权限系统 UI 给真实角色绑定上述菜单+接口（人工操作，本文件永不生成授权语句）。
--    角色绑定前调用接口将报 SEC-00021，属预期；绑定后由平台生成 AUTH_ROLE_RESOURCE_URL 缓存行。
```

## 标准换算（design.md → 资源行）

| design.md 内容 | 产物 |
|---|---|
| 路由 children 一条 `/a/b`（查询列表页，组件 `views/a/B.vue` name `BQuery`） | 菜单页面行 1（C_VIEWPATH=`/a/B`，C_VIEWNAME=`BQuery`）+ AUTH_MODULE_URL 查询行 1（C_TYPE=1） |
| 该页 resourceConfig 有 add 按钮且 Controller 有 insert | + AUTH_MODULE_URL 写接口行 1（C_TYPE=2）+ AUTH_RES_BUTTON 按钮行 1 |
| 只读页（无按钮） | 仅查询接口相关行 |
| 新业务域一级目录 | 目录行 1（C_VIEWPATH='Layout'，N_PARKEYID=0） |
| Controller 其它写方法 | 与 insert 同法，行数与接口一一对应写进验证注释 |

**任何形态都不产 AUTH_ROLE_RESOURCE_URL 行**（业务接口不放 EVERYONE，放行走 UI 真实角色绑定）。

## 验证与回滚（骨架）

```sql
-- 验证 SELECT（人工执行后把输出贴回 issue，agent 判读）：
-- 预期：菜单行 N+1（含目录）；AUTH_MODULE_URL 行 M；按钮行 K；末查 COUNT 预期 0（UI 绑定角色后才会非 0）
SELECT ID, C_MODNUMB, C_MODNAME, C_URL, C_TYPE, C_VIEWPATH, C_VIEWNAME, C_SHOW, C_ICON, N_PARKEYID
  FROM AUTH_RES_MENU WHERE C_URL LIKE '/{模块路由前缀}%' ORDER BY N_PARKEYID, C_URL;
SELECT ID, N_MODULEID, C_URL, C_TYPE, C_DESC FROM AUTH_MODULE_URL WHERE C_URL LIKE '/{模块路由前缀}/%' ORDER BY C_URL;
SELECT ID, C_NAME, N_PARKEYID, C_AREA, C_STOREMETHOD, C_ICON, C_SIGN, C_AUTH
  FROM AUTH_RES_BUTTON WHERE N_PARKEYID IN (SELECT ID FROM AUTH_RES_MENU WHERE C_URL LIKE '/{模块路由前缀}%');
SELECT COUNT(*) AS cnt FROM AUTH_ROLE_RESOURCE_URL WHERE C_URL LIKE '/{模块路由前缀}/%';
-- 回滚（按需人工执行，注释形式 DELETE，顺序：按钮 → 接口 → 菜单）
-- DELETE FROM AUTH_RES_BUTTON WHERE N_PARKEYID IN (SELECT ID FROM AUTH_RES_MENU WHERE C_URL LIKE '/{模块路由前缀}%');
-- DELETE FROM AUTH_MODULE_URL WHERE C_URL LIKE '/{模块路由前缀}/%';
-- DELETE FROM AUTH_RES_MENU   WHERE C_URL LIKE '/{模块路由前缀}%';
```

## 完整实例

`openspec/changes/add-warehouse-mgmt/auth-resource.sql`（目录行+三页面行+5 接口行+2 按钮行+放行说明段）。
