# KunkkaModal 弹窗

> 基于 `el-dialog` 封装的增强弹窗（拖拽 / 全屏 / 最小化 / 底部按钮扩展位），是项目所有弹窗场景的**强制组件**（禁止直接用 `el-dialog` 拼业务弹窗）。

> 来源库：`sunnygroup-components`（全局注册，标签 `<kunkka-modal>`）｜ API 提取自 `E:\kunkka组件库\kunkka\packages\components\llms-full.txt`（源码核对，2026-09-10）

## 1. 何时使用

- 新增 / 编辑 / 查看类弹窗（内含 kunkka-form / CommonTable）
- 明细编辑、导入导出弹窗（importDialog / exportDialog 内部也是它）等业务交互
- 需要底部扩展按钮（取消 / 确定之外）或全屏 / 拖拽

不适用：

- 轻量操作确认 → `MessageBox.confirm()`（不要为此开全量弹窗）
- 侧边抽屉 → `el-drawer`

## 2. 导入

全局注册，模板直接写 `<kunkka-modal>`，无需 import。

## 3. 代码演示

### 3.1 基础用法（项目标准形态）

受控开关用 **`:visible.sync`**；项目惯例子组件自持 `visible`、由父组件 `$refs` 调 `onDataReceive` 打开：

```vue
<kunkka-modal
  ref="registerModal"
  :visible.sync="visible"
  :title="title"
  width="960px"
  :close-on-click-modal="false"
  :show-close="false"
  @ok="handleOk"
  @cancel="handleCancel"
>
  <kunkka-form ref="kunkka-form" v-bind="formData" :events="events" />
</kunkka-modal>
```

```javascript
// 父组件打开：this.$refs.xxxAdd.onDataReceive({ row })
// 子组件：
methods: {
  onDataReceive(data) {
    // ...加载资源 / 回显
    this.visible = true
  },
  handleOk() {
    this.$refs.registerModal.changeOkLoading(true)
    save(...).then(() => { this.visible = false })
      .finally(() => { this.$refs.registerModal.changeOkLoading(false) })
  },
  handleCancel() { this.visible = false }
}
```

### 3.2 提交按钮 loading（防连点，必做）

`changeOkLoading(true/false)` 控制确定按钮 loading；也可直接传 prop `:confirm-loading="loading"`。

### 3.3 底部扩展按钮位

```vue
<kunkka-modal :visible.sync="visible" title="使用决策" width="1024px" @ok="handleOk">
  <!-- 取消前面 -->
  <template #insertFooter><el-button plain @click="...">草稿</el-button></template>
  <!-- 取消与确定中间 -->
  <template #centerFooter><el-button plain @click="...">发送</el-button></template>
  <!-- 确定后面 -->
  <template #appendFooter><el-button plain @click="...">打印</el-button></template>
  <!-- 整个底部全重写（覆盖取消/确定） -->
  <!-- <template #footer>...</template> -->
  <kunkka-form ref="kunkka-form" v-bind="formData" />
</kunkka-modal>
```

> 资源按钮 `cSubArea` 与插槽一一对应（`insertFooter` / `centerFooter` / `appendFooter` / `footer`），渲染方式见 [form-modal.md §3.4](../modules/form-modal.md)。

## 4. API

### 4.1 Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `visible` | `boolean` | `false` | 是否可见（**必须 `.sync`**） |
| `title` | `string` | - | 标题 |
| `width` | `string` | - | 宽度（如 `"960px"` / `"1200px"`） |
| `appendToBody` | `boolean` | `true` | 挂 body |
| `fullscreen` | `boolean` | `null` | 全屏态（`.sync`） |
| `canFullscreen` | `boolean` | `true` | 显示全屏按钮 |
| `canMinimize` | `boolean` | `true` | 显示最小化按钮 |
| `draggable` | `boolean` | `true` | 标题栏拖拽（内置指令） |
| `showOkBtn` / `showCancelBtn` | `boolean` | `true` | 确定 / 取消按钮（详情弹窗 `:show-ok-btn="false"`） |
| `okText` / `cancelText` | `string` | i18n | 按钮文字 |
| `confirmLoading` | `boolean` | `false` | 确定 loading（与 `changeOkLoading` 等效） |
| `showOnlyRequired` | `boolean` | `false` | 只看必填项开关（emit `onlyRequired`） |
| `height` / `modalHeaderHeight` / `modalFooterHeight` | - | `null` / `40` / `49` | 高度控制（内容区需要定高时用 `height`） |
| `size` | `string` | `'mini'` | 尺寸 |

> 其余透传 `el-dialog`（`top` / `z-index` / `modal` …）；组件**强制** `close-on-click-modal: false`、zIndex 1001，可用 prop 覆盖前者。

### 4.2 Events

| Event | Parameters | Description |
|-------|------------|-------------|
| `ok` | `e` | 确定按钮点击 |
| `cancel` | `e` | 取消按钮点击 |
| `visible-change` | `bool` | 可见性变化 |
| `onlyRequired` | `bool` | 只看必填项开关变化 |
| `register` | `{instance}` | created 即发（拿实例） |
| `update:visible` / `update:fullscreen` | `bool` | .sync 更新 |

### 4.3 Methods（`this.$refs.registerModal`）

| Method | Description |
|--------|-------------|
| `changeOkLoading(bool)` | 确定按钮 loading 开关（提交防连点标准写法） |
| `setModalProps(props)` | 运行期合并 props |
| `closeModal()` | 关闭 |
| `handleFullScreen()` | 切全屏 |

### 4.4 Slots

| Slot | Description |
|------|-------------|
| 默认 | 弹窗主体 |
| `footer` | 整个底部重写 |
| `insertFooter` / `centerFooter` / `appendFooter` | 底部插入位（取消前 / 中间 / 确定后） |

## 6. 注意事项 / FAQ

- **`:visible.sync` 必须带 `.sync`**：组件靠 `update:visible` 关窗，漏了就是「能打开、确定/取消关不掉」。
- **打开走 `onDataReceive` 约定**：子组件自持 `visible`，父组件 `$refs` 调方法打开；不要用 props 透传开关（时序与回显都难控）。
- **异步提交必做 loading**：`@ok` 里 `changeOkLoading(true)` → `.finally(changeOkLoading(false))`。
- **宽弹窗惯例**：表单弹窗 `width="960px"`，带明细表格 `width="1200px"` + `top="50px"`，需要时 `:can-fullscreen="true"`。
- **遮罩点击**：默认已禁用（`close-on-click-modal: false`），别打开它以免误关填了一半的表单。
- **ref 惯例名**：`registerModal`（模板全家都这么写，`changeOkLoading` 调用处保持一致）。

## 7. 关联资源

- **相关组件**：[KunkkaForm.md](KunkkaForm.md)（表单弹窗内含物）、[CommonTable.md](CommonTable.md)（明细表格弹窗内含物）、importDialog / exportDialog（内部也用它）
- **标准模板**：[form-modal](../modules/form-modal.md) / [table-modal](../modules/table-modal.md)
- **真实代码**：[src/template/formDialogTemplate.vue](../../../../../src/template/formDialogTemplate.vue)（官方模板）
