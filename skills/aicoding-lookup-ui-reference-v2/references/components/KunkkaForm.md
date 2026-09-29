# KunkkaForm 表单

> 资源 schema 驱动的表单组件（内部由 `basic-form-dom` 渲染引擎逐字段生成 Element 控件），是所有表单场景的**强制组件**（禁止直接手写 `el-form` 拼页面表单）。搜索栏通常不直接写它——由 `kunkka-ux-grid` 的 `formConfig` 内嵌渲染。

> 来源库：`sunnygroup-components`（[main.js](../../../../../src/main.js) `Vue.use` 全局注册，标签 `<kunkka-form>`）｜ API 提取自 `E:\kunkka组件库\kunkka\packages\components\llms-full.txt`（源码核对，2026-09-10）｜ 实装版本以所在工程 node_modules 为准

## 1. 何时使用

- 弹窗内新增 / 编辑 / 详情表单（`v-bind="formData"`，字段数组来自资源 `cArea='form'`）
- `formEvents` / `events` 做字段联动；放大镜字段（InputSearch）配 `kunkka-search-dialog`
- 需要独立手写表单时（少数自定义场景）直接传 `form` 数组

不适用：

- 搜索栏 → 配资源 `cArea='searchForm'`，由 `kunkka-ux-grid` 渲染（[query-list](../page-patterns/query-list.md)）
- 纯展示 → 文本 / `el-descriptions` 思路

## 2. 导入

全局注册，模板直接写 `<kunkka-form>`，无需 import。

## 3. 代码演示

### 3.1 弹窗表单（资源驱动，最常见）

```vue
<kunkka-form
  ref="kunkka-form"
  label-position="left"
  label-width="auto"
  :show-message="false"
  v-bind="formData"
  :events="events"
  @inputSearchClick="inputSearchClick"
/>
```

```javascript
// formData 由 onDataReceive 里资源接口填充（见 form-modal 模板）
formData: {
  gutter: 20,
  showMessage: false,
  size: 'mini',
  form: [],      // 字段配置数组（资源 initFormItem 生成）
  button: [],
  model: {}      // 表单值，双向同步
},
events: {}       // 字段事件
```

### 3.2 字段事件（联动）

```javascript
events: {
  cSsgs: {                       // 字段 prop
    change: (val) => {           // Element 控件事件名
      // 联动：改下游自定义下拉的查询参数（触发重查）
      const target = this.formData.form.find(f => f.prop === 'cXmdl')
      if (target) {
        this.$set(target.params, 'attrParam', { cCompany: val })
      }
    }
  }
}
```

### 3.3 手写 form 数组（自定义场景兜底）

```javascript
formData: {
  model: {},
  form: [
    { label: '名称', prop: 'cName', components: 'Input', lg: 8 },
    { label: '状态', prop: 'nZt', components: 'Select',
      optionlist: [{ cKeyname: '启用', cKeynumb: '1' }, { cKeyname: '停用', cKeynumb: '0' }] },
    // 自定义字段：配 components: 'Slot' 后模板写 <template #cRemark="{ item, model }">
    { label: '备注', prop: 'cRemark', components: 'Slot' }
  ]
}
```

## 4. API

### 4.1 Props（常用）

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `form` | `Array` | `[]` | 字段配置数组（资源 `initFormItem` 生成或手写） |
| `model` | `Object` | `{}` | 表单值（kunkka-form 内部与父级双向同步） |
| `events` | `Object` | `{}` | 字段事件 `{ [prop]: { [事件名]: fn } }` |
| `handle` | `Array` | `[]` | 附加按钮配置 |
| `lg` / `md` | `number` | `8` / `8` | 每项默认栅格占位（24 栅；搜索栏常用 `lg: 4` 一行六格） |
| `gutter` | `number` | `0` | 栅格间距 |
| `size` | `string` | `'mini'` | 尺寸 |
| `title` | `string \| boolean` | `false` | 标题（false 隐藏） |
| `showActionButtonGroup` | `boolean` | `false` | 是否显示提交 / 重置按钮组 |
| `showSubmitButton` / `showResetButton` | `boolean` | `true` | 提交 / 重置按钮 |
| `showSearchPlanButton` | `boolean` | `true` | 查询方案按钮（dispatch `assSearchplan/show`） |
| `showAdvancedButton` | `boolean` | `false` | 高级搜索折叠按钮（搜索栏用） |
| `useEntrySearch` | `boolean` | `true` | 回车触发查询（内置 `v-EntrySearch` 指令） |
| `actionColOptions` | `Object` | `{lg:4, md:4}` | 按钮组列宽 |

> `labelWidth` / `label-position` / `rules` / `disabled` / `show-message` 等经 `$attrs` 透传内层 `el-form`。

### 4.2 字段项（form 数组元素 / 资源 `initFormItem` 产物）

| 键 | 说明 |
|----|------|
| `components` | 控件类型：`Input` / `InputNumber` / `Select` / `Radio` / `RadioGroup` / `Switch` / `DatePicker` / `InputSearch`（放大镜）/ `SelectSearch`（标签+放大镜）/ `Autocomplete` / `CheckBox`（带全选）/ `CustomizeSelect` / `Upload` / `Cascader` / `Slot`（自定义插槽） |
| `label` / `prop` | 标签 / 字段名（对齐后端） |
| `optionlist` | 选项数组 `{cKeyname, cKeynumb, cSlot}`（字典 / 枚举） |
| `lg` / `md` | 单项栅格覆盖 |
| `tip` | label 后问号提示 |
| `isShow` / `show` | 显隐，布尔或 `({model, form}) => boolean`（资源 `cDynamicShow` 生成） |
| `dynamicRules(model, prop)` | 动态校验规则（资源 `cDynamicRules` 生成） |
| `disabled` | 禁用，布尔或函数 |
| 其余 | 透传对应 Element 控件（`placeholder` / `filterable` / `multiple` …） |

### 4.3 Events

| Event | Parameters | Description |
|-------|------------|-------------|
| `handleSubmit` | `model` | 提交按钮（showActionButtonGroup 时） |
| `handleReset` | `{model}` | 重置按钮 |
| `inputSearchClick` | `(item, event)` | 放大镜字段点击（打开 `kunkka-search-dialog` 的入口） |
| `toggleAdvanced` | `{isAdvanced}` | 高级搜索折叠切换 |

### 4.4 Methods（`this.$refs['kunkka-form']`）

| Method | Description |
|--------|-------------|
| `vaild()` | 触发校验（注意拼写就是 `vaild`） |
| `clearValid()` | 清除校验状态 |
| `changeValue(prop, value)` | 设置单字段值 |
| `changeForm(form)` | 整体替换 form 数组（`{}` 重置对象 / `[]` 重置数组） |
| `setIsAdvanced(bool)` | 设置高级搜索折叠态 |
| `setMergeProps(props)` | 合并 props |

> **el-form 原生能力走双层 ref**：`this.$refs['kunkka-form'].$refs['kunkkaForm']`（内部 el-form 实例）——`validate(cb)` / `clearValidate()` / `resetFields()`。

### 4.5 Slots

| Slot | Description |
|------|-------------|
| `#<prop>` | 自定义字段渲染，作用域 `{ item, model }`（字段配 `components: 'Slot'`） |
| `#footer` | 替换按钮组 |

## 6. 注意事项 / FAQ

- **校验 / 清校验用双层 ref**（`['kunkka-form'].$refs['kunkkaForm']`），单层拿不到 el-form 实例——「validate is not a function」基本都是这原因。
- **字段配置来自资源**（`cFieldtype` → `components`、`cSeltype` 决定选项来源），**禁止在业务 `.vue` 里手写 form 数组**（原型兜底除外，须注明待迁回资源）。
- **回显**：直接改 `formData.model`（`update_init` 接口返回）；打开弹窗后 `$nextTick` 里 `clearValidate()` 清残留。
- **默认值**：资源字段 `cDefval` 经 `initFormItem` 变成 `defVal`，mixin 填进 `model`。
- **国际化数据**：字段多语言编辑重写 mixin 的 `renderI18nDataDialog(model, prop)`（dispatch `i18nDataDialog/show`）。
- **提示用 Element 的 `$message`**；接口错误 `request.js` 已全局拦截，别重复报。

## 7. 关联资源

- **相关组件**：[KunkkaModal.md](KunkkaModal.md)（表单弹窗外壳）、[KunkkaSearchDialog.md](KunkkaSearchDialog.md)（放大镜字段配套）、[KunkkaCustomizeSelect.md](KunkkaCustomizeSelect.md)（CustomizeSelect 字段）
- **标准模板**：[form-modal](../modules/form-modal.md)、[table-modal](../modules/table-modal.md)、[query-list](../page-patterns/query-list.md)（搜索栏内嵌）
- **组件库参考**：`E:\kunkka组件库\kunkka\app\views\kunkka\kunkka-form.vue`（demo）、`E:\kunkka组件库\kunkka\app\views\kunkka\docs\kunkka-form\readme.md`（docs）
- **真实代码**：[src/template/formDialogTemplate.vue](../../../../../src/template/formDialogTemplate.vue)（官方模板）、[src/views/demo/querylist/demoAdd.vue](../../../../../src/views/demo/querylist/demoAdd.vue)（官方 demo）
