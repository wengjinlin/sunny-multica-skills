# KunkkaCustomizeSelect 自定义下拉

> 按 `cNum`（自定义下拉编号）从后端拉选项的远程下拉，选项 `{cKeyname, cKeynumb, cSlot}`；支持远程搜索、第二列显示、**`attrParam` 级联传参**。表单里以字段类型 `CustomizeSelect`（资源 `cSeltype='3'`）使用，是「选项由后端配置 / 需要级联」场景的**强制组件**（禁止手写 el-select + 自己查 options）。

> 来源库：`sunnygroup-components`（表单内由 basic-form-dom 渲染；也可独立用标签 `<kunkka-customize-select>`）｜ 数据流：`$store.dispatch('zdyxlk/assQuery', {cNum, attrParam})` → `/core/assSelect/commonQuery`（api：[src/api/gnzjgl/zdyxlk.js](../../../../../src/api/gnzjgl/zdyxlk.js)）｜ API 提取自 `E:\kunkka组件库\kunkka\packages\components\llms-full.txt`（源码核对，2026-09-10）

## 1. 何时使用

- 表单字段下拉：选项来自后端「自定义下拉」配置（cNum），如项目下拉、客户下拉
- **级联**：下游选项依赖上游字段值（选了公司 → 项目下拉只出该公司的）
- 远程搜索型长列表下拉

不适用：

- 数据字典（资源 `cSeltype='0'`）→ 资源带 `fieldDictList`，普通 Select
- 前端固定枚举（`cSeltype='1'`） → [src/utils/select-options.js](../../../../../src/utils/select-options.js)
- 弹窗选择 → [KunkkaSearchDialog.md](KunkkaSearchDialog.md)

## 2. 导入

表单内**不需要 import**——资源字段 `cFieldtype='CustomizeSelect'`（或 form 项 `components: 'CustomizeSelect'`）即渲染。独立使用时全局标签 `<kunkka-customize-select>`。

## 3. 代码演示

### 3.1 表单字段（资源驱动）

资源字段配 `cFieldtype='CustomizeSelect'`、`cSeltype='3'`、`cNum`（自定义下拉编号）即可，`initFormItem` 生成：

```javascript
// initFormItem 产物（示意）
{ label: '项目', prop: 'cXmdl', components: 'CustomizeSelect',
  params: { cNum: 'XXX_XXXX' } }
```

### 3.2 级联联动（最常见：上游 change 改下游 attrParam）

```javascript
// form 的 events（或搜索栏 formEvents）
events: {
  cSsgs: {                                   // 上游：公司
    change: (val) => {
      const target = this.formData.form.find(f => f.prop === 'cXmdl')   // 下游：项目
      if (target) {
        // attrParam 变化触发 zdyxlk 重新查询，选项随之刷新
        this.$set(target.params, 'attrParam', { cCompany: val })
      }
    }
  }
}
```

### 3.3 独立使用

```vue
<kunkka-customize-select
  v-model="value"
  c-num="XXX_XXXX"
  :attr-param="{ cCompany: cSsgs }"
  @selectChange="(val, $this) => {...}"
/>
```

## 4. API

### 4.1 Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `string` | `''` | v-model（选中值 = `cKeynumb`） |
| `cNum` | `string` | `''` | **自定义下拉编号（必填）**，后端资源管理里配 |
| `attrParam` | `Object` | `{}` | **查询附加参数；变化会重新查询**（级联核心） |
| `defaultQuery` | `boolean` | `true` | 挂载即查一次 |
| `defaultConfig` | `Object` | `{}` | 下拉配置覆盖（`nType` 0=普通 / 1=远程搜索默认；`cLabelslotcol` 第二列字段；`nSearchinterval` 搜索节流默认 700ms） |
| `handle` | `string` | `''` | 选中后要 dispatch 的 Vuex action |

### 4.2 Events

| Event | Parameters | Description |
|-------|------------|-------------|
| `input` | `value` | v-model 更新 |
| `selectChange` | `(value, $this)` | 选中变化（推荐用这个做联动） |
| `change` | `({value, $this})` | 同上，参数打包 |
| `clear` | - | 清空 |

### 4.3 选项结构

```javascript
{ cKeyname: '显示名', cKeynumb: '值', cSlot: '第二列显示（配 cLabelslotcol 时）' }
```

## 6. 注意事项 / FAQ

- **级联靠 `attrParam` 引用变化**：直接改对象内部属性可能不触发（watch 的是引用），用 `$set` 换新对象 / 新值；上游事件写在 `events` / `formEvents` 里。
- **cNum 是后端配置**：新下拉在资源管理「自定义下拉」里配（SQL / 实现），前端只引用编号；选项缓存与查询走 Vuex `zdyxlk` 模块。
- **远程搜索默认开**（`nType: '1'`）：输入 700ms 节流后带关键字重查；要纯下拉配 `defaultConfig: { nType: '0' }`。
- **表格列里的同类下拉**：CommonTable 单元格用 `Select` + `params.optionlist`（页面自己查好塞进去），或插槽自写。
- **选项值是 `cKeynumb`**：提交 / 比较都用它，显示名 `cKeyname` 仅展示。

## 7. 关联资源

- **相关组件**：[KunkkaForm.md](KunkkaForm.md)（表单宿主）、[KunkkaSearchDialog.md](KunkkaSearchDialog.md)（弹窗选择）
- **标准模板**：[form-modal](../modules/form-modal.md)、[query-list](../page-patterns/query-list.md)（`formEvents` 级联）
- **真实代码**：级联套路见 [query-list.md](../page-patterns/query-list.md) §4 `formEvents` 级联、[CommonTable.md](CommonTable.md) §3.3 插槽级联
