# 查询列表页标准模板（query-list）

> 最常见的业务页面：顶部搜索栏 + 工具栏按钮 + 数据表格 + 分页，可选导入 / 导出 / 操作列 / 行双击详情。**全资源驱动**——搜索表单字段、表格列、工具栏按钮、分页都由后端资源管理下发，页面 `.vue` 只剩「引 mixin + 写事件分发」。本模板自包含，照着改 `name` / api 即可生成。

> 模板源文件：[src/template/queryListTemplate.vue](../../../../../src/template/queryListTemplate.vue)（2024.12.10 定稿）｜ 零业务噪声 demo：[src/views/demo/querylist/demoQuery.vue](../../../../../src/views/demo/querylist/demoQuery.vue)（本文即模板精编，自包含）

## ⚠️ 开工前置：资源没配，页面就是空壳（最高频踩坑）

页面一切内容来自资源接口。写页面前先确认后端「资源管理」已配好本模块：

1. **菜单资源**：`cViewpath` 指向本页面（如 `demo/querylist/demoQuery`），`cViewname` = 页面组件 `name`（见下方铁律），资源 id 运行期进 `$route.meta.number`；
2. **字段资源**：`cArea='searchForm'`（搜索栏字段）、`cArea='searchTable'`（表格列）；控件 `cFieldtype`、下拉来源 `cSeltype`、必填 `cRequired`、动态显隐 `cDynamicShow`；
3. **按钮资源**：`cArea='searchTable'` 且无 `cSubArea`（工具栏按钮）、`cSubArea='columnTable'`（行操作列按钮）；**`cStoremethod`（handle）非空**且 store 模块有对应 action。

## 1. 何时使用

- 数据列表展示（分页、多条件查询、高级搜索）
- 批量操作（删除 / 启用禁用）、导入导出、查询方案 / 显示设置（列自定义）

不适用：

- 纯录入无列表 → 只写表单弹窗（[form-modal](../modules/form-modal.md)）
- 主从明细一次提交 → [table-modal](../modules/table-modal.md)
- 独立弹窗选业务实体 → `KunkkaSearchDialog`（[KunkkaSearchDialog.md](../components/KunkkaSearchDialog.md)）

## 2. 文件结构（Query 三件套 + 弹窗兄弟）

```
src/api/<模块>/<name>.js                    # API 函数（selectForPage / delById / insert / update_init / update）
src/store/modules/<模块>/<name>.js          # Vuex 模块（state_init / queryList / del / addSave / updateSave…）
src/views/<模块>/<子模块>/<name>/<name>Query.vue    # 查询页（本模板）
src/views/.../<name>Add.vue / <name>Update.vue / <name>Detail.vue   # 弹窗兄弟（按需，见 form-modal）
```

> 命名铁律：`name` 三处一致——页面 `data().name`（= store 模块名 = `mapGetters` 名）、store 文件名、api 引用；**页面组件 `name`（如 `ProgramItemQuery`）必须与资源管理菜单的 `cViewname` 完全一致**（keep-alive 缓存 + 权限路由匹配都靠它，不一致会出现表格空白 / 缓存串页）。

## 3. 标准实现

### 3.1 API 层 — `src/api/<模块>/<name>.js`

照 [src/template/apiTemplate.js](../../../../../src/template/apiTemplate.js)（`selectForPage` / `delById` 必备，弹窗再加 `insert` / `update_init` / `update`）：

```javascript
import request from '@/utils/request'

// 分页查询
export function selectForPage(data) {
  return request({
    url: '/xxx/xxx/selectForPage',
    method: 'post',
    data
  })
}

// 批量删除
export function delById(data) {
  return request({
    url: '/xxx/xxx/delById',
    method: 'post',
    data    // { idList: [...] }
  })
}
```

### 3.2 Vuex 模块 — `src/store/modules/<模块>/<name>.js`

照 [src/template/vuexTemplate.js](../../../../../src/template/vuexTemplate.js)。**必须 `namespaced: true`**，state 固定三件（`tableAttrs` / `selectRow` / `langList`），`store/index.js` 用 `require.context` 自动注册：

```javascript
import { selectForPage, delById } from '@/api/manHourManagement/programItem'
import { Message, MessageBox } from 'element-ui'

const state = {
  tableAttrs: {},   // list mixin 拼好后塞进来，kunkka-ux-grid v-bind 它
  selectRow: [],    // 勾选行（页面 @selection-change 回填）
  langList: []
}

const actions = {
  // 删除（工具栏按钮 handle='<name>/del' 派发到这）
  del({ dispatch, state }, data) {
    return new Promise(async(resolve) => {
      if (state.selectRow.length === 0) {
        Message({ showClose: true, message: this._vm.$code('FCG-00002'), type: 'error' })
        return resolve({ item: { handle: null } })   // 拦截后续 toggleToolbarClick
      }
      MessageBox.confirm(this._vm.$code('FCG-00004'), this._vm.$code('FCG-00005'), {
        confirmButtonText: this._vm.$code('FCG-00006'),
        cancelButtonText: this._vm.$code('FCG-00007'),
        type: 'warning'
      }).then(() => {
        const jsonStr = { idList: state.selectRow.map(el => el.id) }
        delById(jsonStr).then(res => {
          if (res.code === 200) { dispatch('queryList') }   // 删完刷新
          Message.success({ message: res.message, duration: 3 * 1000 })
          resolve()
        }).catch(() => resolve({ item: { handle: null } }))
      }).catch(() => resolve({ item: { handle: null } }))
    })
  },
  // 查询（分页/搜索栏提交都走这；tableAttrs 里有当前页码页距和表单值）
  queryList({ state }) {
    const jsonStr = {
      pageNo: state.tableAttrs.pagination.currentPage,
      pageSize: state.tableAttrs.pagination.pageSize,
      programItem: state.tableAttrs.formConfig.model   // 实体名按后端约定
    }
    return selectForPage(jsonStr).then(res => {
      state.tableAttrs.model = res.result.records
      state.tableAttrs.pagination.total = res.result.total
      state.selectRow = []
    })
  }
}

export default { namespaced: true, state, actions, mutations: {} }
```

> 错误码文案用 `this._vm.$code('FCG-00002')`（全局原型方法，[src/utils/code-msg.js](../../../../../src/utils/code-msg.js)），不硬编码中文。⚠️ 仅 Vuex action 上下文这么写（`this` = store 实例）；组件 methods 里 `this._vm` 是 undefined，直接用 `this.$code(...)`。

### 3.3 页面组件 — `<name>Query.vue`

照 [queryListTemplate.vue](../../../../../src/template/queryListTemplate.vue)：

```vue
<template>
  <div class="programItemQuery commonQueryDiv">
    <kunkka-ux-grid
      ref="kunkka-ux-grid"
      v-bind="programItem.tableAttrs"
      :form-events="formEvents"
      @selection-change="toggleSelectRow"
      @toggleToolbarClick="toggleToolbarClick"
      @row-dblclick="toggleDblclickRow"
      @inputSearchClick="inputSearchClick"
    />
    <!-- 导入组件（资源配了 daoru/show 按钮才需要） -->
    <importDialog ref="importDialog" @uploadCallback="uploadCallback" />
    <!-- 导出组件（资源配了 daochu/show 按钮才需要） -->
    <exportDialog />
    <!-- 公共查询弹窗（搜索栏有 InputSearch 放大镜字段才需要） -->
    <kunkka-search-dialog
      ref="kunkka-search-dialog"
      @submitAction="submitAction"
      @cleanAction="cleanAction"
    />
    <!-- 弹窗兄弟组件 -->
    <programItemAdd ref="programItemAdd" />
    <programItemUpdate ref="programItemUpdate" />
    <programItemDetail ref="programItemDetail" />
  </div>
</template>
<script>
import { mapGetters } from 'vuex'
import list from '@/mixins/list'
import programItemAdd from './programItemAdd.vue'
import programItemUpdate from './programItemUpdate.vue'
import programItemDetail from './programItemDetail.vue'

export default {
  name: 'ProgramItemQuery', // 菜单缓存名，与资源管理菜单中的 cViewname 保持一致
  components: { programItemAdd, programItemUpdate, programItemDetail },
  mixins: [list],
  data() {
    return {
      name: 'programItem',   // = store 模块名 = getters 名
      formEvents: {}         // 搜索栏字段事件，如 { cSsgs: { change: fn } }
    }
  },
  computed: {
    ...mapGetters(['programItem'])
  },
  methods: {
    // 资源加载完的钩子（mixin 的 created 最后会调）：有 columnTable 操作列按钮时注入操作列
    state_init() {
      const _this = this
      if (this.programItem.tableAttrs.columnTableAttrs.length > 0) {
        this.programItem.tableAttrs.columns.push({
          title: this.$t('操作列'),
          fixed: 'left',
          width: '200',
          slots: {
            default: (scope, h) => {
              const _columnTable = []
              _this.programItem.tableAttrs.columnTableAttrs.forEach((element) => {
                _columnTable.push(
                  <el-button size='mini' onClick={() => _this.toggleToolbarClick({ item: element, scope: scope })}>
                    <i class={element.icon}></i>
                    {element.label}
                  </el-button>
                )
              })
              return [<div class='kunkka-ux-grid-toolbar'>{_columnTable}</div>]
            }
          }
        })
      }
    },

    // 勾选行回填 store（删除等批量 action 用 state.selectRow）
    toggleSelectRow(row) {
      this[this.name].selectRow = row
    },

    // 行双击（惯例：开详情弹窗）
    toggleDblclickRow(row) {
      this.$refs.programItemDetail.onDataReceive({ row })
    },

    // 搜索栏放大镜字段点击（打开公共查询弹窗）
    inputSearchClick(data) {
      this.$refs['kunkka-search-dialog'].openInit({ cNum: 'XXX', selection: false, defaultModel: {} })
    },

    // 公共查询弹窗选中回填（单选 data=行对象，字段 C_XXX 大写）
    submitAction(data, fData) {},
    cleanAction(data, fData) {},

    // 表格/工具栏/操作列按钮回调（走完 store action 后到这）
    toggleToolbarClick(data) {
      const { handle } = data.item
      const { scope } = data   // 操作列按钮时有：scope.row 当前行
      switch (handle) {
        case 'programItem/add':
          this.$refs.programItemAdd.onDataReceive({})
          break
        case 'programItem/update':
          this.$refs.programItemUpdate.onDataReceive({ row: scope.row })
          break
        default:
          break
      }
    },

    // 导入成功回调：刷新列表
    uploadCallback(res) {
      this.$store.dispatch(`${this.name}/queryList`)
    }
  }
}
</script>
```

## 4. 关键约定（踩坑高频点）

- **`list` mixin 的 created 干了所有重活**（[src/mixins/list.js](../../../../../src/mixins/list.js)）：用 `$route.meta.number` 拉资源 → `initFormItem` / `initTableColumn` / `initButtonItem` 拼出 `tableAttrs`（含 `formConfig` / `columns` / `toolbar` / `exportBtns` / `pagination`，见 mixin 源码里的完整默认值）→ 塞进 `store.getters[name]` → `dispatch(`${name}/state_init`)` + 调页面自己的 `state_init()`。页面不要重复造这些。
- **ref 名固定 `kunkka-ux-grid`**：mixin `finally` 里 `this.$refs['kunkka-ux-grid']?.redoHeight()`、TableSetting 取父级实例都按这个名字找，改名会静默失效。
- **刷新列表只有一句话**：`this.$store.dispatch(`${this.name}/queryList`)`（弹窗保存成功后通常由 store action 里自行 dispatch，页面不用管）。
- **按钮分发两级**：`handle` 有对应 store action（如 `<name>/del`）的先走 Vuex（校验勾选、confirm、调接口、刷新都在 action 里，见 vuexTemplate `del`）；action `resolve({ item: { handle: null } })` 可拦截后续；开弹窗类（add / update / detail）在页面 `toggleToolbarClick` 里 switch `handle` 调 `$refs.xxx.onDataReceive()`。
- **搜索栏字段事件写 `formEvents`**：`{ cSsgs: { change: (val) => {...} } }`，kunkka-ux-grid 内部转给 kunkka-form 的 `events`；级联下拉在这里改下游字段 `attrParam`（见 [KunkkaCustomizeSelect.md](../components/KunkkaCustomizeSelect.md)）。
- **分页默认**：pageSize 100，pageSizes [100,200,300,500]；翻页 / 改页距由 kunkka-ux-grid 内部触发 `api()`（= `dispatch(`${name}/queryList`)`），页面不写分页逻辑。
- **可编辑表格**：解开 mixin 里 `tableAttr.editConfig` 注释（`{ trigger: 'click', mode: 'cell' }`）即整个查询表可编辑；弹窗内明细表格编辑不用这个，用 `CommonTable`（[CommonTable.md](../components/CommonTable.md)）。
- **错误不重复提示**：`request.js` 已全局拦截 `code !== 200` 统一报错（530 自动重登），业务 `catch` 里别再 `$message.error()`。
- **导入 / 导出零代码集成**：资源按钮 `cStoremethod='daoru/show'` / `'daochu/show'` + 页面放 `<importDialog ref="importDialog" @uploadCallback="..."/>` / `<exportDialog />` 即可，详见 [import.md](../modules/import.md) / [export.md](../modules/export.md)。

## 5. 变体

| 变体 | 做法 |
|------|------|
| 无搜索栏 | mixin `tableAttr.useSearchForm: false`（在 mixin 拼装后覆盖，或资源不配 searchForm 字段） |
| 无分页 | `tableAttr.pagination = false` |
| 行双击开详情 | `@row-dblclick` → `$refs.xxxDetail.onDataReceive({ row })`（框架惯例） |
| 查询方案 / 显示设置 | 资源 `cTemplatetype === '0'` 自动启用（mixin 已内置 `assSearchplan` / `assShowPlan` 逻辑），无页面代码 |
| 业务履历按钮 | 表格列 `nBill` ∈ [1,2,3] 时 mixin 自动注入「查询业务履历」按钮（handle=`operationLog/FindBusiness`） |
| 国际化 | 字段 / 按钮多语言由资源 `langList` + `$t()` 处理；数据翻译重写 mixin 的 `renderI18nDataDialog(model, prop)` |

## 6. 关联资源

- **模板与 mixin**：[src/template/](../../../../../src/template/)（queryListTemplate.vue / apiTemplate.js / vuexTemplate.js）、[src/mixins/list.js](../../../../../src/mixins/list.js)、[src/mixins/configurationFile/utils.js](../../../../../src/mixins/configurationFile/utils.js)（资源→schema 的心脏）
- **组件文档**：[KunkkaUxGrid.md](../components/KunkkaUxGrid.md)、[KunkkaForm.md](../components/KunkkaForm.md)（搜索栏由它渲染）、[KunkkaSearchDialog.md](../components/KunkkaSearchDialog.md)
- **弹窗集成**：[form-modal](../modules/form-modal.md) / [table-modal](../modules/table-modal.md)、[import.md](../modules/import.md) / [export.md](../modules/export.md)
- **真实代码**：[demoQuery.vue](../../../../../src/views/demo/querylist/demoQuery.vue)（官方 demo）+ [src/template/vuexTemplate.js](../../../../../src/template/vuexTemplate.js) + [src/template/apiTemplate.js](../../../../../src/template/apiTemplate.js)（三件套源文件）
