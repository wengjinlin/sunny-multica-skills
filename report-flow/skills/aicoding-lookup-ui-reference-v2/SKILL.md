---
name: aicoding-lookup-ui-reference-v2
description: kunkka / sunnygroup-components + 资源驱动 前端 UI 选型速查手册：官方代码生成器模板（src/template/ 的 queryList / formDialog / formTableDialog / formTabsDialog + list / formModal 等 mixin）、成套模块（导入 importDialog、导出 exportDialog）、框架组件（KunkkaForm / KunkkaModal / KunkkaSearchDialog / KunkkaCustomizeSelect / KunkkaUxGrid / CommonTable / MulSearchDialog / CommonFileUpload），Element UI 仅为最后兜底；只输出查阅结论，不生成业务代码。TRIGGER——写或评审任何 Vue 页面 / 弹窗 / 表单 / 表格 / 选择器 / 导入导出之前，或用户问「该用哪个组件」「有没有现成的」「参考哪个模式」「怎么写查询页 / 弹窗」，或排错定位（弹窗关不掉、校验不生效、按钮点击无反应、表格空白、回显异常）时使用本技能，即使没点名要「查选型」。
license: MIT
metadata:
  author: sunnygroup-components 资源驱动前端框架
  version: '1.1'
---

# 组件与模式选型参考

本技能是**框架前端 UI 的速查手册**：把官方代码生成器模板、成套模块（导入 / 导出）、框架组件沉淀成参考表，随时查阅「有没有现成方案」「该用哪个组件」「这个 bug 是不是用法错了」。只输出查阅结论，**不生成业务代码、不写文件**。

## 输入

`$ARGUMENTS` = 可选，用户的需求描述（如「查询列表」「表单弹窗」「一个下拉选择」「上传」）。未提供时直接按「快速定位」表给出候选并追问一句聚焦点，不要空转等待。

---

## 核心心智模型：资源驱动（先读懂这条再看选型）

本框架是**资源 / 配置驱动**的低代码体系：页面不写死搜索表单、表格列、工具栏按钮——全部由后端「资源管理」按模块配置下发，前端用框架组件渲染。

- 页面 / 弹窗创建时用 `$route.meta.number`（= 资源 id）或 `modnumb`（模块编号）调 `getCurrentUserResourcesByParId`，拿到 `resFieldList` / `resButtonList` / `resColumnList` 后经 [src/mixins/configurationFile/utils.js](../../../src/mixins/configurationFile/utils.js) 的 `initFormItem / initTableColumn / initButtonItem` 拼成 `tableAttrs` / `formModalAttrs`，`v-bind` 给 kunkka 组件。
- 字段区域 `cArea`：`searchForm`（搜索栏）/ `searchTable`（表格列与工具栏按钮）/ `form`（弹窗表单）/ `table`（弹窗明细表格列）；按钮细分 `cSubArea`：`columnTable`（行操作列）/ `insertFooter` / `centerFooter` / `appendFooter` / `footer`（弹窗底栏位置）。
- 控件类型由字段 `cFieldtype` 决定（Input / Select / InputSearch / CustomizeSelect / date / daterange / Slot …），下拉来源由 `cSeltype` 决定（0 数据字典 / 1 前端枚举 / 2 工厂（取 `store.getters.gc`，默认 store 未注册该 getter——配置前先确认已注册，否则取不到数据） / 3 自定义下拉 cNum / 4 其他权限）。
- **按钮的 `handle`（= cStoremethod，如 `programItem/add`、`daoru/show`、`daochu/show`）就是 Vuex action 路径**：kunkka-ux-grid 工具栏点击先 `$store.dispatch(item.handle)`，再 `$emit('toggleToolbarClick')` 给页面拦截开弹窗。

**写一个页面的套路 = 后端配资源 → 复制 `src/template/` 官方模板 → 改 `name` / `modnumb` / api。**

---

## 快速定位（任务 → 直接读哪一份）

| 用户要做的事 | 直接读 |
| ------------ | ------ |
| 查询列表页（搜索栏 + 表格 + 分页 + 工具栏） | [`references/page-patterns/query-list.md`](references/page-patterns/query-list.md) |
| 新增 / 编辑弹窗（表单） | [`references/modules/form-modal.md`](references/modules/form-modal.md) |
| 弹窗内「表单 + 明细表格」一次提交 | [`references/modules/table-modal.md`](references/modules/table-modal.md) |
| 工具栏导入 Excel | [`references/modules/import.md`](references/modules/import.md) |
| 工具栏导出 Excel | [`references/modules/export.md`](references/modules/export.md) |
| 弹窗选择业务实体（选物料 / 客户 / 司机…） | [`references/components/KunkkaSearchDialog.md`](references/components/KunkkaSearchDialog.md)（多选带已选栏看 [MulSearchDialog.md](references/components/MulSearchDialog.md)） |
| 下拉选项（字典 / 远程 / 级联联动） | [`references/components/KunkkaCustomizeSelect.md`](references/components/KunkkaCustomizeSelect.md) |
| 任何表单（字段联动 / 放大镜字段 / 动态校验） | [`references/components/KunkkaForm.md`](references/components/KunkkaForm.md) |
| 弹窗外壳 / 底部按钮 / 提交 loading | [`references/components/KunkkaModal.md`](references/components/KunkkaModal.md) |
| 弹窗内可编辑明细表格 | [`references/components/CommonTable.md`](references/components/CommonTable.md) |
| 页面级查询表格（api + 分页 + 搜索） | [`references/components/KunkkaUxGrid.md`](references/components/KunkkaUxGrid.md) |
| 表单 / 表格里传附件（上传） | [`references/components/CommonFileUpload.md`](references/components/CommonFileUpload.md) |
| 以上都不是的基础组件（Input / Tag / Tree / Tabs …） | 走下方第 3 层 Element UI 兜底流程 |

---

## 选型决策（三层，自上而下，命中即停）

```
第 1 层 官方模板 + mixin（src/template/，资源驱动成套方案） → 第 2 层 框架组件（kunkka-* / 全局业务组件） → 第 3 层 Element UI 原生
```

为什么分层：官方模板 + mixin 内置了资源加载、表单 / 列 / 按钮拼装、分页、查询方案、显示设置、导入导出整套体系，退回组件自拼会脱离这套体系、逐项踩坑；kunkka 组件封装了资源 schema 渲染、Vuex 联动（ggcxtc / zdyxlk / assShowPlan / assSearchplan），Element 原生没有。所以**上层命中就不用下层**。

### 第 1 层 — 官方模板 / 成套模块（命中即用）

**页面 / 弹窗模板**（代码生成器官方模板，位于 [`src/template/`](../../../src/template/)，配套 demo 在 [src/views/demo/querylist/](../../../src/views/demo/querylist/)）：

| 业务场景 | 标准方案 | 文档（按需读） |
| -------- | -------- | -------------- |
| 查询列表页 | `queryListTemplate.vue` + `@/mixins/list` + `vuexTemplate.js` + `apiTemplate.js` | [`references/page-patterns/query-list.md`](references/page-patterns/query-list.md) |
| 表单弹窗（新增 / 编辑） | `formDialogTemplate.vue` + `@/mixins/formModal` | [`references/modules/form-modal.md`](references/modules/form-modal.md) |
| 表单 + 明细表格弹窗 | `formTableDialogTemplate.vue` | [`references/modules/table-modal.md`](references/modules/table-modal.md) |
| 表单 + 多 Tab 明细弹窗 | `formTabsDialogTemplate.vue` + `@/mixins/formTabsModal` | [table-modal.md](references/modules/table-modal.md) §5 变体 |
| Excel 导入 | 全局组件 `<importDialog />` + 资源按钮 `daoru/show`（自包含流程） | [`references/modules/import.md`](references/modules/import.md) |
| Excel 导出 | 全局组件 `<exportDialog />` + 资源按钮 `daochu/show`（自包含流程） | [`references/modules/export.md`](references/modules/export.md) |

> ⚠️ **没有匹配的模板时**：弹窗 = `KunkkaModal` 外壳 + [`references/components/`](references/components/) 里需要的框架组件自行编排；页面同理自行组合。导入 / 导出自包含，直接用。

### 第 2 层 — 框架组件（kunkka-* 与项目全局业务组件）

第 1 层未覆盖时，用这些积木组装。封装了资源 schema 渲染 / Vuex 联动 / 字典转换等业务逻辑，**命中则强制使用，禁止用 Element 对应组件**：

| 业务场景 | 必须使用 | 来源 | API/用法详情（按需读） |
| -------- | -------- | ---- | ---------------------- |
| 表单 | `KunkkaForm`（`<kunkka-form>`） | sunnygroup-components | [`KunkkaForm.md`](references/components/KunkkaForm.md) |
| 弹窗外壳 | `KunkkaModal`（`<kunkka-modal>`） | sunnygroup-components | [`KunkkaModal.md`](references/components/KunkkaModal.md) |
| 业务搜索弹窗 | `KunkkaSearchDialog` / `MulSearchDialog` | 组件库 / 工程内置 | [`KunkkaSearchDialog.md`](references/components/KunkkaSearchDialog.md)、[`MulSearchDialog.md`](references/components/MulSearchDialog.md) |
| 自定义下拉（cNum / 级联） | `KunkkaCustomizeSelect` | sunnygroup-components | [`KunkkaCustomizeSelect.md`](references/components/KunkkaCustomizeSelect.md) |
| 查询表格 | `KunkkaUxGrid` / `KunkkaYjyGrid` | sunnygroup-components | [`KunkkaUxGrid.md`](references/components/KunkkaUxGrid.md) |
| 可编辑明细表格 | `CommonTable`（vxe-table 封装） | 工程全局组件 |[`CommonTable.md`](references/components/CommonTable.md) |
| 上传附件 | `CommonFileUpload` + `FileList` | 工程全局组件 |[`CommonFileUpload.md`](references/components/CommonFileUpload.md) |

> 组件来源两处：**`sunnygroup-components`**（kunkka 组件库，`main.js` 里 `Vue.use` 全局注册，标签 `<kunkka-*>`）；**工程内全局业务组件**（[src/plugins/sunnyoptical.js](../../../src/plugins/sunnyoptical.js) 注册：`CommonTable` / `CommonFileUpload` / `ExportDialog` / `ImportDialog` / `FileList` / `DepartmentChoose` / `I18nDataDialog` 等）。页面代码不直接操作 axios，一律走 `src/api/` 层函数（`request.js` 已统一带 token / 全局报错）。

### 第 3 层 — 基础组件兜底（Element UI 2.15）

上两层都没有的基础组件（`el-input` / `el-select` / `el-date-picker` / `el-tag` / `el-radio` / `el-checkbox` / `el-switch` / `el-tree` / `el-tabs` / `el-steps` / `el-pagination` …）：

1. 先查工程内是否已有包装（`CommonTable` 放表格、指令 `v-number-*` 放数字输入约束，见 [src/directive/index.js](../../../src/directive/index.js)）；
2. 没有 → 查 **Element UI 2.x 官方文档**（https://element.eleme.io/#/zh-CN/component/installation ，或本地 `node_modules/element-ui` 源码 / 类型定义）；
3. 表格类兜底用 **vxe-table 3.6**（项目按需注册于 [src/components/VXE/index.js](../../../src/components/VXE/index.js)）。

> 个别存量工程的 `main.js` 全局注册过 ant-design-vue 1.x（能看到存量页面在用其日历等组件）——**新代码一律用 Element UI**：不新增 antd 组件、不引 antd 样式文件，提示 / 确认框只用 `$message` / `MessageBox.confirm`。

---

## 高频踩坑速查（排错定位）

| 症状 | 原因与解法 | 详见 |
| ---- | ---------- | ---- |
| 弹窗「能打开、关不掉」或开关状态错乱 | `KunkkaModal` 受控必须 `:visible.sync="visible"`（.sync 修饰符）；且框架惯例**不走 props 打开**——父组件 `this.$refs.xxxAdd.onDataReceive({ row })`，子组件自持 `visible` | [KunkkaModal.md](references/components/KunkkaModal.md) |
| 表单校验代码报错 / `validate is not a function` | kunkka-form 内部包一层 el-form，校验要走**双层 ref**：`this.$refs['kunkka-form'].$refs['kunkkaForm'].validate(...)`；弹窗打开后 `clearValidate()` 清残留校验态 | [form-modal.md](references/modules/form-modal.md) |
| 工具栏按钮看得见、点了没反应 | 按钮 `handle` 就是 Vuex action 路径：① 资源管理里按钮 `cStoremethod` 必须非空且 store 模块有同名 action；② 开弹窗类按钮要在页面 `toggleToolbarClick` 里按 `handle` switch 分发 | [query-list.md](references/page-patterns/query-list.md) |
| 新页面表格空白 / 搜索栏没有字段 | 资源没配（页面用 `$route.meta.number` 拉资源）或**页面组件 `name` 与资源管理的 `cViewname` 不一致**（keep-alive 缓存与权限路由都靠它匹配） | [query-list.md](references/page-patterns/query-list.md) |
| 给 kunkka-ux-grid 传 `immediate: true` 不自动查询 | `immediate` 是保留字段、**不生效**；查询由 `list` mixin 在资源加载完成后 `dispatch(`${name}/queryList`)` 触发，刷新也用它 | [KunkkaUxGrid.md](references/components/KunkkaUxGrid.md) |
| 确定按钮连点重复提交 | `@ok` 里先 `this.$refs.registerModal.changeOkLoading(true)`，请求 `.finally(() => changeOkLoading(false))` 成败都复位 | [form-modal.md](references/modules/form-modal.md) |
| 页面弹出重复错误提示 | `request.js` 已全局拦截 `code !== 200` 统一报错（530 自动重登），业务 `catch` 里不要再 `this.$message.error()` | [query-list.md](references/page-patterns/query-list.md) |
| 搜索弹窗选中后数据取不到 / 字段全是 `C_XXX` 大写 | `submitAction(data, fData)` 单选 `data` = 行对象、多选 = 数组，**字段名是后端 SQL 别名（大写下划线）**；「未选中点确定」走 `cleanAction`（不是 submitAction 传空） | [KunkkaSearchDialog.md](references/components/KunkkaSearchDialog.md) |
| 多选搜索弹窗重新打开时已选项丢失 | 用 `MulSearchDialog`，`openInit` 传 `selected`（回显已选）、`singleCol`（去重键）、`selectedCol`（右侧栏显示列） | [MulSearchDialog.md](references/components/MulSearchDialog.md) |
| 级联下拉不联动（选了公司，项目下拉没变） | `CustomizeSelect` 靠 `attrParam` 变化触发重查：在 `events` 里监听上游字段 `change`，改下游字段的 `attrParam`（如 `{ cCompany: val }`） | [KunkkaCustomizeSelect.md](references/components/KunkkaCustomizeSelect.md) |
| 弹窗内明细表格必填没校验 / 校验太弱 | 提交前 `await this.$refs['common-table'].validateTable()`（required 列非空校验）；要行级规则校验用 `handleValidate()`（vxe editRules，错误定位到行列） | [CommonTable.md](references/components/CommonTable.md) |
| 上传选了文件保存后附件丢了 | `CommonFileUpload` 是两段式：选文件只入暂存列表，**必须点「上传附件」**；v-model 是 JSON 字符串，没上传的文件不在值里 | [CommonFileUpload.md](references/components/CommonFileUpload.md) |
| 表格高度异常 / 显示设置（列设置）报错 | kunkka-ux-grid 的 **ref 名固定为 `kunkka-ux-grid`**（TableSetting 与 `redoHeight()` 都按这个名字取实例），不要改成别的 | [KunkkaUxGrid.md](references/components/KunkkaUxGrid.md) |

---

## 查找流程

1. **识别意图** — 做「一块 UI」（页面 / 弹窗 / 字段 / 表格 / 导入导出）、确认选型，还是排错。
2. **定位** — 先查「快速定位」表，命中即得答案与该读的那一份文档；未命中按「选型决策」三层表自上而下推荐；排错先查「高频踩坑速查」。
3. **按需深读** — 只有需要完整 API / 示例代码 / 资源配置项时才读对应 references 文件；普通问题用本文件表内信息即可回答。
4. **只输出查阅结论** — 推荐「用哪个方案 / 哪个组件 / 参考在哪」，不生成业务代码。

## 输出格式

简洁、事实化，每条推荐给出可点击的路径：

```
推荐方案：<模板/模块名>（命中第 1 层）或 推荐组件：<组件名>（来自 sunnygroup-components / 工程内全局组件）
理由：<一句话>
深入查阅：<文件路径>
```

## 规则

- **只读**：不写文件、不生成业务代码、不修改组件库与本仓库源码。
- **资源优先**：字段 / 列 / 按钮由后端资源管理配置下发，**禁止在 `.vue` 里手写死表单 schema、表格列、工具栏按钮**（资源暂未配好做原型时才允许本地兜底，须注明「待迁回资源配置」）。页面 `.vue` 只负责：mixins 引入、`name` / `modnumb`、api 引用、事件分发（`toggleToolbarClick` 等）。
- **选型优先级**：三层自上而下——官方模板 / 成套模块 > 框架组件（命中即强制，禁止 Element 对应组件兜底）> Element UI 原生。上层命中禁止退回下层自己拼。
- **Vue 2 写法**：本框架是 Vue 2.7 + Options API（无 `<script setup>` / 组合式 hooks）；组件交互靠 ref 实例方法 + `.sync`，不写 v-model 多参数绑定等 Vue 3 语法。
- **提示统一 Element**：`$message` / `MessageBox.confirm` / `$code('FCG-xxxxx')` 错误码文案。
- **路径准确**：只引用实际存在的目录/文件；文档内 `src/...` 链接相对技能所在工程的根解析（技能装在哪个工程，就指向哪个工程的源码）。
- **查无匹配**：如实说明，并给兜底建议（Element 基础组件 / 最接近的官方模板），不要编造不存在的组件或模式。
- **组件库权威源**：kunkka 组件库本地源码仓库 `E:\kunkka组件库\kunkka`（`packages/components/llms.txt` / `llms-full.txt` / `llms-semantic.md`，及 demo `app/views/kunkka/`）——只读参考，实装版本以所在工程 `node_modules/sunnygroup-components` 为准；工程内全局业务组件源码在 `src/components/`。
- **自包含参考**：`references/` 下是自包含参考文档——`modules/`（成套业务模块）、`page-patterns/`（页面模板）、`components/`（框架组件 API），按需读对应那份即可。
