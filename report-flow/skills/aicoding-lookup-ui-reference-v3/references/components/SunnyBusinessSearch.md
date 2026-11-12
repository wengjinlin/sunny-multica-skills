# SunnyBusinessSearch 业务搜索

> 业务搜索选择组件：通过 `cNum`（业务编码）从后端自动加载搜索表单 + 表格列 + 弹窗配置，弹窗选择用户 / 角色 / 物料 / 设备等业务数据。是项目里「从系统已有数据里挑一条/几条」场景的**强制组件**。
>
> 来源库：`@sunny-base-web/ui`（组件）+ `@sunny-base-web/effects`（`useBusinessSearchModal`）｜ 分类：Composite / 复合 ｜ API 提取自 `docs/src/public/llms-full.txt`（2026-04-10）

## 1. 何时使用

- 表单字段：挑选用户 / 角色 / 部门 / 物料 / 设备等业务实体（内嵌式）
- 搜索栏条件：作为查询条件的选择项
- 独立按钮：工具栏或自定义按钮点击后弹窗选择（独立调用式）

不适用：

- 固定少量选项 → 用 `Select` + `selectOptions.dictCode`
- 自定义带附加参数的下拉 → 用 `SunnyCustomizeSelect`

> ⚠️ 组件返回的是**对象数组**，在表单中使用必须配 `objectToValueFields`，否则回显异常（见第 6 节）。

## 2. 导入

```typescript
import { SunnyBusinessSearch } from '@sunny-base-web/ui';
import { useBusinessSearchModal } from '@sunny-base-web/effects'; // 独立调用式
```

## 3. 代码演示

### 3.1 表单字段内嵌（最常见）

作为 `FormSchema` 的 `component` 配置在 `config.ts`，由 `useForm` 渲染。**必须**配 `objectToValueFields`：

```typescript
// config.ts
import type { FormSchema } from '@sunny-base-web/ui';
import { markRaw } from 'vue';
import { SunnyBusinessSearch } from '@sunny-base-web/ui';

const BusinessSearch = markRaw(SunnyBusinessSearch); // 组件用 markRaw

export const addFormSchema: FormSchema[] = [
  {
    fieldName: 'roleValue',
    label: '角色选择',
    component: BusinessSearch,
    componentProps: {
      cNum: 'XTGL_USER_ROLE',        // 业务编码（必填）
      placeholder: '请选择角色',
      modalProps: {
        multiple: false,             // 单选
        fieldNames: { label: 'C_ROLENAME', value: 'ID', desc: 'C_ROLENUMB' },
      },
    },
  },
];
```

```typescript
// useForm 必须告知该字段存的是对象
const [FormComponent, formApi] = useForm({
  schema: addFormSchema,
  objectToValueFields: ['roleValue'], // ← 不配会导致回显变成序列化字符串
});
```

> `query-list` 的 `searchFormSchema` 中用法完全相同。

### 3.2 联动赋值（选完自动填其他字段）

`componentProps` 用函数形式拿到 `formApi`，在 `onChange` 里给别的字段赋值：

```typescript
{
  fieldName: 'roleValue',
  component: BusinessSearch,
  componentProps: (_values, formApi) => ({
    cNum: 'XTGL_USER_ROLE',
    modalProps: { multiple: false, fieldNames: { label: 'C_ROLENAME', value: 'ID' } },
    onChange: (values: any[]) => {
      // 选中角色后，把角色编号回填到备注字段
      formApi.setFieldValue('cRemark', values[0]?.C_ROLENUMB ?? '');
    },
  }),
}
```

### 3.3 独立调用（非表单场景，useBusinessSearchModal）

不在表单里、需按钮 / 工具栏点击弹窗选择时，用 `useBusinessSearchModal`。**调用方负责渲染 `SunnySearchModal`**（hook 只返回 `visible` + `modalProps`，不返回组件）：

```vue
<script setup lang="ts">
import { useBusinessSearchModal } from '@sunny-base-web/effects';
import { SunnySearchModal } from '@sunny-base-web/ui';

defineOptions({ name: 'DemoQuery' });

const { visible, modalProps, open, selectedValues } = useBusinessSearchModal({
  cNum: 'IQC_MATERIAL',
  multiple: true,
  fieldNames: { label: 'C_MATERIAL_NAME', value: 'ID' },
  onConfirm: (rows) => { console.log('选中的物料：', rows); }, // 对象数组
});
</script>

<template>
  <a-button @click="open">选择物料</a-button>
  <SunnySearchModal v-model:visible="visible" v-bind="modalProps" />
</template>
```

**query-list 工具栏触发**：在 `gridEvents.toolbarButtonClick` 里调 `open()`，选中后经 `onConfirm` 拿数据：

```typescript
const searchModal = useBusinessSearchModal({
  cNum: 'IQC_MATERIAL', multiple: true,
  onConfirm: (rows) => handleSelected(rows),
});

const gridEvents = {
  toolbarButtonClick(params: any) {
    if (params.button.code === 'selectMaterial') searchModal.open();
  },
};
// 模板里仍需渲染 <SunnySearchModal v-model:visible="searchModal.visible" v-bind="searchModal.modalProps" />
```

**预设选中值（编辑回显）**：打开前调 `setSelectedValues`：

```typescript
function handleEdit(record: any) {
  searchModal.setSelectedValues(record.selectedItems); // 预设已选
  searchModal.open();
}
```

> `useBusinessSearchModal` 的完整 Options / 返回值见 §4.5。

## 4. API

### 4.1 Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `cNum` | `string` | - | **动态配置编码（必填）**，如 `'XTGL_USER_ROLE'` / `'IQC_MATERIAL'`；据此从后端加载 formSchema/tableColumns/title/width/multiple |
| `type` | `string` | - | 业务类型（静态预设，如 `'user'`）；提供时优先走静态配置，否则走 `cNum` 动态配置 |
| `modelValue` | `any[] \| null` | - | 双向绑定的选中值（对象数组） |
| `multiple` | `boolean` | `true` | 是否多选 |
| `cSelectionMode` | `string` | - | 选择模式 `'single' \| 'multiple'`，优先级低于 `multiple` |
| `fieldNames` | `{ label?: string; value?: string; desc?: string }` | - | 字段映射。优先级：`props.fieldNames` > `modalProps.fieldNames` > 后端配置 |
| `modalProps` | `Partial<SunnySearchModalProps>` | - | 透传给内部 `SunnySearchModal`（`multiple` / `fieldNames` / `title` / `width` 等） |
| `defaultModel` | `Record<string, any>` | - | 打开弹窗时自动填充到搜索表单的默认值 |
| `maxTagCount` | `number` | - | 输入框最大显示标签数 |
| `placeholder` | `string` | `'请选择'` | 占位符 |
| `disabled` | `boolean` | `false` | 是否禁用 |

### 4.2 Events

| Event | Parameters | Description |
|-------|------------|-------------|
| `update:modelValue` | `values: any[]` | 选中值变化（对象数组） |

> 业务里更常用的是通过 `componentProps.onChange` 拿选中数据做联动（见示例 3.2），而非监听事件。

### 4.5 Hooks

#### `useBusinessSearchModal`（来自 `@sunny-base-web/effects`）— 独立调用式

适用于按钮点击、工具栏等**非表单**场景：

```typescript
const { visible, modalProps, open, selectedValues } = useBusinessSearchModal(options)
```

**Options**

| 属性 | 类型 | 说明 |
|------|------|------|
| `cNum` | `string` | 业务编码（必填） |
| `fieldNames` | `{ label?; value?; desc? }` | 字段映射 |
| `multiple` | `boolean` | 是否多选，默认 `true` |
| `onConfirm` | `(rows: any[]) => void` | 确认选择回调 |

**返回值**

| 属性 | 类型 | 说明 |
|------|------|------|
| `visible` | `Ref<boolean>` | 弹窗显隐 |
| `modalProps` | `ComputedRef` | 合并后传给 `SunnySearchModal` 的属性 |
| `open` | `() => Promise<void>` | 打开弹窗（首次自动加载配置并缓存） |
| `selectedValues` | `ComputedRef<any[]>` | 当前选中值 |
| `setSelectedValues` | `(val: any[]) => void` | 手动预设选中值（编辑回显） |
| `handleConfirm` | `(rows: any[]) => void` | 确认回调 |

#### `useSunnyBusinessSearch`（来自 `@sunny-base-web/ui`）— 低级

组件内部使用的 Hook，业务一般不直接调用。

## 5. 类型定义

```typescript
// 字段映射：把后端字段名映射为 label / value / 第二行描述
interface FieldNames {
  label?: string; // 显示在 Tag / 行里的文本字段
  value?: string; // 选中值的唯一标识字段
  desc?: string;  // 第二行描述文本字段（可选）
}

// useBusinessSearchModal 配置
interface UseBusinessSearchModalOptions {
  cNum: string;
  fieldNames?: FieldNames;
  multiple?: boolean;
  onConfirm?: (rows: any[]) => void;
}
```

## 6. 注意事项 / FAQ

- **对象数组 → 必配 `objectToValueFields`**：组件返回对象数组，`useForm` 必须写 `objectToValueFields: ['字段名']`，否则选中对象被序列化成字符串，回显异常。这是最高频踩坑点。
- **`cNum` 必填**：业务编码对应后端 `/core/assDialog/openInit` 配置，据此自动加载搜索表单 + 表格列 + 弹窗属性；首次加载后缓存。
- **`fieldNames` 优先级**：`props.fieldNames` > `modalProps.fieldNames` > 后端配置默认值；不配则用后端返回。
- **联动赋值**用 `componentProps` 函数形式 `(_, formApi) => ({ onChange: ... })`，在 `onChange` 里 `formApi.setFieldValue`，别手写 `watch`。
- **组件用 `markRaw` 标记**（`markRaw(SunnyBusinessSearch)`），避免被 Vue 转成响应式。
- **独立场景别用组件**：按钮点击弹窗选数据用 `useBusinessSearchModal`，不要硬塞一个 `SunnyBusinessSearch` 进模板。
- **独立调用需自行渲染 `SunnySearchModal`**：`useBusinessSearchModal` 只返回 `visible` + `modalProps`（不返回组件），调用方必须 `<SunnySearchModal v-model:visible="visible" v-bind="modalProps" />`；`onConfirm` 拿到的是按 `fieldNames` 取值的对象数组。
- **`multiple` 写在 `modalProps` 里**：内嵌式单选/多选由 `modalProps.multiple` 控制（见示例）。
- **全局适配器**：`businessSearchAdapter` 在 `bootstrap.ts` 配置，内嵌式与独立式共享同一套，配置一致。

## 7. 关联资源

- **相关组件**：`SunnySearchModal`（内部使用的搜索弹窗）、`SunnyCustomizeSelect`（自定义带参下拉，更轻量）、`SunnyForm` / `useForm`（内嵌式宿主）
- **标准模块**：[form-modal](../modules/form-modal.md)（表单字段内嵌）、[query-list](../page-patterns/query-list.md)（搜索栏内嵌）；独立调用式见本文 §3.3
