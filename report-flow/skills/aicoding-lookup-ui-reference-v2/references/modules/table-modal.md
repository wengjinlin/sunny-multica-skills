# 表单 + 明细表格弹窗标准模板（table-modal）

> 弹窗内「上部表单 + 下部可编辑明细表格」一次提交，本质是 **`KunkkaModal` + `kunkka-form` + `CommonTable`** 的组合。表单字段走资源 `cArea='form'`，明细表格列走 `cArea='table'`（经 `initVxeColumn` 生成 vxe 列配置）。本模板自包含。

> 模板源文件：[src/template/formTableDialogTemplate.vue](../../../../../src/template/formTableDialogTemplate.vue) ｜ demo：[src/views/demo/querylist/demoFormTableAdd.vue](../../../../../src/views/demo/querylist/demoFormTableAdd.vue)（本文即模板精编，自包含）

## 1. 何时使用

- 主从结构数据一次录入 / 编辑：表单头 + 明细行（增删行、行内编辑、整表校验）后一次提交
- 明细行需要下拉 / 日期 / 放大镜单元格、列间级联

不适用：

- 纯表单（无明细） → [form-modal](./form-modal.md)
- 弹窗只勾选返回、不编辑 → `KunkkaSearchDialog` / `MulSearchDialog`
- 页面内嵌表格（不带弹窗） → `@/mixins/formTable`（同套路去外壳）

## 2. 文件结构

```
src/api/<模块>/<name>.js              # 追加 update_init（带明细列表回显）/ update（明细随实体一起提交）
src/views/.../<name>Update.vue        # 表单+表格弹窗（本模板）
```

> 后端资源：弹窗模块 `modnumb`；字段 `cArea='form'`（表单）、`cArea='table'`（明细列）；按钮 `cArea='table'`（表格上方工具条 `btns`，无 `cSubArea`；行内细分区域按钮配 `cSubArea='<propName>'`）。

## 3. 标准实现

### 3.1 弹窗组件

照 [formTableDialogTemplate.vue](../../../../../src/template/formTableDialogTemplate.vue)：

```vue
<template>
  <kunkka-modal
    ref="registerModal"
    :visible.sync="visible"
    :title="title"
    top="50px"
    width="1200px"
    :close-on-click-modal="false"
    :show-close="false"
    @ok="handleOk"
    @cancel="handleCancel"
  >
    <kunkka-form
      ref="kunkka-form"
      label-position="left"
      label-width="auto"
      :show-message="false"
      v-bind="formData"
      :events="events"
      @inputSearchClick="inputSearchClick"
    />
    <common-table
      v-bind="tableData"
      ref="common-table"
      @handleTableClick="toolbarClick"
      @handleValueChange="handleValueChange"
      @inputSearchClick="inputSearchClick"
    >
      <!-- 单元格自定义插槽：propName 即资源里配的 prop（内置控件不够用时覆盖） -->
      <!-- <template #nDxmId="{ row, rowIndex }">
        <el-select v-model="row.nDxmId" ... />
      </template> -->
    </common-table>
    <kunkka-search-dialog
      ref="kunkka-search-dialog"
      @submitAction="submitAction"
      @cleanAction="cleanAction"
    />
  </kunkka-modal>
</template>
<script>
import { mapGetters } from 'vuex'
import { update_init, update } from '@/api/manHourManagement/manualEntry'
import { getResourceByParIdOrModnumb } from '@/mixins/configurationFile/utils'

export default {
  data() {
    return {
      visible: false,
      title: this.$t('编辑'),
      formData: { gutter: 20, showMessage: false, size: 'mini', form: [], button: [], model: {} },
      tableData: { data: [], columns: [], btns: [], loading: false },
      modalBtn: [],
      inlineBtns: [],
      events: {}
    }
  },
  computed: {
    ...mapGetters(['manualEntry'])
  },
  methods: {
    onDataReceive(data) {
      const { row } = data
      getResourceByParIdOrModnumb({ modnumb: '<弹窗资源modnumb>' }).then(result => {
        const { resFieldList, resColumnList, resButtonList } = result
        this.formData.form = resFieldList['form']
        this.formData.button = resButtonList['form']
        this.tableData.columns = resColumnList['table']   // initVxeColumn 已生成 vxe 列
        this.tableData.btns = this._.filter(resButtonList['table'], ['cSubArea', null])  // 表格上方按钮（用 this._，勿照抄模板的裸 _，见 §4）
        // this.inlineBtns = this._.filter(resButtonList['table'], ['cSubArea', '<propName>']) // 行内按钮
        this.formData.model = {}
        this.tableData.data = []
        this.modalBtn = this._.filter(resButtonList['form'])
        update_init({ manualEntry: { id: row.id } }).then(res => {
          this.formData.model = res.result
          this.tableData.data = res.result.manualEntrymxList   // 明细列表字段名按后端约定
        })
        this.visible = true
        this.$nextTick(() => {
          this.$refs['kunkka-form'].$refs['kunkkaForm'].clearValidate()
        })
      })
    },

    // 表格上方按钮 / 行内按钮统一回调
    async toolbarClick(btdata, row, rowIndex) {
      const { handle } = btdata
      switch (handle) {
        case 'addRow':
          this.tableData.data.push({})
          break
        case 'delRow':
          this.$refs['common-table'].removeCheckRow().catch(() => {
            this.$message.warning(this.$t('请至少选择一条记录'))
          })
          break
        default:
          break
      }
    },

    // 单元格值变化（联动其他单元格在这里写）
    handleValueChange({ value, row, rowIndex, item }) {},

    inputSearchClick(item, row, rowIndex) { /* 打开 kunkka-search-dialog，回填 row[item.field] */ },
    submitAction(data, fData) {},
    cleanAction(data, fData) {},

    // 确定：表单校验 → 表格校验 → 提交（明细随实体一起）
    handleOk() {
      this.$refs['kunkka-form'].$refs['kunkkaForm'].validate(async(valid) => {
        if (!valid) return false
        await this.$refs['common-table'].validateTable()   // 必填列非空校验，不过则 reject
        this.$refs.registerModal.changeOkLoading(true)
        this.formData.model.manualEntrymxList = this.tableData.data
        update({ manualEntry: { ...this.formData.model } }).then(res => {
          this.$store.dispatch('manualEntry/queryList')
          this.visible = false
        }).finally(() => {
          this.$refs.registerModal.changeOkLoading(false)
        })
      })
    },

    handleCancel() {
      this.visible = false
    }
  }
}
</script>
```

### 3.2 CommonTable 的单元格编辑

明细列在资源里配 `cFieldtype` 后由 `initVxeColumn` 生成，`CommonTable` 按列的 `components` 渲染内置编辑控件（详见 [CommonTable.md](../components/CommonTable.md)）：

| 列 `components` | 渲染 |
|-----------------|------|
| `Input` | `el-input`（clearable） |
| `Select` | `el-select` + `params.optionlist`（`{cKeyname, cKeynumb}`） |
| `date` / `datetime` | `el-date-picker`（值格式 `yyyy-MM-dd` / `yyyy-MM-dd HH:mm:ss`） |
| `InputSearch` | 只读 `el-input` + 放大镜按钮，点击 emit `inputSearchClick(item, row, rowIndex)` |
| 其他 / 复杂交互 | 页面用 `#<prop>` 插槽覆盖（如级联 el-select、remote 搜索） |

## 4. 关键约定（踩坑高频点）

- **提交前两段校验缺一不可**：`kunkka-form` 双层 ref `validate()`（表单）+ `await this.$refs['common-table'].validateTable()`（明细必填列）；`validateTable` 失败是 reject，务必 `await`，别吞掉继续提交。
- **`removeCheckRow()` 无勾选时 reject**：catch 里给「请至少选择一条记录」提示。
- **明细数据就在 `tableData.data`**：单元格 `v-model="row[field]"` 双向改的就是它，提交时整个数组挂到实体字段（如 `xxxmxList`）一次传后端；不需要「先取数再转换」。
- **取勾选行**（提交勾选返回类需求）：`this.$refs['common-table'].$refs['commonTable'].getCheckboxRecords()`（双层 ref 到 vxe 实例）。
- **表格上方按钮 = 资源 `cArea='table'` 无 `cSubArea` 按钮**（`tableData.btns`，CommonTable 自渲染工具条）；点击统一走 `@handleTableClick` → `toolbarClick(item)` 按 `handle` 分发。
- **弹窗要够大**：明细表格弹窗惯例 `width="1200px"` + `top="50px"`（表格多时 `canFullscreen` 全屏）。
- **别手写明细列**：列来自资源（`initVxeColumn`）；内置控件不够用先看 `params.optionlist` / 函数型 `disabled` / `multiple` / `filterable`，再不行才 `#<prop>` 插槽。
- **错误不重复提示**：`request.js` 已全局拦截，业务 `catch` 别再 `$message.error()`。
- **lodash 用 `this._.`，别照抄模板里的裸 `_`**：官方模板 / demo 里的 `_.filter(...)` 写的是裸 `_` 且未 import lodash——全项目没有 `window._` 全局，照抄运行时 ReferenceError。`_` 挂在 `Vue.prototype`（[src/plugins/lodash.js](../../../../../src/plugins/lodash.js)），组件里写 `this._.filter(...)` 即可。

## 5. 变体

| 变体 | 做法 |
|------|------|
| 多 Tab 明细 | [formTabsDialogTemplate.vue](../../../../../src/template/formTabsDialogTemplate.vue) + `@/mixins/formTabsModal`（demo：[demoFormTabsAdd.vue](../../../../../src/views/demo/querylist/demoFormTabsAdd.vue)） |
| 页面内嵌表格（无弹窗） | `@/mixins/formTable`（同一套 CommonTable 用法，去掉 KunkkaModal 外壳） |
| 勾选返回（不编辑） | `showCheckbox` + 提交时 `getCheckboxRecords()`，emit 给父组件 |
| 只读明细 | Detail 弹窗 + 插槽换成纯文本 / `editConfig` 不启用 |

## 6. 关联资源

- **组成组件**：[KunkkaModal.md](../components/KunkkaModal.md)、[KunkkaForm.md](../components/KunkkaForm.md)、[CommonTable.md](../components/CommonTable.md)、[KunkkaSearchDialog.md](../components/KunkkaSearchDialog.md)
- **页面集成**：[query-list](../page-patterns/query-list.md)（工具栏 / 操作列按钮 `onDataReceive` 打开）
- **真实代码**：[src/template/formTableDialogTemplate.vue](../../../../../src/template/formTableDialogTemplate.vue)（官方模板）、[src/views/demo/querylist/demoFormTableAdd.vue](../../../../../src/views/demo/querylist/demoFormTableAdd.vue)（官方 demo）
