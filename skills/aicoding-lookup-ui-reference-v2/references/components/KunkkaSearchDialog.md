# KunkkaSearchDialog 公共查询弹窗

> 「从系统已有数据里挑一条 / 几条」的业务搜索弹窗：通过 `cNum`（公共查询弹窗编号）从后端拉搜索条件 + 表格列配置，弹窗选择物料 / 客户 / 供应商等业务数据。是表单放大镜字段（InputSearch）的**标配搭档**，也是独立按钮选数据的方案。多选且要「右侧已选栏」用增强版 [MulSearchDialog.md](MulSearchDialog.md)。

> 来源库：`sunnygroup-components`（全局注册，标签 `<kunkka-search-dialog>`）｜ 内部 = KunkkaModal + KunkkaForm + ux-grid + el-pagination ｜ API 提取自 `E:\kunkka组件库\kunkka\packages\components\llms-full.txt`（源码核对，2026-09-10）｜ 数据流：`$store.dispatch('ggcxtc/show', cNum)`（store：[src/store/modules/gnzjgl/ggcxtc.js](../../../../../src/store/modules/gnzjgl/ggcxtc.js)，api：[src/api/gnzjgl/ggcxtc.js](../../../../../src/api/gnzjgl/ggcxtc.js)）

## 1. 何时使用

- 表单 / 表格里的放大镜字段：点击弹窗选择业务实体（单选为主）
- 独立按钮点击后弹窗选数据

不适用：

- 固定少量选项 → `Select` + `optionlist`（字典）
- 带附加参数的远程下拉（不用弹窗） → [KunkkaCustomizeSelect.md](KunkkaCustomizeSelect.md)
- 多选 + 已选栏 + 去重 → [MulSearchDialog.md](MulSearchDialog.md)

## 2. 导入

全局注册，模板直接写 `<kunkka-search-dialog>`，无需 import。**无 props，全部通过 `openInit(fData)` 编程式打开。**

## 3. 代码演示

### 3.1 放大镜字段选择（最常见）

```vue
<template>
  <kunkka-form ref="kunkka-form" v-bind="formData" @inputSearchClick="inputSearchClick" />
  <kunkka-search-dialog
    ref="kunkka-search-dialog"
    @submitAction="submitAction"
    @cleanAction="cleanAction"
  />
</template>
```

```javascript
methods: {
  inputSearchClick(item) {
    // item.prop 触发字段；按字段决定弹哪个 cNum、是否多选
    this.$refs['kunkka-search-dialog'].openInit({
      cNum: 'XXX_XXXX',          // 公共查询弹窗编号（后端"资源管理-公共查询弹窗"里配 SQL / 实现）
      selection: false,          // false=radio 单选（默认 true=checkbox 多选）
      defaultModel: { C_SSGS: this.formData.model.cSsgs }  // 预置查询条件
    })
  },
  // 选中提交：单选 data=行对象；多选 data=数组。字段是后端 SQL 别名（大写下划线）
  submitAction(data, fData) {
    this.formData.model.cWlbm = data.C_WLBM
    this.formData.model.cWlmc = data.C_WLMC
  },
  // 未选中点确定（清空回填）
  cleanAction(data, fData) {
    this.formData.model.cWlbm = ''
    this.formData.model.cWlmc = ''
  }
}
```

### 3.2 自定义接口（不走 cNum 配置）

```javascript
this.$refs['kunkka-search-dialog'].openInit({
  api: mySelectForPage,                    // Function | Promise，返回 { records, total }
  conditions: [/* 与 KunkkaForm form 项同构的搜索条件 */],
  tableCols: [/* 与 ux-grid columns 同构的列 */],
  cTitle: '选择物料',
  selection: true
})
```

### 3.3 表格单元格内（CommonTable 的 InputSearch 列）

```vue
<common-table @inputSearchClick="inputSearchClick" />
```

```javascript
inputSearchClick(item, row, rowIndex) {
  this.searchingRow = row           // 记住来源行
  this.$refs['kunkka-search-dialog'].openInit({ cNum: 'XXX_XXXX', selection: false })
},
submitAction(data) {
  this.searchingRow[item.field] = data.C_CODE   // 回填到行
}
```

## 4. API

### 4.1 `openInit(fData)` 参数

| 参数 | Type | Default | Description |
|------|------|---------|-------------|
| `cNum` | `string` | - | **公共查询弹窗编号（方式一，必填其一）**；配置在资源管理，走 Vuex `ggcxtc/show` |
| `api` + `conditions` + `tableCols` | - | - | **方式二**：自定义接口 + 搜索条件（KunkkaForm form 项同构）+ 列（ux-grid columns 同构） |
| `selection` | `boolean` | `true` | `false`=radio 单选 / `true`=checkbox 多选 |
| `cTitle` | `string` | - | 弹窗标题 |
| `cWidth` | `string` | `'650px'` | 宽度 |
| `cHeight` | `number` | `300` | 表格区高度 |
| `nRows` | `number` | `200` | 分页条数 |
| `defaultModel` | `Object` | - | 预置查询条件（如 `{ C_SSGS: xx }` 限范围） |
| `wheres` / `prefixUrl` / `queryPrefixUrl` | - | - | 附加查询条件 / 接口前缀（ggcxtc 参数透传） |
| `fetchPath` | `Object` | `{listField:'result.list', totalField:'result.total'}` | 响应取数路径 |

### 4.2 Events

| Event | Parameters | Description |
|-------|------------|-------------|
| `submitAction` | `(selections, fData)` | 确定且**有选中**：单选 = 行对象、多选 = 行数组；`fData` = openInit 传入的配置（回传辨别来源） |
| `cleanAction` | `(selections, fData)` | **未选中点确定**（清空场景；llms-full 未记载、源码有） |

> 行为细节：单选**双击行直接提交**；多选单击行切换勾选；打开后自动查第 1 页；搜索条件区、分页内置。

## 6. 注意事项 / FAQ

- **返回字段是大写下划线**（`C_XXX`，后端 SQL 别名）：回填 camelCase 的 model 时手动映射，别指望同名自动回填。
- **「未选中点确定」走 `cleanAction` 不走 `submitAction`**——清空回填逻辑要写在 cleanAction 里，漏写会出现「清不掉」。
- **`defaultModel` 限范围**：按公司 / 组织过滤数据时传（键也是 `C_XXX` 大写）。
- **一个弹窗实例可复用**：`fData` 会回传给 submitAction / cleanAction，可用它区分是哪个字段触发的（或每字段各放一个实例）。
- **cNum 是后端配置**：新业务弹窗要在资源管理「公共查询弹窗」里配（SQL 或自定义实现），前端只引用编号。
- **表格内多行选择回填**：记住来源行（`inputSearchClick(item, row, rowIndex)` 的 row），submitAction 里写回。

## 7. 关联资源

- **相关组件**：[MulSearchDialog.md](MulSearchDialog.md)（多选增强版）、[KunkkaForm.md](KunkkaForm.md)（InputSearch 字段）、[CommonTable.md](CommonTable.md)（表格内放大镜列）
- **标准模板**：[form-modal](../modules/form-modal.md)、[table-modal](../modules/table-modal.md)、[query-list](../page-patterns/query-list.md)
- **组件库参考**：`E:\kunkka组件库\kunkka\app\views\kunkka\docs\kunkka-search-dialog\readme.md`
- **真实代码**：[src/template/queryListTemplate.vue](../../../../../src/template/queryListTemplate.vue)、[src/template/formDialogTemplate.vue](../../../../../src/template/formDialogTemplate.vue)（inputSearchClick → openInit → submitAction 回填全套）
