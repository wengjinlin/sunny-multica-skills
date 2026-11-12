# SunnyModal 弹窗

> 模态弹窗组件，基于 Arco Modal 封装，是项目所有弹窗场景的**强制组件**（禁止直接用 Arco `Modal`）。通常作为表单 / 表格 / 详情的外壳，配合父组件的 `visible` 受控开关。
>
> 来源库：`@sunny-base-web/ui` ｜ 分类：Feedback / 反馈 ｜ API 提取自 `docs/src/public/llms-full.txt`（2026-04-10）

## 1. 何时使用

- 新增 / 编辑 / 查看类弹窗（内含表单或表格）
- 明细数据编辑、决策弹窗、附件弹窗等业务交互
- 需要自定义底部按钮（确认 / 取消之外再加按钮）

不适用：

- 轻量操作确认 → 用 `Modal.confirm()` 或 `Message`（不要为此开全量弹窗）
- 侧边滑出 → 用 `Drawer`

## 2. 导入

```typescript
import { Modal } from '@sunny-base-web/ui'; // 注意：来自 ui，不是 @arco-design/web-vue
```

## 3. 代码演示

### 3.1 基础用法

受控开关用 **`:model-value` + `@update:model-value`**（Vue `v-model` 约定，主用法）：

```vue
<script setup lang="ts">
defineOptions({ name: 'DemoAdd' });

const props = defineProps<{ visible: boolean }>();
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void;
  (e: 'success'): void;
}>();

/** 确认（@ok 模式：提交后弹窗自动关闭） */
async function handleOk() {
  // 提交逻辑...
  emit('success');
}

/** 关闭 */
function handleClose() {
  emit('update:visible', false);
}
</script>

<template>
  <Modal
    :model-value="visible"
    title="新增"
    :width="600"
    @ok="handleOk"
    @update:model-value="emit('update:visible', $event)"
    @close="handleClose"
  >
    <!-- 表单 / 表格 / 任意内容 -->
    <p>弹窗内容</p>
  </Modal>
</template>
```

> 父组件用法：`<DemoAdd v-model:visible="addVisible" @success="handleRefresh" />`，在工具栏事件里把 `addVisible.value = true`。
>
> **推荐变体（项目基准 RoleAdd 式）**：子组件自持 `const visible = ref(false)`，通过 `defineExpose({ addInit, editInit })` 暴露打开方法，提交成功后自己 `visible.value = false`——不走 prop 透传，时序最可控。

### 3.2 校验失败不关闭（:on-before-ok）

需要「校验通过才关、失败保留」时用 `:on-before-ok`，返回 `false` 阻止关闭：

```vue
<Modal
  :model-value="visible"
  title="新增"
  :on-before-ok="handleBeforeOk"
  @update:model-value="emit('update:visible', $event)"
>
  <FormComponent />
</Modal>

<script setup lang="ts">
async function handleBeforeOk() {
  const { valid } = await formApi.validate();
  if (!valid) return false;   // 校验失败 → 不关闭
  const values = await formApi.getValues();
  await add(values);
  Message.success('新增成功');
  emit('success');
  return true;                // 返回 true → 关闭弹窗
}
</script>
```

| 模式 | 用法 | 适用 |
|------|------|------|
| 自动关闭 | `@ok="handleOk"` | 提交即关闭 |
| 手动控制 | `:on-before-ok="handleBeforeOk"` | 校验 / 提交失败时不关闭，靠返回值决定 |

### 3.3 自定义底部按钮 + 加载态

`ok-text` / `ok-loading` / `:mask-closable="false"`，并用 `#centerFooter` 插槽在取消与确认之间追加按钮：

```vue
<Modal
  :model-value="visible"
  title="使用决策"
  width="1024px"
  ok-text="保存"
  :ok-loading="saveLoading"
  :mask-closable="false"
  @ok="handleSave"
  @update:model-value="emit('update:visible', $event)"
>
  <Form />

  <!-- 底部居中额外按钮区 -->
  <template #centerFooter>
    <a-button :loading="sendLoading" @click="handleSendS4">发送S4</a-button>
  </template>
</Modal>
```

## 4. API

### 4.1 Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | `boolean` | `false` | 是否可见（**唯一受控入口**，配合 `v-model` / `:model-value` + `@update:model-value`） |
| `title` | `string` | - | 标题 |
| `width` | `string \| number` | - | 宽度（数字 = px，或字符串如 `'1024px'`） |
| `top` | `string \| number` | - | 距顶部距离 |
| `zIndex` | `number` | - | 层级 |
| `helpMessage` | `string` | - | 标题栏帮助提示（问号图标 Tooltip） |
| `closeOnEsc` | `boolean` | - | 是否支持 ESC 关闭 |
| `fullscreen` | `boolean` | - | 是否显示全屏按钮 |
| `closeOnClickModal` | `boolean` | - | 是否点击遮罩关闭（Arco 别名 `mask-closable` 同样透传可用） |
| `okText` / `cancelText` | `string` | - | 确认 / 取消按钮文字 |
| `okLoading` | `boolean` | - | 确认按钮 loading（提交时置 `true`） |
| `hideCancel` | `boolean` | - | 是否隐藏取消按钮 |
| `okButtonProps` / `cancelButtonProps` | `any` | - | 确认 / 取消按钮 props |
| `onBeforeOk` | `(done?) => void \| boolean \| Promise<any>` | - | 确认前回调，返回 `false` 阻止关闭 |
| `onBeforeCancel` | `() => boolean \| Promise<boolean>` | - | 取消前回调 |
| `onVisibleChange` | `(visible: boolean) => void` | - | 可见性变化回调 |
| `onOk` / `onClose` | `() => void` | - | 确认 / 关闭回调（也可用 `@ok` / `@close` 事件形式） |

> 组件基于 Arco Modal 封装，Arco 原生 prop（如 `mask-closable` / `modal-class` / `wrap-style`）透传可用。

### 4.2 Events

| Event | Parameters | Description |
|-------|------------|-------------|
| `update:modelValue` | `value: boolean` | 可见性变化（**唯一**，配合 `v-model` / `:model-value`） |
| `ok` | - | 确认按钮点击 |
| `cancel` | - | 取消按钮点击 |
| `close` | - | 弹窗关闭 |
| `fullscreen-change` | `value: boolean` | 最大化 / 还原切换（点全屏按钮或双击标题栏）。⚠️ 确认/取消**关闭**时组件内部复位最大化但**不发**此事件——同步了本地状态的调用方须在关闭时自行复位 |

> `onOk` / `onClose` 等既可作为 prop（`onOk`）也可作为事件（`@ok`）使用，二者等价。

### 4.4 Slots

| Slot | Description |
|------|-------------|
| 默认插槽 | 弹窗主体内容（表单 / 表格 / 任意） |
| `centerFooter` | 底部居中额外按钮区，插在「取消」与「确认」之间（见示例 3.3） |

### 4.5 Hooks

#### `useSunnyModal`（低级，业务少用）

```typescript
import { useSunnyModal, ModalTypes } from '@sunny-base-web/ui';
const modal = useSunnyModal(options: ModalApiOptions): UseModalReturnType;
```

命令式打开弹窗。**项目业务统一用声明式 `<Modal>` + `visible` prop**，此 Hook 仅在需要动态创建 / 命令式弹窗时使用；`ModalTypes` 为弹窗类型枚举。

## 6. 注意事项 / FAQ

- **`Modal` 必须从 `@sunny-base-web/ui` 导入**，不是 `@arco-design/web-vue`。
- **开关受控（唯一入口）**：只支持 `v-model` / `:model-value` + `@update:model-value`。**不要用 `:visible` / `v-model:visible`**——SunnyModal 没有这个 prop（0.9.23–0.9.24 曾短暂提供过兼容别名，0.9.25 起已移除）。传 `:visible` 会出现「能打开、确定/取消按钮关不掉」：它经 `$attrs` 透传到内层 Arco modal 所以能打开，但关闭只 emit `update:modelValue`。（原生 `<a-modal>` 的 `visible` 用法与 SunnyModal 无关，照常可用。）
- **推荐模式（RoleAdd 式）**：新增/编辑弹窗子组件自持 `visible` ref + `defineExpose` 暴露 `addInit/editInit` 打开方法，提交成功后自己置 `false`，不走 prop 透传。
- **两种提交模式**：`@ok`（提交即自动关闭）vs `:on-before-ok`（靠返回值控制，校验失败返回 `false` 不关闭）。
- **额外按钮**放 `#centerFooter` 插槽，不要自己重写整个 footer。
- **遮罩点击关闭**：Sunny 名 `closeOnClickModal`，Arco 名 `mask-closable`，两者都可用。
- **内容加载态**：弹窗内用 `<a-spin :loading="loading">` 包裹表格等异步内容。
- **弹窗内 Grid / 需要占剩余高度的组件**：弹窗常态**没有确定高度**（由内容撑开、仅 max-height 封顶；body 的 `flex:1 + min-height:0` 只在最大化或内容超限时生效）。根容器纯 `h-full` 链常态断在 body 上，vxe `height:'auto'` 与内容高度互相反馈 → 表格逐轮缩小或无限增高。正解：常态根容器固定高度（如 `h-[520px]`），最大化时用 `@fullscreen-change` 同步状态切回 `h-full` 填满（关闭时 Modal 内部复位最大化不发该事件，须自行复位），详见 [form-table-modal.md](../modules/form-table-modal.md) §3.3/§4。
- **不直接依赖 `requestClient`**：提交走 API 层函数；`requestClient` 已内置全局错误拦截，业务 `catch` 里别再 `Message.error()`。

## 7. 关联资源

- **相关组件**：`SunnyForm`（表单弹窗内含物）、`useSunnyEditGrid` / `useTable`（表格弹窗内含物）、`SunnyImportModal` / `SunnyExportModal` / `SunnySearchModal`（专用弹窗）
- **标准模块**：[form-modal](../modules/form-modal.md) / [table-modal](../modules/table-modal.md) / [form-table-modal](../modules/form-table-modal.md)
- **真实代码**：`packages/@effects/src/views/setting/role/RoleAdd.vue`（RoleAdd 式：子组件自持 visible + `defineExpose`）
