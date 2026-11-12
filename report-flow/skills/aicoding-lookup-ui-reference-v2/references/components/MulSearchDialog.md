# MulSearchDialog 多选搜索弹窗（带已选栏）

> 对 `kunkka-search-dialog` 的**多选增强拷贝**（随工程脚手架内置）：左侧查询表格勾选 → 「确认选择」加入**右侧已选栏** → 确定返回。支持回显已选、按关键字段去重。选物料 / 客户 / 产品等多个业务实体并拼逗号串的场景用它（单选 / 简单多选直接用 [KunkkaSearchDialog.md](KunkkaSearchDialog.md)）。

> 来源：[src/components/MulSearchDialog/index.vue](../../../../../src/components/MulSearchDialog/index.vue)（按需引入，非全局注册）｜ 内部同样走 Vuex `ggcxtc/show`（cNum 配置驱动）

## 1. 何时使用

- 多选业务实体且需要**已选回显 / 去重**（编辑回显时把已选传回来）
- 选中多项后拼「代码,代码」/「名称,名称」回填两个字段

不适用：

- 单选 → `kunkka-search-dialog`（`selection: false`）
- 下拉选择（不弹窗） → [KunkkaCustomizeSelect.md](KunkkaCustomizeSelect.md)

## 2. 导入

```javascript
import mulSearchDialog from '@/components/MulSearchDialog'

export default {
  components: { mulSearchDialog }
}
```

## 3. 代码演示

### 3.1 多选回填（最常见）

```vue
<template>
  <kunkka-form ref="kunkka-form" v-bind="formData" @inputSearchClick="inputSearchClick" />
  <mul-search-dialog ref="mul-search-dialog" @submitAction="submitAction" />
</template>
```

```javascript
methods: {
  inputSearchClick(item) {
    this.$refs['mul-search-dialog'].openInit({
      cNum: 'XXX_XXXX',            // 公共查询弹窗编号
      selection: true,             // 多选（本组件就是为多选而生）
      cWidth: '850px',
      // 回显已选：把已回填的值还原成对象数组（按 cNum 的 SQL 字段构造）
      selected: this.formData.model.cKjlxbm
        ? this.formData.model.cKjlxbm.split(',').map((bm, i) => ({
          C_XXX: bm,
          C_XXXNAME: (this.formData.model.cKjlxmc || '').split(',')[i]
        }))
        : [],
      singleCol: ['C_XXX'],        // 去重键（重复勾选不进已选栏）
      selectedCol: ['C_XXX', 'C_XXXNAME'],  // 右侧已选栏显示列
      defaultModel: {}
    })
  },
  // 确定：data = 已选数组（含回显 + 新选）
  submitAction(data) {
    this.formData.model.cKjlxbm = data.map(d => d.C_XXX).join(',')
    this.formData.model.cKjlxmc = data.map(d => d.C_XXXNAME).join(',')
  }
}
```

## 4. API

### 4.1 `openInit(fData)` 参数（kunkka-search-dialog 参数全部可用，另加）

| 参数 | Type | Description |
|------|------|-------------|
| `selected` | `Array` | **回显已选**（对象数组，字段用 `C_XXX` 大写）；不传每次打开从空开始 |
| `singleCol` | `string[]` | **去重键**：勾选项按这些字段与已选比对，重复不加入 |
| `selectedCol` | `string[]` | 右侧已选栏每项显示的字段 |

> 其余（`cNum` / `api`+`conditions`+`tableCols` / `selection` / `cWidth` / `cHeight` / `nRows` / `defaultModel` …）同 [KunkkaSearchDialog.md §4.1](KunkkaSearchDialog.md)。

### 4.2 Events

| Event | Parameters | Description |
|-------|------------|-------------|
| `submitAction` | `(selected, fData)` | 确定返回**已选数组**（右侧栏全量 = 回显 + 新选 − 手动删除）；单选模式双击行提交 `(row, fData)` |

> ⚠️ **没有 `cleanAction` 事件**（与 kunkka-search-dialog 不同，源码只 emit `submitAction`）：点「确认」**总是**触发 `submitAction`——未选任何项时收到**空数组 `[]`**（清空场景在业务侧判空处理），不要监听不存在的 `@cleanAction`。

### 4.3 交互

- 左侧表格勾选 → 点「确认选择」（`confirm()`）加入右侧已选栏（按 `singleCol` 去重）
- 右侧每项 `×` 可手动移除
- 单选模式下双击行直接提交（同 kunkka-search-dialog）

## 6. 注意事项 / FAQ

- **`selected` 回显要自己构造对象数组**：后端存的是逗号串，回填前按存储格式 split 再 map 成行对象（字段名与 cNum 的 SQL 别名一致，`C_XXX` 大写）。
- **去重靠 `singleCol`**：不传会重复加入；通常传业务主键（代码列）。
- **必须 `selection: true`**：单选没必要用本组件。
- **标签页关闭/重开**：`selected` 不传或传空数组即清空重来。

## 7. 关联资源

- **相关组件**：[KunkkaSearchDialog.md](KunkkaSearchDialog.md)（单选 / 基础版）
- **标准模板**：[form-modal](../modules/form-modal.md)
- **真实代码**：在所在工程 `src/views/` 全局搜索 `MulSearchDialog` 引用可找多选回填实例
