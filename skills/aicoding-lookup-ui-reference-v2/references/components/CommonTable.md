# CommonTable 可编辑明细表格

> vxe-table 封装的项目全局业务表格（**弹窗内明细 / 页面内嵌明细的标准件**）：按列 `components` 内置单元格编辑控件、必填红星表头、表格上方按钮栏、整表校验。与查询页主体的 `kunkka-ux-grid`（umy-ui）是两套——**明细编辑用本组件，查询列表用 ux-grid**。

> 来源：[src/components/Sunnyoptical/commonTable/index.vue](../../../../../src/components/Sunnyoptical/commonTable/index.vue)（[src/plugins/sunnyoptical.js](../../../../../src/plugins/sunnyoptical.js) 全局注册，标签 `<common-table>`）｜ 底层 vxe-table 3.6（[src/components/VXE/index.js](../../../../../src/components/VXE/index.js)）

## 1. 何时使用

- 弹窗内明细表格（表单 + 明细一次提交，见 [table-modal](../modules/table-modal.md)）
- 页面内嵌可编辑表格（`@/mixins/formTable`）
- 行内编辑 + 必填校验 + 增删行的任何明细场景

不适用：

- 查询列表页主体（搜索 + 分页 + api 驱动） → [KunkkaUxGrid.md](KunkkaUxGrid.md)
- 纯展示小表格 → `el-table`（Element 兜底层）

## 2. 导入

全局注册，模板直接写 `<common-table>`，无需 import。

## 3. 代码演示

### 3.1 基础用法（v-bind tableData）

```vue
<common-table
  v-bind="tableData"
  ref="common-table"
  @handleTableClick="toolbarClick"
  @handleValueChange="handleValueChange"
  @inputSearchClick="inputSearchClick"
/>
```

```javascript
tableData: {
  data: [],       // 行数据（单元格 v-model 直接改它）
  columns: [],    // vxe 列（资源 initVxeColumn 生成）
  btns: [],       // 表格上方按钮（资源 cArea='table' 无 cSubArea 按钮）
  loading: false
}
```

### 3.2 提交（两段校验 + 删行）

```javascript
async handleOk() {
  this.$refs['kunkka-form'].$refs['kunkkaForm'].validate(async(valid) => {
    if (!valid) return false
    await this.$refs['common-table'].validateTable()   // 必填列非空校验（失败 reject）
    // 提交：明细就在 tableData.data
  })
}

// 删除勾选行（无勾选 reject，catch 里提示）
this.$refs['common-table'].removeCheckRow().catch(() => {
  this.$message.warning(this.$t('请至少选择一条记录'))
})
```

### 3.3 插槽覆盖单元格（复杂交互）

```vue
<common-table v-bind="tableData" ref="common-table">
  <!-- 列 prop = nDxmId：级联 el-select（复杂交互时覆盖内置控件） -->
  <template #nDxmId="{ row, rowIndex }">
    <el-select v-model="row.nDxmId" filterable remote :remote-method="..."
      @change="val => onDxmChange(val, row)">
      <el-option v-for="op in dxmOptions" :key="op.cKeynumb"
        :label="op.cKeyname" :value="op.cKeynumb" />
    </el-select>
  </template>

  <!-- 行内操作按钮列（资源 cSubArea='<propName>' 按钮） -->
  <template #action="{ row, rowIndex }">
    <el-button v-for="btn in inlineBtns" :key="btn.nButtonid"
      @click="toolbarClick(btn, row, rowIndex)">{{ btn.label }}</el-button>
  </template>
</common-table>
```

## 4. API

### 4.1 Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `showCheckbox` | `boolean` | `true` | 首列多选框 |
| `showIndex` | `boolean` | `true` | 序号列 |
| `showExpand` | `boolean` | `false` | 展开行（配 `#expand` 插槽） |
| `size` | `string` | `'mini'` | 尺寸 |
| `showOverflow` / `showHeaderOverflow` | `string` | `'title'` | 溢出显示 |
| `editConfig` | `Object` | `{trigger:'maual', mode:'row', showStatus:true}` | vxe 编辑配置（⚠️ 默认值 `maual` 就是源码拼写，保持勿改） |

> **数据三件经 `$attrs` 传**（`v-bind="tableData"`）：`data` / `columns` / `btns`；其余 `$attrs` / `$listeners` 全透传 vxe-table（`edit-rules` / `tree-config` / `height` …）。

### 4.2 列配置（columns 元素，资源 `initVxeColumn` 生成）

| 键 | 说明 |
|----|------|
| `field` / `title` | 字段 / 标题 |
| `components` | 内置编辑控件：`Input` / `Select`（选项 `params.optionlist`）/ `date` / `datetime` / `InputSearch`（放大镜，点击 emit `inputSearchClick`）；纯展示：`spanselect`（值经 `filterSelect` 过滤器按 `params.optionlist` 翻译成显示名，不可编辑） |
| `required` | `true` 时表头红星 + `validateTable()` 参与校验 |
| `params.optionlist` | Select 选项 `[{cKeyname, cKeynumb}]` |
| `disabled` / `multiple` / `filterable` | 布尔**或函数** `(row, field, item) => boolean`（按行动态控制） |
| 其余 | 透传 vxe-column（`width` / `fixed` / `visible` …） |

### 4.3 Events

| Event | Parameters | Description |
|-------|------------|-------------|
| `handleTableClick` | `(item)` | 表格上方按钮栏点击（`btns` 里的一项） |
| `handleValueChange` | `({value, row, rowIndex, item})` | 任意内置单元格值变化（联动写这里） |
| `inputSearchClick` | `(item, row, rowIndex)` | 放大镜单元格点击（打开 kunkka-search-dialog 后回填 `row[item.field]`） |
| vxe 透传 | - | `selection-change` / `checkbox-change` / `cell-click` 等（`$listeners` 直通） |

### 4.4 Methods（`this.$refs['common-table']`）

| Method | Description |
|--------|-------------|
| `validateTable()` | **必填列非空校验**（`required: true` 列逐列 every；失败 `$message.error('xx不能为空')` + reject） |
| `handleValidate(showMessage?)` | **vxe editRules 完整校验**（列配 `edit-rules` 时用；错误定位到行列，HTML 汇总提示；返回 errMap） |
| `removeCheckRow()` | 删除勾选行（resolve 剩余数据；**无勾选 reject**） |
| vxe 原生 | 双层 ref：`this.$refs['common-table'].$refs['commonTable']`（`getCheckboxRecords()` / `insertAt` / `revert` …） |

### 4.5 Slots

| Slot | Description |
|------|-------------|
| `#<prop>` | 覆盖某列单元格，作用域 `{ item, row, rowIndex }`（`item` = 列配置） |
| `#expand` | 展开行内容，作用域 `{ row, rowIndex }` |

## 6. 注意事项 / FAQ

- **单元格值变化自动 `updateStatus`**（vxe 编辑态同步）再 emit `handleValueChange`——自定义插槽里改 `row` 后如需触发校验刷新，参考内置实现手动调 `$refs.commonTable.updateStatus({row, column})`。
- **两套校验按需选**：资源 `cRequired` → `validateTable()`（非空级）；列 `edit-rules` → `handleValidate()`（规则级）。提交前 `await`，别吞 reject。
- **数据不用「取出再转」**：单元格直接改 `tableData.data` 的行对象，提交时整个数组挂实体字段（如 `xxxmxList`）。
- **取勾选行走双层 ref**：`$refs['common-table'].$refs['commonTable'].getCheckboxRecords()`。
- **按钮栏自动渲染**：`btns` 非空即渲染表格上方按钮条（`btns.length > 0`），点击统一 `@handleTableClick`。
- **表格上方 / 行内按钮来自同一资源区**：`cArea='table'` 无 `cSubArea` → `btns`；`cSubArea='<propName>'` → 行内（页面自己接插槽渲染）。

## 7. 关联资源

- **相关组件**：[KunkkaModal.md](KunkkaModal.md)（弹窗外壳）、[KunkkaSearchDialog.md](KunkkaSearchDialog.md)（放大镜单元格）、[KunkkaUxGrid.md](KunkkaUxGrid.md)（查询页表格，注意区分）
- **标准模板**：[table-modal](../modules/table-modal.md)、`@/mixins/formTable`（页面内嵌）
- **真实代码**：[src/template/formTableDialogTemplate.vue](../../../../../src/template/formTableDialogTemplate.vue)（官方模板）、[src/views/demo/querylist/demoFormTableAdd.vue](../../../../../src/views/demo/querylist/demoFormTableAdd.vue)（官方 demo）
