---
name: aicoding-config-auth-resource-v2
description: Vue2 老框架（vue-admin-template 系：Vue2 + vue-router 3 + element-ui）新模块或新页面上线需要配置菜单/按钮/字段权限资源时使用：从 design.md 的前端页面与按钮清单生成权限资源注册 SQL（含表结构对齐 DDL 段 + 菜单树 + 接口 + 按钮 + 字段资源）。触发词：权限资源、菜单注册、按钮资源、字段资源、AUTH_RES_MENU、AUTH_RES_BUTTON、AUTH_RES_FIELD、AUTH_MODULE_URL、SEC-00021、auth-resource.sql、C_VIEWPATH、C_STOREMETHOD、表结构对齐。本技能适用 Vue2 老框架前端；Vue3 新框架用 aicoding-config-auth-resource-v3，勿混用。只生成 SQL 永不执行、只注册资源永不生成角色授权、业务接口永不加 EVERYONE。
metadata:
  author: mika
  version: '1.1'
---

# 权限资源 SQL 生成（Vue2 老框架，人工执行）

把「新模块上线要在权限/资源系统配菜单+按钮+字段」这一人工前置，沉淀成 agent 可标准生成的 SQL 工件。**只生成脚本，永不执行**——`auth-resource.sql` 与 DDL 完全同等待遇：由发起人统一人工执行、回帖贴验证 SELECT 输出，agent 判读。

## 适用边界（与 v3 的分工，按前端框架形态区分，不按系统区分）

- **本技能（v2）＝ Vue2 老框架前端**：Vue 2.7 + vue-router 3 + element-ui + webpack `require` 加载页面 + sunnyfont/svg 图标；菜单/按钮/字段资源由 `getCurrentUserResourcesByParId` 链路驱动。
- **Vue3 新框架（Vite + lucide 图标 + resourceConfig 回填）用 `aicoding-config-auth-resource-v3`**。两者四表模型同构但前端消费链不同，模板不可互套：C_ICON 体系、按钮链路、字段资源、注册后回填四点均不同。
- 同一 change 只产一份 auth-resource.sql，按目标仓库前端形态选技能：Vue2 老框架 → 本技能；Vue3 新框架 → v3。

## 输入

`$ARGUMENTS` = change-id（如 `add-sample-mgmt`）或一句需求描述。
未提供时先问「哪个 change？design.md 的前端页面/按钮/字段清单定稿了吗？」再继续。
仓库无 `openspec/` 目录（老框架仓库现用 `docs/superpowers/specs/` 惯例）时，生成物路径先与发起人确认一次，默认仍 `openspec/changes/{change-id}/auth-resource.sql`。

## 何时使用本技能

- Vue2 老框架仓库的 change 在 PM 阶段产出 design.md（含前端页面/按钮/字段清单）后，同步产出 `auth-resource.sql`
- 新模块联调撞 `SEC-00021 没有进行配置`：先判读——**资源未注册** → 按本技能补生成注册 SQL；资源已注册 → **角色未绑定**（权限系统 UI 人工操作，不归本技能）
- 老框架列表页表单/表格列不渲染 → 大概率 **AUTH_RES_FIELD 字段资源缺失**（老框架列表页列/表单全由资源表驱动，见字段资源节）
- 用户说「配权限资源」「注册菜单」「按钮资源」「字段资源」「auth-resource」

## 硬红线（违反任何一条立即停止）

1. **永不执行写库 SQL**——DDL（含表结构对齐段）与权限 INSERT 一视同仁；agent 永不连接数据库（目标 dev 库也不行，库地址以环境配置为准）。执行永远归发起人人工。
2. **永不生成角色授权 SQL，也永不写 AUTH_ROLE_RESOURCE_URL（含 EVERYONE 行）**——业务模块接口默认不加 EVERYONE（EVERYONE 仅用于基础框架接口）。业务接口放行 = 发起人在权限系统 UI 给真实角色绑定菜单+接口（人工操作）。生成物中不得出现任何 AUTH_ROLE_RESOURCE_URL 写语句、真实角色编号行（AUTH_ROLE_RESOURCE / AUTH_USER_ROLE 同禁）。
3. **只写一个文件**——生成物 = `{change 目录}/auth-resource.sql`（表结构对齐 DDL 段作为文件内**前置段**，不拆分文件），不改前端代码。老框架无 v3 的 resourceConfig 回填机制（list mixin 用 `$route.meta.number`＝菜单行 ID 自动定位资源），注册后无需前端回填，禁止生成回填说明。

## 资源模型（四表 + 字段表，详证见 [references/auth-tables.md](references/auth-tables.md)）

| 表 | 角色 | 关键列 |
|---|---|---|
| `AUTH_RES_MENU` 资源菜单表 | **菜单树**：一级目录 + 页面行，驱动前端路由与菜单栏 | `C_VIEWPATH`、`C_VIEWNAME`、`N_PARKEYID`、`C_TYPE`、`C_SHOW` |
| `AUTH_MODULE_URL` 菜单URL表 | **后端接口 URL 登记**：每 API 一行，`N_MODULEID` 挂菜单行 | `C_URL`、`N_MODULEID`、`C_TYPE`(1菜单/2按钮/-1 everyone) |
| `AUTH_RES_BUTTON` 资源按钮表 | **工具栏/操作列按钮登记**，`N_PARKEYID` 挂菜单行 | `C_NAME`、`C_AREA`('searchTable')、`C_STOREMETHOD`(handle)、`C_SUB_AREA`、`C_ICON`(固定映射) |
| `AUTH_RES_FIELD` 资源字段表 | **老框架列表页必需**：查询表单字段 + 表格列由资源行驱动 | `C_LABEL`、`C_PROP`、`C_FIELDTYPE`、`C_AREA`('searchForm'/'searchTable') |
| `AUTH_ROLE_RESOURCE_URL` 角色资源url表(缓存) | **API 鉴权放行缓存**——业务模块永不直写，UI 角色绑定产物 | 只读知识，不出现在生成物 |

## 菜单行权威语义（Vue2 老框架 `src/store/modules/permission.js` getTreeRoutes 逐字段印证）

- **C_VIEWPATH 三值机制（与 v3 同构，require 直读）**：一级目录 `'Layout'`（N_PARKEYID=0）；二级目录 `'Second'`（layout/components/SecondaryMenu）；叶子页面行 = views 相对路径如 `/basic/companyConfiguration/companyConfigurationQuery`——前端 `require(`@/views${C_VIEWPATH}.vue`)` 直读组件（**必须以 `/` 开头、不含 .vue**；路径错 require 抛错被 catch 吞掉，表现为点菜单无响应）
- `C_URL`=路由 path；`C_VIEWNAME`=路由 name（keepAlive 唯一，= 组件 `name`）
- **`C_SHOW` 反向语义：0=显示，1=隐藏**（`hidden: cShow === '1'`），极易写反
- `C_SIGN`：0=禁用 1=启用（默认写 1）；`C_TYPE`：1=菜单 4=超链接 5=弹窗 6=iframe -1=everyone 资源——**菜单树查询传 types [0,1,4]，0 疑为目录形态；一级目录行 C_TYPE 实际取值以第 0 段观测现库根行为准，不猜**
- `C_ICON` 三体系（老框架无 lucide，v3 映射表全部不适用）：含 `baseicon-`/`el-icon-`/`iconfont` → 按字体 class 直用 `<i class>`；否则 = 本地 svg 文件名（`src/icons/svg/` 下 26 个，如 `form`/`table`）。菜单/页面行按现库同类行观测对齐选图标，无把握留空
- `C_MODNUMB`：**老库存在短代码形态**（代码实证 `'XTGL'`＝系统管理目录特判）；新行取值以现库同类行观测对齐，不预设 UUID
- 其余惯例列：`C_SYSTEM`＝目标系统标识（取目标前端 `.env` 的 `VUE_APP_CURRENT_SYSTEM` 值，**按仓库实际取值，不硬编码**）、`D_CREDATE=sysdate`、`C_AUTH='1'`

## 按钮行硬规范（`src/mixins/configurationFile/utils.js` initButtonItem 实证）

- **按钮 handle 承载列 = `C_STOREMETHOD`**（`handle: cStoremethod`），页面按 `bt.handle === 'xxx'` 分发。`C_CALLMETHOD` 是调后端方法配置列（导出方法/导入接口），不是 handle。
- **handle 实证值**（一手代码）：新增 `add`、查询 `search`、重置 `reset`、删除 `del`、导入显示 `daoru/show`、导出显示 `daochu/show`；大量页面自定义形态为 `模块/动作`（如 `material/tab2Add`）——**新按钮 handle 必须与 design.md 页面代码分发串一致，无代码实证的操作先观测现库同类行，无参照列封闭式问题问发起人，不猜**
- `C_AREA='searchTable'`（一手实证，非字典误拼 searchTabel）；`C_SUB_AREA='columnTable'` = 操作列按钮（列表行内按钮）；无 C_SUB_AREA = 工具栏按钮
- `resMenu.cTemplatetype === '0'` 开启「上下结构查询页」模板与显示设置——列表页菜单行 `C_TEMPLATETYPE='0'`
- **按钮 C_ICON 固定映射（硬规范，不做语义匹配、不观测）**：

| 操作 | 图标 |
|---|---|
| 新增 | `sunnyfont baseicon-add` |
| 修改 | `sunnyfont baseicon-update` |
| 删除 | `sunnyfont baseicon-del` |
| 导入 | `sunnyfont baseicon-import` |
| 导出 | `sunnyfont baseicon-export` |

- 其他操作（启用/禁用等无映射项）的图标按现库同类按钮行观测对齐；`C_CLASS` 同观测；`C_VALID`/`C_SIGN`/`N_ORDER`/`C_AUTH` 惯例值以观测对齐

## 字段资源行（老框架特有，v3 无此节）

`src/mixins/list.js`（列表页标配）从 `getCurrentUserResourcesByParId` 返回的 `resFieldList` 构建查询表单与表格列：`C_AREA='searchForm'` → 查询表单项，`C_AREA='searchTable'` → 表格列。**无字段资源行 = 页面表单与表格全空**——老框架新列表页必须生成 AUTH_RES_FIELD 行（行数 = design.md 字段清单），只读页/弹窗页按 design.md 判断是否需要。字段行关键字段：`C_LABEL`（中文名）、`C_PROP`（后端传参 key）、`C_FIELDTYPE`（Input/Select/date/datetime/year/Cascader/spanselect/Index…）、`N_PARKEYID`=页面菜单行 ID、`C_SYSTEM`=目标系统标识；下拉类需 `C_SELTYPE`/`C_SELVAL`，缺实证值的枚举问 PM 不猜。

## 标准模式 → 资源行对应（模板见 [references/sql-templates.md](references/sql-templates.md)）

| design.md 页面形态 | 菜单树 | AUTH_MODULE_URL | AUTH_RES_BUTTON | AUTH_RES_FIELD |
|---|---|---|---|---|
| 查询列表页（list mixin）+ add 按钮 | 页面行 ×1（挂一级目录下，C_TEMPLATETYPE='0'） | 查询接口 ×1（C_TYPE=1）+ 写接口 ×1（C_TYPE=2） | 按钮行 ×1（C_NAME='新增'，C_STOREMETHOD='add'，C_ICON='sunnyfont baseicon-add'） | 表单字段行 + 表格列字段行（按字段清单） |
| 只读查询页 | 页面行 ×1 | 查询接口 ×1（C_TYPE=1） | 无 | 按需（页面消费 resFieldList 则生成） |
| 新业务域一级目录 | 目录行 ×1（C_VIEWPATH='Layout'，N_PARKEYID=0） | — | — | — |

## 生成物结构（单文件 auth-resource.sql，段次如下）

**注释排版硬规则**（与 ddl.sql 同一受限人工通道）：每段执行 SQL 的注释只写段头（段号+说明+预期值集中段头注释块），SQL 语句之间不插注释、语句行尾不挂注释——段 = 段头注释 + 连续平铺多条语句。

1. 注释头：change 名、目标库、执行方式=人工、红线声明
2. **第 -1 段 表结构对齐（v2 新增）**：先观测四表现有结构（all_tab_columns 计数输出贴回），agent 比对所需结构（references/auth-tables.md 列清单，源=平台同构库活库导出）——**缺表生成幂等 CREATE TABLE、缺列生成幂等 ALTER TABLE ADD**（PL/SQL 存在性判块，可重复执行）；结构齐全则本段只留观测 SELECT 与「无差异」注释
3. 第 0 段前置观测：四/五表计数（应 0 行，非 0 先判读）+ 惯例观测（菜单根行 `C_TYPE`+`C_MODNUMB`+`C_SYSTEM` 形态、现有『新增』按钮行、现有字段行、C_AREA 取值、菜单行 C_ICON 取值惯例）
4. 菜单树注册（第 1-2 段）：目录行 + 页面行，幂等 MERGE（C_URL 判重；子行 N_PARKEYID 标量子查询取父行 ID）
5. 接口登记（第 3 段）+ 按钮登记（第 4 段）+ 字段资源（第 5 段）：判重键 N_PARKEYID+C_NAME（按钮）/ N_PARKEYID+C_PROP+C_AREA（字段）
6. 放行说明段（第 6 段，**无 SQL**）：注释写明放行走权限系统 UI 真实角色绑定，绑定前 SEC-00021 属预期
7. 验证 SELECT（预期行数写进段头注释，含 AUTH_ROLE_RESOURCE_URL 预期 0 行）+ 回滚段（注释 DELETE，顺序：字段 → 按钮 → 接口 → 菜单）

## 交办流程（生成后）

1. commit push 到 change 所在分支
2. 在对应 issue 评论交办发起人：说明与 DDL 同等待遇、先跑第 -1 段结构观测与第 0 段惯例观测（目录行 C_TYPE、C_SYSTEM、图标体系、按钮惯例列）、执行后把验证 SELECT 输出贴回、再到权限系统 UI 绑定菜单+接口到测试账号所属角色（即发起人给 Tester 配置 TEST_ROLE 环境变量时填的角色名；agent 无权查 env，交办文字只引用变量名不填具体值）
3. 判读回贴输出：行数与字段值符合预期 → 触发 Tester 回归（前置：UI 角色绑定完成）；不符 → 按实际输出修正 SQL 再来一轮
4. **无注册后回填**：老框架资源定位用 `$route.meta.number`（菜单行 ID）自动完成，不需要前端回填动作

## 常见错误

- 生成 ANY `AUTH_ROLE_RESOURCE_URL` 写语句（含 EVERYONE）——业务接口禁用；放行只走 UI 角色绑定，绑定前 SEC-00021 是预期不是故障
- 用 v3 的 lucide 图标映射（老框架是 sunnyfont `baseicon-*` / `el-icon-*` / 本地 svg 名三体系，lucide 前缀在老框架不渲染）
- 按钮图标自行语义匹配或凭观测改写（五个固定操作必须按映射表：新增 baseicon-add / 修改 baseicon-update / 删除 baseicon-del / 导入 baseicon-import / 导出 baseicon-export）
- C_SYSTEM 硬编码猜值（取目标前端 `.env` 的 `VUE_APP_CURRENT_SYSTEM`，以第 0 段现库观测复核）
- `C_SHOW` 写 1 想显示（反了，0 才显示）
- 叶子页 `C_VIEWPATH` 不以 `/` 开头或带 .vue（require 直读，路径错点菜单无响应且无报错弹窗）
- 按钮表单列漏 AUTH_RES_FIELD 行（老框架列表页表单/表格全空）
- 按钮 handle 写进 `C_CALLMETHOD`（正确列 `C_STOREMETHOD`）
- `C_AREA` 写成 searchTabel（老框架一手实证是 `searchTable`）
- 目录行 C_TYPE / C_MODNUMB / 菜单图标凭 v3 惯例硬编码（老库形态不同，先观测第 0 段再定）
- 表结构对齐段不幂等（CREATE/ALTER 必须带存在性判断，可重复执行）
- 忘附回滚段 / 验证 SELECT → 发起人无法回贴，断链重演
- 执行 SQL 语句之间或行尾夹注释（受限通道整块执行会断——注释只放段头，段内语句连续平铺）
