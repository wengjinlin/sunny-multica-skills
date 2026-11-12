# 权限资源表结构沉淀（四表模型）

> 字段语义以平台 jar 反编译 SQL（sunny-auth-client 0.0.21 `LoginMapperOracle.xml`；sunny-base-module 0.0.54 `AuthResourceServiceImpl`/`AuthResButtonMapperOracle.xml`）与前端源码（`sunny-ecq-web/src/router/routes/utils.ts`、`access.ts`、`guard.ts`、querylist 页面 `toolbarButtonClick`）消费链为准，`docs/db/auth.md` 字典佐证；个别取值以现库实际行为准（见各表「执行前核对」）。
> dev 库地址以环境配置为准——agent 永不直连，仅发起人人工执行。

## 表一：AUTH_RES_MENU 资源菜单表（菜单树）

菜单树表，驱动前端路由与菜单栏。权威字段（前端 utils.ts 消费印证）：

| 字段 | 语义 | 填值规范 |
|---|---|---|
| ID | 主键 | insert 省略（identity；报错回贴修正） |
| C_MODNUMB | 模块编号 | 现库惯例 UUID 形态（test 样例 `f4e45e1f-c6a8-454e-aaed-fd187a2c8e7d`），SQL 用 `SYS_GUID()` 格式化生成（USING 子句只调一次）；注册后回填前端 resourceConfig.cModnumb |
| C_MODNAME | 模块名称 | 菜单显示名（前端 meta.title），如 `物料入库` |
| C_MODDESC | 模块描述 | 可同 C_MODNAME |
| N_PARKEYID | 父级 ID | 0=根（一级目录即权限目录，未指明时新建一级目录一律挂 0）；子行挂父行 ID（SQL 用标量子查询取） |
| C_TYPE | 类型 | `1`菜单 `4`超链接 `5`弹窗 `6`iframe `-1`everyone 资源（-1 不进菜单树，属基础框架机制，业务模块不用） |
| C_URL | URL 路径 | 菜单行=前端路由（如 `/ckgl/rk`） |
| C_VIEWPATH | 页面路径 | 一级目录 `'Layout'`；二级目录 `'Second'`；叶子=views 相对路径 `/ckgl/RkQuery`（前端 `import.meta.glob('views/**/*.vue')` 直读，漏目录即白屏告警） |
| C_VIEWNAME | 页面 name | =组件 `defineOptions` name（keepAlive 唯一），如 `CkglRkQuery`；参照 `DataDictionaryQueryPage` |
| C_SHOW | 菜单栏显示 | **0=显示 1=隐藏（反向！）**，前端 `hideInMenu: cShow === '1'` |
| C_SIGN | 是否有效 | 0=禁用 1=启用，默认启用（写 1） |
| N_ORDER | 排序 | 前端当前未消费（getTreeRoutes 不读），可 0 |
| C_ICON | 图标 | 菜单行 INSERT **显式写列**：lucide 图标体系（`lucide:<icon-name>`），按菜单/页面**语义匹配**选图标（前端 `meta.icon=cIcon` 直读，为空时有按名称 hash 的临时随机图标兜底）；按钮行图标不用语义匹配，用表三固定映射 |
| C_AUTH | 角色权限 | 1=启用 0=不启用（按现有行惯例，默认 1） |
| 其余 | C_CRENUMB/D_CREDATE(sysdate)/C_SYSTEM('ECQ')/N_LEVEL/C_META/TS/C_ADRES_CLASS/N_SENSITIVE | 按现有行；C_SYSTEM 固定 'ECQ' |

## 表二：AUTH_MODULE_URL 菜单URL表（后端接口登记）

表示「菜单有哪些 url 接口」。jar 实证两条 SQL：`checkModuleURLExist: select id,N_MODULEID,C_TYPE from AUTH_MODULE_URL where c_url=?`；`insertAuthRoleResourceUrl: insert into AUTH_ROLE_RESOURCE_URL(n_roleid,n_resourceid,n_modurlid,C_ROLENUMB,c_url,c_system) select b.N_DEFROLEID,b.id,a.id,c.C_ROLENUMB,a.c_url,b.c_system from auth_module_url a, auth_res_menu b, auth_role c where a.n_moduleid=b.id and b.N_DEFROLEID=c.id and a.id=?`

| 字段 | 语义 | 填值规范 |
|---|---|---|
| ID | 主键 | insert 省略 |
| N_MODULEID | 所属菜单行 ID | 标量子查询 `(SELECT ID FROM AUTH_RES_MENU WHERE C_URL='/ckgl/rk')` |
| C_URL | 后端接口 URL | `/ckgl/rk/selectForPage`、`/ckgl/rk/insert` |
| C_TYPE | 类型 | `1`菜单接口 `2`按钮接口 `-1`系统通用/everyone |
| C_DESC | 接口描述 | 中文，如 `物料入库-分页查询` |
| C_CRENUMB / D_CREDATE(sysdate) / TS / N_CLICKNUM(0) | 公共列 | 省略/默认 |

## 表三：AUTH_RES_BUTTON 资源按钮表（按钮登记）

查询列表页（querylist）的工具栏按钮登记在此表；与 AUTH_MODULE_URL 的 C_TYPE=2 接口行分工并存：接口行管鉴权 URL，按钮行管工具栏渲染。

字段（平台实体 `AuthResButton` + `AuthResButtonMapperOracle.xml` 实证）：ID、C_NAME 按钮名称、N_PARKEYID→AUTH_RES_MENU 行 ID、C_AREA 区域（查询列表页工具栏，字典枚举 `searchTabel`）、**C_STOREMETHOD 对应 store 的方法（=按钮 code，前端匹配字段）**、C_VALID 是否校验（0:校验 1:不校验）、C_ICON 图标、C_SIGN、N_ORDER、C_AUTH、**C_CALLMETHOD 配置调用后端方法（导出方法配置/导入后台接口）**、C_CLASS、C_TEMPLATETYPE、C_SYSTEM、N_I18NDATA、C_SUB_AREA。

**code 列 = C_STOREMETHOD（实证链）**：平台接口 `POST /core/authResource/queryAreaResource`（按 `N_PARKEYID` + `C_AREA` 调 `findModAreaButton`）返回 `resButtonList`；前端 `useList` 拿到后构造工具栏按钮，`toolbarButtonClick(params)` 里 `params.button.code` 的值即来自 `cStoremethod`（页面代码 `=== 'add'` 分发，见 `views/ckgl/RkQuery.vue`）。`C_CALLMETHOD` 与匹配无关，是按钮点击后调后端方法的配置（导出/导入类按钮用），一般新增/修改按钮留空。

前端消费链：`useList(resourceConfig)` → 平台包按 `nResourceid`/`cModnumb` 拉 `queryAreaResource` → `resButtonList` 渲染工具栏 → `toolbarButtonClick(params)` 按 `params.button.code === 'add'` 分发。

**按钮 code 取值**：新增 = `add`（前端代码实证）。修改/启用/禁用/导入/导出的枚举值无本地代码实证——生成时按第 0 段观测现库同类按钮行对齐，无参照则列封闭式问题问发起人，不猜。

**按钮 C_ICON 固定映射（硬规范，不做语义匹配）**：

| 操作 | 图标 |
|---|---|
| 新增 | `lucide:copy-plus` |
| 修改 | `lucide:pencil-sparkles` |
| 启用 | `lucide:power` |
| 禁用 | `lucide:power-off` |
| 导入 | `lucide:folder-up` |
| 导出 | `lucide:folder-down` |

**执行前核对（走 auth-resource.sql 第 0 段观测，按现库实际值修正模板）**：

- `C_AREA` 取值以 `SELECT DISTINCT C_AREA` 实际输出为准（字典列注释枚举 `searchTabel`；模板按 `searchTable` 写，不符则替换）。
- 按钮 code 列已实证写 `C_STOREMETHOD`；第 0 段现有『新增』按钮行观测用于核对现库一致并补齐惯例列（C_VALID/C_CLASS 等）。

填值惯例：C_NAME='新增'、N_PARKEYID=页面菜单行 ID、C_AREA='searchTable'（待核对）、C_STOREMETHOD='add'、C_ICON='lucide:copy-plus'（固定映射）、C_SIGN='1'、N_ORDER=0、C_AUTH='1'、C_SYSTEM='ECQ'；未实证列（C_VALID/C_CLASS/C_TEMPLATETYPE）留空，现有『新增』行有非空惯例值则对齐补齐。

## 表四：AUTH_ROLE_RESOURCE_URL 角色资源url表(用于缓存)——业务模块永不直写

jar 实证：`getAPIRole: select distinct c_rolenumb from auth_role_resource_url where c_url=? and c_system=?`（`sunny-auth` 鉴权链最终判此处）。

**业务模块接口默认不加 EVERYONE——EVERYONE 只用于基础框架接口。** 本技能生成物**永不包含**任何 `AUTH_ROLE_RESOURCE_URL` 写语句（含 EVERYONE）。业务接口放行方式：在权限系统 UI 给真实角色绑定菜单+接口（人工操作），绑定后由平台生成缓存行。角色绑定前调用接口报 SEC-00021 属预期，不是注册 SQL 的问题。

| 字段 | 说明 |
|---|---|
| ID / N_ROLEID / N_RESOURCEID / N_MODURLID / D_CREDATE / C_ROLENUMB / C_URL / C_SYSTEM | 全部**不由本技能产物写入**；仅作判读知识：鉴权读 c_rolenumb+c_url+c_system |

## 安全与竞态注意

- EVERYONE 资源对**未携带 token 的请求也放行**（框架语义）——正因如此业务接口禁用 EVERYONE，放行只走 UI 真实角色绑定。
- UI 绑定角色后插入缓存行有秒级窗口个别请求仍 SEC-00021——redis `ECQ:URL_ROLENUMB` hash 兜底回填竞态，等 1 分钟重试，勿重复操作。
