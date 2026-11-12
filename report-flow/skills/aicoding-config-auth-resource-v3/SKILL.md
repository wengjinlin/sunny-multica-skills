---
name: aicoding-config-auth-resource-v3
description: 新模块或新页面上线需要配置菜单/按钮权限资源时使用：从 design.md 的前端页面与按钮清单生成权限资源注册 SQL（openspec/changes/{change-id}/auth-resource.sql）。触发词：权限资源、菜单注册、按钮资源、AUTH_MODULE_URL、AUTH_RES_MENU、AUTH_RES_BUTTON、AUTH_ROLE_RESOURCE_URL、SEC-00021 没有进行配置、auth-resource.sql、三件套人工前置、二级菜单、C_VIEWPATH。适用 PM 在 stage 1 产出设计工件时；只生成 SQL 永不执行、只注册资源永不生成角色授权、业务接口永不加 EVERYONE。
metadata:
  author: mika-ecq
  version: '1.8'
---

# 权限资源 SQL 生成（auth-resource.sql，人工执行）

把「新模块上线要在权限/资源系统配菜单+按钮」这一人工前置，沉淀成 agent 可标准生成的 SQL 工件。**只生成脚本，永不执行**——`auth-resource.sql` 与 `ddl-oracle.sql` 完全同等待遇：三件套（design.md + ddl-oracle.sql + auth-resource.sql）在编码前交办，由发起人统一人工执行、回帖贴验证 SELECT 输出，agent 判读。

## 输入

`$ARGUMENTS` = change-id（如 `add-warehouse-mgmt`）或一句需求描述。
未提供时先问「哪个 change？design.md 的前端页面/按钮清单定稿了吗？」再继续。

## 何时使用本技能

- OpenSpec change 的 stage 1：PM 产出 design.md（含前端页面/按钮清单）后，同步产出三件套第三件 `auth-resource.sql`
- 新模块联调撞 `SEC-00021 没有进行配置`：先判读——若是**资源未注册**，按本技能补生成注册 SQL；若资源已注册，则是**角色未绑定**（权限系统 UI 人工操作，不归本技能）
- 用户说「配权限资源」「注册菜单」「按钮资源」「auth-resource」

## 硬红线（违反任何一条立即停止）

1. **永不执行写库 SQL**——DDL 与权限 INSERT 一视同仁；agent 永不连接数据库（目标 dev 库也不行，库地址以环境配置为准）。执行永远归发起人人工。
2. **永不生成角色授权 SQL，也永不写 AUTH_ROLE_RESOURCE_URL（含 EVERYONE 行）**——业务模块接口默认不加 EVERYONE（EVERYONE 仅用于基础框架接口）。业务接口放行 = 发起人在权限系统 UI 给真实角色绑定菜单+接口（人工操作）。生成物中不得出现任何 AUTH_ROLE_RESOURCE_URL 写语句、真实角色编号行（AUTH_ROLE_RESOURCE / AUTH_USER_ROLE 同禁）。
3. **只写一个文件**——生成物 = `openspec/changes/{change-id}/auth-resource.sql`，不改前端代码（resourceConfig 回填由发起人执行注册后另行交办，见「注册后回填」）。

## 资源模型（四表，详证见 [references/auth-tables.md](references/auth-tables.md)）

| 表 | 角色 | 关键列 |
|---|---|---|
| `AUTH_RES_MENU` 资源菜单表 | **菜单树**：一级目录 + 页面行，驱动前端路由与菜单栏 | `C_VIEWPATH`、`C_VIEWNAME`、`N_PARKEYID`、`C_TYPE`、`C_SHOW` |
| `AUTH_MODULE_URL` 菜单URL表 | **后端接口 URL 登记**：表示菜单有哪些 url 接口，每 API 一行，`N_MODULEID` 挂菜单行 | `C_URL`、`N_MODULEID`、`C_TYPE`(1菜单/2按钮/-1 everyone) |
| `AUTH_RES_BUTTON` 资源按钮表 | **工具栏按钮登记**：查询列表页按钮，`N_PARKEYID` 挂菜单行 | `C_NAME`、`C_AREA`、`C_STOREMETHOD`(code)、`C_ICON`(固定映射) |
| `AUTH_ROLE_RESOURCE_URL` 角色资源url表(用于缓存) | **API 鉴权放行缓存**（`getAPIRole` 读此表）——业务模块永不直写，UI 角色绑定的产物 | 只读知识，不出现在生成物 |

## 菜单行权威语义（前端 `router/routes/utils.ts` 逐字段印证）

- **二级菜单机制**：一级目录行 `C_VIEWPATH='Layout'`（N_PARKEYID=0，权限目录）；二级目录 `'Second'`；叶子页面行直接写 views 相对路径如 `/setting/dataDictionary/dataDictionaryQuery`——前端按 `views{C_VIEWPATH}.vue` glob 直读组件
- `C_URL`=路由路径；`C_VIEWNAME`=路由 name=组件 `defineOptions` name（keepAlive 唯一，如 `DataDictionaryQueryPage`）
- **`C_SHOW` 反向语义：0=显示，1=隐藏**（前端 `hideInMenu: cShow === '1'`），极易写反
- `C_SIGN`：0=禁用 1=启用（默认启用）；`C_TYPE`：1=菜单 4=超链接 5=弹窗 6=iframe -1=everyone 资源（-1 行不进菜单树，属基础框架机制，业务模块不用）
- `C_ICON` 菜单图标：INSERT **显式写列**（前端 `meta.icon = cIcon` 直读），取值 = **lucide 图标体系**（`lucide:<icon-name>`）。菜单/页面行按语义匹配选图标（如「物料入库」选入库语义图标）；`N_ORDER` 前端当前未消费，可 0；`C_MODNUMB` 现库 UUID 形态，`SYS_GUID()` 生成（必须在 USING 子句只调一次）

## 按钮行硬规范（v1.4）

- **按钮 code 承载列 = `C_STOREMETHOD`**（前端实证：平台 `queryAreaResource` 返回 `resButtonList`，前端 `params.button.code` 即 `cStoremethod` 值，页面按 `=== 'add'` 分发）。`C_CALLMETHOD` 是另一用途——配置按钮调用的后端方法（导出方法/导入后台接口），**不是** code 列。
- 操作 → code 取值：**新增 = `add`**（前端代码一手实证）。修改/启用/禁用/导入/导出的 code 枚举值尚无代码实证——生成前按第 0 段观测现库同类按钮行对齐，仍无参照则列封闭式问题问发起人，**不猜**。
- **按钮 C_ICON 固定映射（硬规范，不做语义匹配）**：

| 操作 | 图标 |
|---|---|
| 新增 | `lucide:copy-plus` |
| 修改 | `lucide:pencil-sparkles` |
| 启用 | `lucide:power` |
| 禁用 | `lucide:power-off` |
| 导入 | `lucide:folder-up` |
| 导出 | `lucide:folder-down` |
| 删除 | `lucide:trash-2` |

菜单/页面行图标仍按语义匹配（见上节），两规则并存勿混用。

## 标准模式 → 资源行对应（模板见 [references/sql-templates.md](references/sql-templates.md)）

| design.md 页面形态 | 菜单树 | AUTH_MODULE_URL | AUTH_RES_BUTTON |
|---|---|---|---|
| 查询列表页 + add 按钮 | 页面行 ×1（挂一级目录下） | 查询接口 ×1（C_TYPE=1）+ 写接口 ×1（C_TYPE=2） | 按钮行 ×1（C_NAME='新增'，C_STOREMETHOD='add'，C_ICON='lucide:copy-plus'） |
| 只读查询页 | 页面行 ×1 | 查询接口 ×1（C_TYPE=1） | 无 |
| 新模块一级目录 | 目录行 ×1（C_VIEWPATH='Layout'，N_PARKEYID=0） | — | — |

## 生成物结构（六段，SQL 风格对齐 ddl-oracle.sql）

**注释排版硬规则**：每段执行 SQL 的注释只写段头（段号+说明+预期值集中段头注释块），SQL 语句之间不插注释、语句行尾不挂注释——段 = 段头注释 + 连续平铺的多条语句（与 ddl.sql 同一受限人工通道，只认连续平铺语句）。

1. 注释头：change 名、目标库、执行方式=人工、红线声明
2. 第 0 段前置观测：四表计数（应 0 行，非 0 先判读）+ 惯例观测（`SELECT DISTINCT C_AREA`、现有『新增』按钮行各列、现有菜单行 `C_ICON` 取值）供第 4 段与 C_ICON 对齐（按钮 code 列已实证 `C_STOREMETHOD`，观测仅为核对现库一致）
3. 菜单树注册（第 1-2 段）：目录行 + 页面行，幂等 MERGE（C_URL 判重；子行 N_PARKEYID 用标量子查询取父行 ID）
4. 接口登记（第 3 段）+ 按钮登记（第 4 段）：AUTH_MODULE_URL 行 + AUTH_RES_BUTTON 行（判重键 N_PARKEYID+C_NAME）
5. 放行说明段（第 5 段，**无 SQL**）：注释写明放行走权限系统 UI 真实角色绑定，绑定前 SEC-00021 属预期
6. 验证 SELECT（预期行数写进**段头注释**，含 AUTH_ROLE_RESOURCE_URL 预期 0 行）+ 回滚段（注释 DELETE，顺序：按钮 → 接口 → 菜单）

## 交办流程（生成后）

1. commit push 到 change 所在分支
2. 在对应 issue 评论交办发起人：说明与 DDL 同等待遇、先跑第 0 段观测对齐（C_AREA 拼写；按钮现库惯例列）、执行后把验证 SELECT 输出贴回，并回贴页面菜单行 ID/C_MODNUMB 供前端 resourceConfig 回填、再到权限系统 UI 绑定到测试账号所属角色（即发起人给 Tester 配置 TEST_ROLE 环境变量时填的角色名；agent 无权查 env，交办文字只引用变量名不填具体值）
3. 判读回贴输出：行数与字段值符合预期 → 触发 Tester 回归（前置：UI 角色绑定完成）；不符 → 按实际输出修正 SQL，再来一轮

## 注册后回填（发起人执行并回贴 ID/C_MODNUMB 后）

前端 `config.ts` 的 `resourceConfig` 需回填真实值：`nResourceid`=页面菜单行 ID（数值），`cModnumb`=该行 `C_MODNUMB`（现库惯例 UUID 形态，test 样例 `f4e45e1f-…`；`resourceId` 保持逻辑名如 `rkQuery`）。回填以发起人回贴数据为准，另行 commit，不写进本 SQL。

## 常见错误

- 生成 ANY `AUTH_ROLE_RESOURCE_URL` 写语句（含 EVERYONE）——业务接口禁用；放行只走 UI 角色绑定，绑定前 SEC-00021 是预期不是故障
- `C_SHOW` 写 1 想显示（反了，0 才显示）
- 叶子页 `C_VIEWPATH` 写成路由/漏了 views 下子目录（必须是从 views 起算的相对路径，如 `/ckgl/RkQuery`）
- `SYS_GUID()` 在 INSERT 内调多次（会拼出拼接怪 UUID——只在 USING 子句调一次）
- 按钮行 C_AREA 拼写想当然（以现库 DISTINCT 实际值为准）
- 按钮 code 写进 `C_CALLMETHOD`（正确列是 `C_STOREMETHOD`——前端 `button.code` 映射 `cStoremethod`；`C_CALLMETHOD` 是调后端方法列，导出/导入类按钮才用）
- 按钮图标自行语义匹配（必须按固定映射表：新增 copy-plus / 修改 pencil-sparkles / 启用 power / 禁用 power-off / 导入 folder-up / 导出 folder-down）；菜单图标则相反——按语义匹配，不套用按钮映射表
- 修改/启用/禁用/导入/导出按钮的 code 值凭感觉编（只有 add 有前端实证，其余先观测现库、无参照列封闭式问题问发起人）
- 菜单行表名写成 AUTH_MODULE_URL（菜单树=AUTH_RES_MENU，AUTH_MODULE_URL 是接口 URL 表）
- 忘附回滚段 / 验证 SELECT → 发起人无法回贴，断链重演
- 执行 SQL 语句之间或行尾夹注释（受限通道整块执行会断——注释只放段头，段内语句连续平铺）

完整实例：`openspec/changes/add-warehouse-mgmt/auth-resource.sql`。
