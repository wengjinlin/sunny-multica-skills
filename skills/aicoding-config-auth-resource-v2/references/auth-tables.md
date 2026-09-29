# 权限资源表结构沉淀（Vue2 老框架，四表 + 字段表）

> 字段语义以 Vue2 老框架前端（vue-admin-template 系）源码消费链为准：`src/store/modules/permission.js`（getTreeRoutes 菜单树）、`src/permission.js`（路由守卫）、`src/mixins/list.js`（列表页资源装配）、`src/mixins/configurationFile/utils.js`（initButtonItem/initFormItem/initTableColumn）、`src/layout/components/Sidebar/Item.vue`（图标渲染）、`src/icons/`（svg 体系）。后端为同款权限平台（四表模型与 v3 技能所述同构），列结构以平台同构库活库导出为权威（见各表「列结构」节，兼作 auth-resource.sql 表结构对齐段比对基准）。
> dev 库地址以环境配置为准——agent 永不直连，仅发起人人工执行。

## 表一：AUTH_RES_MENU 资源菜单表（菜单树）

菜单树表，驱动前端路由与菜单栏。权威字段（getTreeRoutes 消费印证）：

| 字段 | 语义 | 填值规范 |
|---|---|---|
| ID | 主键 | insert 省略（identity；报错回贴修正）；行 ID 即前端 `$route.meta.number`，list mixin 按它拉按钮/字段资源 |
| C_MODNUMB | 模块编号 | **老库存在短代码形态**（代码实证：`cModnumb === 'XTGL'` 特判挂资源管理路由）；新行取值以现库同类行观测对齐，不预设 UUID 形态 |
| C_MODNAME | 模块名称 | 菜单显示名（meta.title），如 `样品台账` |
| C_MODDESC | 模块描述 | 可同 C_MODNAME |
| N_PARKEYID | 父级 ID | 0=根（一级目录挂 0）；子行挂父行 ID（SQL 用标量子查询取） |
| C_TYPE | 类型 | `1`菜单 `4`超链接 `5`弹窗 `6`iframe `-1`everyone 资源；**菜单树查询传 types [0,1,4]，0 疑为目录形态——一级目录行 C_TYPE 实际值以第 0 段观测现库根行为准（`SELECT ID,C_TYPE,C_VIEWPATH,C_URL,C_MODNUMB,C_SYSTEM FROM AUTH_RES_MENU WHERE N_PARKEYID=0`），观测后全模块统一** |
| C_URL | URL 路径 | 菜单行=前端路由（如 `/sampleManagement/sampleLedger`） |
| C_VIEWPATH | 页面路径 | 一级目录 `'Layout'`；二级目录 `'Second'`；叶子=views 相对路径 **以 `/` 开头且不含 .vue**（`require(`@/views${C_VIEWPATH}.vue`)` 直读；路径错 require 抛错被 catch 吞，点菜单无响应） |
| C_VIEWNAME | 页面 name | =组件 `name`（keepAlive 唯一），如 `CompanyConfigurationQuery`；另被 `queryAllThirdMenu` 三级菜单缓存链消费 |
| C_SHOW | 菜单栏显示 | **0=显示 1=隐藏（反向！）**，前端 `hidden: cShow === '1'` |
| C_SIGN | 是否有效 | 0=禁用 1=启用，默认启用（写 1） |
| C_NEXTLEVEL | 是否有下级 | 0:没有 1:有，按层级写 |
| N_ORDER | 排序 | 可 0 |
| C_ICON | 图标 | 三体系（Item.vue 实证）：值含 `baseicon-`/`el-icon-`/`iconfont` → `<i class>` 字体图标直用；否则 = 本地 svg 文件名（`src/icons/svg/` 26 个：ai/aizhoushu/computer/dashboard/example/form/keyboard/link/mobile/nested/password/setting/table/tree/user…）。**无 lucide**。按现库同类行观测对齐，无把握留空 |
| C_TEMPLATETYPE | 模板类型 | `0`=上下结构查询页（list mixin 读 `resMenu.cTemplatetype==='0'` 开启显示设置）——查询列表页菜单行写 0 |
| C_AUTH | 角色权限 | 1=启用 0=不启用，默认 1 |
| 其余 | C_CRENUMB/D_CREDATE(sysdate)/C_SYSTEM/N_LEVEL/C_META/TS/N_SEARCHFORMLG/N_DEFROLEID/C_ADRES_CLASS/N_SENSITIVE | 按现有行；**C_SYSTEM = 目标系统标识**：取目标前端 `.env` 的 `VUE_APP_CURRENT_SYSTEM` 值（各仓库不同，**不硬编码**；以第 0 段现库现有行观测复核） |

### 列结构（表结构对齐段比对基准，源=平台同构库活库导出）

ID NUMBER PK；C_MODNUMB VARCHAR2(200)；C_MODNAME VARCHAR2(200)；C_MODDESC VARCHAR2(200)；N_PARKEYID NUMBER；C_TYPE VARCHAR2(200)；C_CRENUMB VARCHAR2(100)；D_CREDATE DATE default sysdate；C_URL VARCHAR2(300)；C_VIEWPATH VARCHAR2(200)；C_VIEWNAME VARCHAR2(200)；C_SHOW VARCHAR2(50)；C_SIGN VARCHAR2(50)；C_NEXTLEVEL VARCHAR2(50)；N_ORDER NUMBER；C_ICON VARCHAR2(100)；N_SEARCHFORMLG NUMBER；C_TEMPLATETYPE VARCHAR2(50)；C_SYSTEM VARCHAR2(100)；N_LEVEL NUMBER；N_DEFROLEID NUMBER；C_META VARCHAR2(1000)；TS DATE；C_AUTH VARCHAR2(50)；C_ADRES_CLASS VARCHAR2(100)；N_SENSITIVE NUMBER。主键 PK_AUTH_RES_MENU(ID)；索引 IDX_AUTH_RES_MENU(C_MODNUMB)；无唯一索引；无外键。

## 表二：AUTH_MODULE_URL 菜单URL表（后端接口登记）

表示「菜单有哪些 url 接口」，每 API 一行（后端权限平台与 v3 技能所述同构：checkModuleURLExist / insertAuthRoleResourceUrl）。

| 字段 | 语义 | 填值规范 |
|---|---|---|
| ID | 主键 | insert 省略 |
| N_MODULEID | 所属菜单行 ID | 标量子查询 `(SELECT ID FROM AUTH_RES_MENU WHERE C_URL='/xxx/yyy')` |
| C_URL | 后端接口 URL | 如 `/sampleLedger/selectForPage`、`/sampleLedger/insert`（拼法=Controller 映射+方法名，以 design.md 接口清单为准） |
| C_TYPE | 类型 | `1`菜单接口 `2`按钮接口 `-1`系统通用/everyone |
| C_DESC | 接口描述 | 中文 |
| 其余 | C_CRENUMB / D_CREDATE(sysdate) / TS / N_CLICKNUM(0) | 省略/默认 |

### 列结构

ID NUMBER PK；N_MODULEID NUMBER；C_URL VARCHAR2(300)；C_CRENUMB VARCHAR2(100)；D_CREDATE DATE default sysdate；C_TYPE VARCHAR2(50)；TS DATE；C_DESC VARCHAR2(100)；N_CLICKNUM NUMBER default 0。主键 PK_AUTH_MODULE_URL(ID)；索引 IDX_AUTH_MODULE_URL(C_URL)；无唯一索引；无外键。

## 表三：AUTH_RES_BUTTON 资源按钮表（按钮登记）

工具栏与操作列按钮登记。消费链（一手实证）：`mixins/list.js` created → `getCurrentUserResourcesByParId({parId: $route.meta.number, types:[2,3]})` → 返回 `resButtonList` → `initButtonItem`（`mixins/configurationFile/utils.js`）构造工具栏，页面按 `bt.handle === 'xxx'` 分发。

**handle 列 = C_STOREMETHOD（initButtonItem 实证：`handle: cStoremethod`）**。handle 实证值：新增 `add`、查询 `search`、重置 `reset`、删除 `del`、导入显示 `daoru/show`、导出显示 `daochu/show`；页面自定义形态多为 `模块/动作`（`material/tab2Add` 等）。新按钮 handle 必须与 design.md 页面代码分发串一致；无实证的先观测现库同类行，无参照列封闭式问题问发起人，**不猜**。

| 字段 | 语义 | 填值规范 |
|---|---|---|
| ID | 主键 | insert 省略 |
| C_NAME | 按钮名称 | 中文，如 `新增`（判重键成员） |
| N_PARKEYID | 页面菜单行 ID | 标量子查询取 |
| C_AREA | 所在区域 | **`searchTable`**（一手代码实证；字典注释拼写 searchTabel 是错的） |
| C_STOREMETHOD | handle（前端分发串） | `add`/`search`/`reset`/`del`/`daochu/show`/`daoru/show`/`模块/动作` |
| C_SUB_AREA | 细分区域 | `columnTable`=操作列（行内）按钮；工具栏按钮不写（list.js 过滤 `!cSubArea`） |
| C_VALID | 是否校验 | 0:校验 1:不校验，按现库同类行 |
| C_ICON | 图标 | **固定映射（硬规范，不做语义匹配、不观测）**：新增 `sunnyfont baseicon-add`；修改 `sunnyfont baseicon-update`；删除 `sunnyfont baseicon-del`；导入 `sunnyfont baseicon-import`；导出 `sunnyfont baseicon-export`。映射表之外的操作按现库同类行观测对齐 |
| C_CLASS | 按钮 class | 观测对齐 |
| C_SIGN / N_ORDER / C_AUTH | 启用/排序/权限 | '1'/0/'1' 默认，观测对齐 |
| C_CALLMETHOD | 调后端方法配置 | 导出方法/导入接口专用，普通按钮留空，**不是 handle 列** |
| 其余 | C_TEMPLATETYPE / C_SYSTEM（目标系统标识，同表一规则） / N_I18NDATA(0) / TS / D_CREDATE(sysdate) / C_CRENUMB | 按现有行 |

### 列结构

ID NUMBER PK；C_NAME VARCHAR2(200)；N_PARKEYID NUMBER；C_CRENUMB VARCHAR2(100)；D_CREDATE DATE default sysdate；C_AREA VARCHAR2(200)；C_STOREMETHOD VARCHAR2(200)；C_VALID VARCHAR2(50)；C_ICON VARCHAR2(100)；C_SIGN VARCHAR2(50)；N_ORDER NUMBER；C_AUTH VARCHAR2(50)；C_CALLMETHOD VARCHAR2(2000)；C_CLASS VARCHAR2(200)；C_TEMPLATETYPE VARCHAR2(50)；C_SYSTEM VARCHAR2(100)；TS DATE；N_I18NDATA NUMBER default 0；C_SUB_AREA VARCHAR2(200)。主键 PK_AUTH_RES_BUTTON(ID)；无索引；无外键。

## 表四：AUTH_RES_FIELD 资源字段表（老框架列表页必需）

**老框架特有消费**：`mixins/list.js`（列表页标配）把 `resFieldList` 按 C_AREA 分流——`searchForm` → `initFormItem` 查询表单项；`searchTable` → `initTableColumn` 表格列。**无字段行 = 表单与表格全空**，新列表页必须生成。

| 字段 | 语义 | 填值规范 |
|---|---|---|
| ID | 主键 | insert 省略 |
| C_LABEL | 字段中文名 | 表单 label / 表格 title |
| N_PARKEYID | 页面菜单行 ID | 标量子查询取 |
| C_AREA | 所在区域 | `searchForm`（查询表单）/ `searchTable`（表格列） |
| C_FIELDTYPE | 组件类型 | Input/Select/date/datetime/year/Cascader/spanselect/Index/InputSearch（initFormItem/initTableColumn switch 实证）；与 design.md 字段清单一致 |
| C_PROP | 后端传参 key | 表格 field / 表单 model key，= 后端查询参数名 |
| C_SELTYPE / C_SELVAL | 下拉类型/取值 | 0:数据字典 1:selectOption 2:工厂 3:自定义下拉 4:其它权限——下拉类字段必填，值从 design.md |
| C_SIGN / C_SHOW | 启用/显示 | '1'/'0'（C_SHOW 同菜单反向：0=显示） |
| C_REQUIRED | 校验 | 0:校验 |
| N_ORDER | 排序 | 按清单顺序 |
| C_WIDTH / C_ALIGN / N_LG | 宽度/对齐/栅格 | 可空 |
| C_META | 额外属性 JSON | 可空 |
| 其余 | C_SYSTEM（目标系统标识，同表一规则）/C_TEMPLATETYPE/C_ENTITY_TABLE/C_ENTITY_COL/N_BILL/N_I18NDATA(0)/C_DYNAMIC_*/C_DEF_VAL/C_DIRECTIVES/C_SUB_AREA/TS/D_CREDATE/C_CRENUMB | 按现有行，未实证留空 |

### 列结构

ID NUMBER PK；C_LABEL VARCHAR2(200)；N_PARKEYID NUMBER；C_CRENUMB VARCHAR2(100)；D_CREDATE DATE default sysdate；C_AREA VARCHAR2(100)；C_FIELDTYPE VARCHAR2(100)；C_PROP VARCHAR2(100)；C_SELTYPE VARCHAR2(100)；C_SELVAL VARCHAR2(200)；C_SIGN VARCHAR2(50)；C_SHOW VARCHAR2(50)；N_ORDER NUMBER；C_ALIGN VARCHAR2(50)；C_WIDTH VARCHAR2(50)；C_REQUIRED VARCHAR2(50)；C_STOREMETHOD VARCHAR2(200)；C_PLACEHOLDER VARCHAR2(200)；C_SLOT VARCHAR2(100)；C_TEMPLATETYPE VARCHAR2(100)；C_SYSTEM VARCHAR2(100)；C_META VARCHAR2(1000)；TS DATE；C_ENTITY_TABLE VARCHAR2(200)；C_ENTITY_COL VARCHAR2(200)；N_LG NUMBER；N_BILL NUMBER；N_I18NDATA NUMBER default 0；C_DYNAMIC_RULES VARCHAR2(1000)；C_DYNAMIC_SHOW VARCHAR2(1000)；C_DEF_VAL VARCHAR2(500)；C_DIRECTIVES VARCHAR2(500)；C_SUB_AREA VARCHAR2(200)；C_DYNAMIC_DISABLED VARCHAR2(1000)。主键 PK_AUTH_RES_FIELD(ID)；索引 IDX_AUTH_RES_FIELD(N_PARKEYID)；无唯一索引；无外键。

## 表五：AUTH_ROLE_RESOURCE_URL 角色资源url表(用于缓存)——业务模块永不直写

（后端同构，与 v3 同判）鉴权链最终判此处（getAPIRole 读 c_rolenumb+c_url+c_system）。**业务模块接口默认不加 EVERYONE——EVERYONE 只用于基础框架接口。** 本技能生成物**永不包含**任何 `AUTH_ROLE_RESOURCE_URL` 写语句（含 EVERYONE）。业务接口放行方式：在权限系统 UI 给真实角色绑定菜单+接口（人工操作），绑定后由平台生成缓存行。角色绑定前调用接口报 SEC-00021 属预期，不是注册 SQL 的问题。

| 字段 | 说明 |
|---|---|
| ID / N_ROLEID / N_RESOURCEID / N_MODURLID / D_CREDATE / C_ROLENUMB / C_URL / C_SYSTEM | 全部**不由本技能产物写入**；仅作判读知识：鉴权读 c_rolenumb+c_url+c_system |

### 列结构

ID NUMBER PK；N_ROLEID NUMBER；N_RESOURCEID NUMBER；N_MODURLID NUMBER；D_CREDATE DATE default sysdate；C_ROLENUMB VARCHAR2(200)；C_URL VARCHAR2(300)；C_SYSTEM VARCHAR2(100)。主键 PK_AUTH_ROLE_RESOURCE_URL(ID)；无索引；无外键。

## 安全与竞态注意

- EVERYONE 资源对**未携带 token 的请求也放行**（框架语义）——正因如此业务接口禁用 EVERYONE，放行只走 UI 真实角色绑定。
- UI 绑定角色后插入缓存行有秒级窗口个别请求仍 SEC-00021——缓存回填竞态，等 1 分钟重试，勿重复操作。
- 表结构对齐段的 ALTER 只允许 ADD COLUMN——**禁止 MODIFY/RENAME/DROP 既有列**（既有列变更属数据迁移，超出本技能范围，需单独 change）。
