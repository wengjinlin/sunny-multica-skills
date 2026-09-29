# KunkkaUxGrid / KunkkaYjyGrid 查询表格

> 查询列表页的表格主体：内嵌搜索表单（KunkkaForm）+ 工具栏按钮 + ux-grid（umy-ui 虚拟滚动表格）+ 分页，`api + fetchSetting` 驱动取数。**查询列表页不直接手写它**——`list` mixin 拼好 `tableAttrs` 后 `v-bind` 上去；本组件 API 用于理解配置项与定制。`KunkkaYjyGrid` 是业务皮肤版（白色圆角容器 + 默认标题，`showTableSetting` 默认关）。

> 来源库：`sunnygroup-components`（全局注册，标签 `<kunkka-ux-grid>` / `<kunkka-yjy-grid>`）｜ API 提取自 `E:\kunkka组件库\kunkka\packages\components\llms-full.txt`（源码核对，2026-09-10）｜ 底层 umy-ui `ux-grid`（类名 `elx-*`，**不是 vxe-table 本身**；弹窗内明细表格用的 vxe 封装是另一个组件 [CommonTable.md](CommonTable.md)）

## 1. 何时使用

- 查询列表页主体（搜索栏 + 表格 + 分页 + 工具栏）——经由 `list` mixin + 资源
- 需要独立拼一块「搜索 + 表格」区域（无资源时的自定义场景）

不适用：

- 弹窗内明细表格（可编辑 / 整表校验） → [CommonTable.md](CommonTable.md)
- 纯静态小表格 → `el-table` / CommonTable

## 2. 导入

全局注册，模板直接写 `<kunkka-ux-grid>`。**ref 固定命名 `kunkka-ux-grid`**（mixin 的 `redoHeight()`、TableSetting 都按这个名字找实例）。

## 3. 代码演示

### 3.1 查询列表页（资源驱动，唯一常规用法）

```vue
<kunkka-ux-grid
  ref="kunkka-ux-grid"
  v-bind="programItem.tableAttrs"
  :form-events="formEvents"
  @selection-change="toggleSelectRow"
  @toggleToolbarClick="toggleToolbarClick"
  @row-dblclick="toggleDblclickRow"
  @inputSearchClick="inputSearchClick"
/>
```

`tableAttrs` 全部由 `list` mixin 生成（见 [query-list.md §4](../page-patterns/query-list.md)），默认结构：

```javascript
{
  name: 'programItem',
  useSearchForm: true,            // 内嵌搜索表单
  formConfig: { lg: 4, showAdvancedButton: true, form: [...], model: {} },
  columns: [...],                  // 含 checkbox 首列 / 操作列
  toolbar: [...],                  // 工具栏按钮（含 handle）
  exportBtns: [...],               // daochu/show 按钮
  pagination: { pageSize: 100, pageSizes: [100,200,300,500], ... },
  model: [],                       // 表格数据
  isCanResizeParent: true,
  resizeHeightOffset: 13,
  api: async () => this.$store.dispatch('programItem/queryList')
}
```

### 3.2 手写最小查询表格（无资源场景）

```vue
<kunkka-ux-grid
  ref="kunkka-ux-grid"
  :use-search-form="true"
  :form-config="{ form: [{ label: '名称', prop: 'cName', components: 'Input' }], model: {} }"
  :columns="[
    { type: 'checkbox', width: 40 },
    { field: 'cName', title: '名称' }
  ]"
  :api="queryApi"
  :pagination="true"
/>
```

```javascript
methods: {
  async queryApi({ pageNo, pageSize, form }) {
    const res = await selectForPage({ pageNo, pageSize, entity: form })
    return { records: res.result.records, total: res.result.total }  // 按 fetchSetting 取数
  }
},
mounted() {
  this.$refs['kunkka-ux-grid'].fetch()   // immediate 不生效，手动触发首查
}
```

## 4. API

### 4.1 Props（常用）

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `api` | `Function \| Promise` | - | 取数函数（queryList 模式下 = dispatch store action） |
| `fetchSetting` | `Object` | `{pageField:'pageNo', sizeField:'pageSize', listField:'records', totalField:'total'}` | 请求 / 响应字段映射（路径支持 `a.b.c`） |
| `useSearchForm` | `boolean` | `false` | 内嵌搜索表单 |
| `formConfig` | `Object` | `{}` | 搜索表单配置（透传 KunkkaForm props + `form` / `model`） |
| `formEvents` | `Object` | `{}` | 搜索表单字段事件（透传 KunkkaForm `events`） |
| `pagination` | `Object \| false` | `true` | 分页配置（`false` 关闭） |
| `toolbar` | `Array` | `[]` | 工具栏按钮（`label` / `handle` / `icon`） |
| `immediate` | `boolean` | `false` | **保留字段，不生效**——首查需手动 `fetch()` 或走 mixin |
| `isCanResizeParent` | `boolean` | `false` | 随父容器自适应高 |
| `resizeHeightOffset` | `number` | `0` | 高度补偿 |
| `loading` | `boolean` | `false` | 加载态 |
| `showTableToolbar` | `boolean` | `true` | 工具栏区域 |
| `resourceId` | `string` | `''` | 资源 id（TableSetting 显示方案用；缺省取 `$route.meta.number`） |

> `columns` / `editConfig` / `size` / `showOverflow` 等经 `$attrs` 透传 umy-ui ux-grid；**传了 `editConfig` 即整表可编辑**（此时 model watcher 不自动 reloadData）。

### 4.2 Events

| Event | Parameters | Description |
|-------|------------|-------------|
| `toggleToolbarClick` | `(data \| {item, scope})` | 工具栏 / 操作列按钮点击（store action 派发**之后** emit，页面在这开弹窗） |
| `fetch-success` | `({items, total})` | 取数成功 |
| `fetch-error` | `(error)` | 取数失败 |
| `inputSearchClick` | `(item, event)` | 搜索栏放大镜字段 |
| `currentChange` / `sizeChange` | 页码 / 页距 | 仅未配 `api` 时发出 |
| ux-grid 透传 | - | `selection-change` / `row-click` / `row-dblclick` / `radio-change` / `sort-change` 等 |

### 4.3 Methods（`this.$refs['kunkka-ux-grid']`）

| Method | Description |
|--------|-------------|
| `fetch({currentPage?, pageSize?})` | 手动查询（可指定页） |
| `reloadData(data)` | 直接灌数据（本地数据模式） |
| `redoHeight()` | 重算高度（容器尺寸变化后调） |
| `setTableProps(props)` | 运行期合并 props |
| ux-grid 原生 | 经内部 `$refs['kunkka-ux-grid']` 可达（`getTableColumn` / `loadColumn` / `toggleRowSelection` …） |

### 4.4 Slots

| Slot | Description |
|------|-------------|
| `toolbar` / `toolbarBtn` | 工具栏自定义区 |
| `form-<prop>` | 搜索表单自定义字段（透传 KunkkaForm） |
| 列单元格 | `columns[].slots.default`（操作列 JSX 见 query-list §3.3） |

## 6. 注意事项 / FAQ

- **`immediate` 是保留字段不生效**：首查由 `list` mixin `dispatch(`${name}/queryList`)` 触发；手写场景 `mounted` 里 `fetch()`。
- **ref 名固定 `kunkka-ux-grid`**：改名后 `redoHeight()`（mixin finally 里）与 TableSetting 静默失效——高度不对 / 显示设置报错先查这个。
- **工具栏按钮两级分发**：点击 → `vaild()` → `$store.dispatch(item.handle)`（有则先走 action）→ `emit('toggleToolbarClick')`。按钮项带 `handle` 时才 dispatch；`handle` 为空 = 点了没反应（资源 `cStoremethod` 必须回填）。
- **搜索表单提交永远回第 1 页**；跨页勾选依赖 checkbox reserve（默认未开，批量操作按当前页理解）。
- **YjyGrid 与 UxGrid** props / events 一致，差异仅默认皮肤与 `showTableSetting`（ux 默认 true / yjy 默认 false）；查询列表页用 UxGrid（mixin 默认）。
- **表格数据在 `tableAttrs.model`**（store 里），不是组件私有 state。

## 7. 关联资源

- **相关组件**：[KunkkaForm.md](KunkkaForm.md)（内嵌搜索表单）、`KunkkaTableSetting`（列显示设置，资源 `cTemplatetype='0'` 自动启用）、[CommonTable.md](CommonTable.md)（弹窗明细表格，注意区分）
- **标准模板**：[query-list](../page-patterns/query-list.md)
- **组件库参考**：`E:\kunkka组件库\kunkka\app\views\kunkka\`（ux-grid / yjy-grid demo + docs）
- **真实代码**：[src/template/queryListTemplate.vue](../../../../../src/template/queryListTemplate.vue)、[src/mixins/list.js](../../../../../src/mixins/list.js)（tableAttrs 全部默认值）
