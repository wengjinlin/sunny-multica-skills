# SunnyForm 表单

> 声明式 Schema 驱动的表单组件，封装了栅格布局、字段联动、字典/权限选项加载、查询方案集成等业务逻辑，是项目所有表单场景的**强制组件**（禁止直接用 Arco `Form`）。
>
> 来源库：`@sunny-base-web/ui`（组件）+ `@sunny-base-web/effects`（`useForm` Hook）｜ 分类：Data Entry / 数据录入 ｜ API 提取自 `docs/src/public/llms-full.txt`（2026-04-10）

## 1. 何时使用

- 任何表单场景：查询表单（搜索栏）、新增 / 编辑表单（弹窗内）、独立表单页
- 需要声明式 Schema 配置字段（`searchFormSchema` / `addFormSchema`）
- 需要字段联动（显隐 / 必填 / 禁用 / 联动赋值）、字典或权限下拉、查询方案

不适用：

- 纯展示用 → 用 `Descriptions` / 文本；需要勾选 → 用 `Checkbox` / `SunnyCustomizeSelect`

## 2. 导入

业务代码**不直接写 `<SunnyForm>`**，而是用 `useForm` 拿到表单组件和 API：

```typescript
import { useForm } from '@sunny-base-web/effects';   // 标准 Hook（业务用这个）
import type { FormSchema } from '@sunny-base-web/ui'; // Schema 类型
// SunnyForm / FormApi 一般无需直接导入，仅在需要类型标注或底层定制时引入
```

## 3. 代码演示

### 3.1 基础用法

最小形态：`useForm` + Schema + 渲染组件 + 提交时 `validate` / `getValues`。Schema 集中写在 `config.ts`。

```typescript
// config.ts
import type { FormSchema } from '@sunny-base-web/ui';

export const addFormSchema: FormSchema[] = [
  {
    fieldName: 'cName',
    label: '姓名',
    component: 'Input',
    rules: 'required',
    componentProps: { placeholder: '请输入姓名', allowClear: true },
  },
];
```

```vue
<script setup lang="ts">
import { useForm } from '@sunny-base-web/effects';
import { addFormSchema } from './config';

const [FormComponent, formApi] = useForm({ schema: addFormSchema });

async function handleSubmit() {
  const { valid } = await formApi.validate(); // 校验
  if (!valid) return;
  const values = await formApi.getValues();   // 取值
  // await add(values);
}
</script>

<template>
  <FormComponent />
</template>
```

> 真实场景通常把 `<FormComponent />` 放进 `Modal`，提交走 `@ok` 或 `:on-before-ok`（见 `form-modal` 模式）。

### 3.2 字段联动（dependencies）

通过 `dependencies` 声明式控制字段的显隐 / 必填 / 禁用 / 动态属性，无需手写 `watch`：

```typescript
{
  fieldName: 'cRemark',
  label: '备注',
  component: 'Input',
  dependencies: {
    show:     (values) => values.nZt === '10001', // 条件显隐（v-show）
    required: (values) => values.nZt === '10001', // 动态必填
    disabled: (values) => values.nZt !== '10001', // 动态禁用
    // if:            (values) => true,            // 条件渲染（v-if，DOM 不存在）
    // componentProps:(values) => ({ ... }),        // 动态属性
  },
}
```

| 联动需求 | 配置 |
|---------|------|
| 条件显隐 | `show: (v) => boolean` |
| 条件渲染 | `if: (v) => boolean` |
| 动态必填 | `required: (v) => boolean` |
| 动态禁用 | `disabled: (v) => boolean` |
| 动态属性 | `componentProps: (v) => object` |

### 3.3 字典 / 权限下拉与业务搜索

字典与权限下拉通过 `selectOptionsAdapter` / `permissionOptionsAdapter`（`bootstrap.ts` 全局配置）自动加载，不硬编码 options：

```typescript
import { markRaw } from 'vue';
import { SunnyBusinessSearch } from '@sunny-base-web/ui';
const BusinessSearch = markRaw(SunnyBusinessSearch); // 组件用 markRaw 标记

export const addFormSchema: FormSchema[] = [
  // 字典下拉：dictCode 对应后端字典定义
  {
    fieldName: 'nZt',
    label: '状态',
    component: 'Select',
    selectOptions: { dictCode: 'SFQY' },
  },
  // 权限下拉：code 对应后端权限配置（如公司/部门）
  {
    fieldName: 'cOrg',
    label: '组织机构',
    component: 'Select',
    permissionOptions: { code: 'COMPANY' },
  },
  // 业务搜索：弹窗选择用户/角色/部门等
  {
    fieldName: 'roleValue',
    label: '角色',
    component: BusinessSearch,
    componentProps: {
      cNum: 'XTGL_USER_ROLE',
      modalProps: { multiple: false, fieldNames: { label: 'C_ROLENAME', value: 'ID' } },
    },
  },
];
```

> `SunnyBusinessSearch` 返回的是**对象数组**，`useForm` 必须配 `objectToValueFields`，否则回显会变成序列化字符串：
>
> ```typescript
> const [FormComponent, formApi] = useForm({
>   schema: addFormSchema,
>   objectToValueFields: ['roleValue'], // 告知表单该字段存对象
> });
> ```

### 3.4 联动赋值与编辑回填

**联动赋值**：`componentProps` 用函数形式，第二个参数拿到 `formApi`，在 `onChange` 里给其他字段赋值：

```typescript
{
  fieldName: 'roleValue',
  component: BusinessSearch,
  componentProps: (_values, formApi) => ({
    cNum: 'XTGL_USER_ROLE',
    onChange: (values: any[]) => {
      formApi.setFieldValue('cRemark', values[0]?.C_ROLENUMB ?? '');
    },
  }),
}
```

**编辑回填**：弹窗打开时 `resetForm()` 再 `setValues()`：

```typescript
watch(() => props.visible, async (visible) => {
  if (!visible) return;
  formApi.resetForm();
  if (props.editData) {
    await nextTick();
    formApi.setValues(props.editData); // 默认过滤非 schema 字段
  }
});
```

## 4. API

### 4.1 Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `schema` | `FormSchema[]` | - | 表单 Schema 配置（声明式驱动，最常用） |
| `layout` | `FormLayout` | - | 表单布局 |
| `size` | `'mini' \| 'small' \| 'medium' \| 'large'` | `'small'` | 表单尺寸 |
| `labelWidth` | `number \| string` | - | 标签宽度 |
| `commonConfig` | `Record<string, any>` | - | 表单项通用配置（colProps / labelWidth / componentProps） |
| `gridProps` | `Record<string, any>` | - | 栅格容器配置（传给 a-grid，如 cols / xGap / yGap） |
| `wrapperClass` | `string` | - | 外层容器类名 |
| `values` | `Record<string, any>` | - | 表单值（受控） |
| `showDefaultActions` | `boolean` | - | 是否显示默认提交 / 重置按钮 |
| `submitOnEnter` | `boolean` | - | 是否回车提交 |
| `submitOnChange` | `boolean` | - | 值变化时自动提交（查询表单常用） |
| `handleSubmit` | `(values) => Promise<void> \| void` | - | 提交回调 |
| `handleReset` | `(values) => Promise<void> \| void` | - | 重置回调 |
| `handleValuesChange` | `(values, changedFields) => void` | - | 值变化回调 |
| `scrollToFirstError` | `boolean` | - | 滚动到第一个错误字段 |
| `collapsed` / `showCollapseButton` / `collapsedRows` | `boolean` / `boolean` / `number` | - | 折叠展开（查询表单常用） |
| `compact` | `boolean` | - | 紧凑模式 |
| `actionLayout` | `'inline' \| 'newLine' \| 'rowEnd'` | - | 操作按钮布局 |
| `actionPosition` | `'left' \| 'right' \| 'center'` | - | 操作按钮位置 |
| `fieldMappingTime` | `FieldMappingTime` | - | 字段映射到时间格式 |
| `arrayToStringFields` | `ArrayToStringFields` | - | 数组字段映射为字符串（默认用 `,`） |
| `objectToValueFields` | `string[]` | - | 对象数组字段提取 value（业务搜索回显必备；`useForm` 选项同名） |
| `searchPlanConfig` | `{ enable?: boolean; ... }` | - | 查询方案配置 |

<details>
<summary>栅格响应式 Props（同 Arco GridItem，一般不直接用）</summary>

`span` / `offset` / `push` / `pull` / `order`（`number`）与 `xs` / `sm` / `md` / `lg` / `xl` / `xxl`（`number | object`），用于整表栅格微调。

</details>

### 4.2 Methods / Expose（FormApi）

`useForm` 返回的 `formApi` 提供命令式方法：

| Method | Signature | Description |
|--------|-----------|-------------|
| `validate` | `() => Promise<{ valid: boolean; errors?: any }>` | 校验整表，返回是否通过 |
| `getValues` | `() => Promise<Record<string, any>>` | 获取表单值 |
| `setValues` | `(values, filterFields = true) => void` | 批量设值；`filterFields=false` 可写入 schema 外的上下文字段（供 dependencies 读取） |
| `setFieldValue` | `(field, value) => void` | 设置单个字段值 |
| `resetForm` | `() => void` | 重置表单（清空数据 + 校验状态） |

### 4.3 Hooks

#### `useForm`（来自 `@sunny-base-web/effects`）— 标准用法

```typescript
const [FormComponent, formApi, onlyRequired] = useForm(options): [Component, FormApi, Ref<boolean>]
```

`options`：`{ schema: FormSchema[]; objectToValueFields?: string[]; ... }`。返回 `[表单组件, 表单 API, 只看必填项开关]`，业务代码统一走它，不直接渲染 `<SunnyForm>`。第 3 个返回值 `onlyRequired`（`Ref<boolean>`）直接 v-model 到弹窗底部 checkbox——开关写 `__onlyRequired` 保留上下文字段，非必填字段的 `dependencies.show` 响应隐藏（见 [form-modal.md](../modules/form-modal.md)）。

#### `useSunnyForm` / `provideFormProps`（来自 `@sunny-base-web/ui`）— 低级

底层实现，业务一般不直接调用。

## 5. 类型定义

```typescript
interface FormSchema {
  fieldName: string;                              // 字段名（对齐后端字段）
  label: string;                                  // 标签
  component: string | Component;                  // 'Input' | 'Select' | 'InputNumber' | markRaw(Component)
  componentProps?: object | ((values, formApi) => object); // 静态对象 或 函数（可访问 formApi）
  rules?: 'required' | ValidationRule;            // 校验规则
  selectOptions?: { dictCode: string; fieldMapping?: FieldNames };  // 字典下拉
  permissionOptions?: { code: string; fieldMapping?: FieldNames };  // 权限下拉
  dependencies?: {                                // 字段联动
    show?: (values) => boolean;
    if?: (values) => boolean;
    required?: (values) => boolean;
    disabled?: (values) => boolean;
    componentProps?: (values) => object;
    rules?: (values) => ValidationRule;
  };
  colProps?: { span?: number; [key: string]: any }; // 栅格
  defaultValue?: any;
}
```

## 6. 注意事项 / FAQ

- **`useForm` 来自 `@sunny-base-web/effects`**，不是 `@sunny-base-web/ui`；`Modal` 来自 `@sunny-base-web/ui`，不是 `@arco-design/web-vue`。
- **`SunnyBusinessSearch` 字段必须配 `objectToValueFields`**，否则选中对象会被序列化成字符串，回显异常。
- **联动回调用 `componentProps` 函数形式** `(_, formApi) => ({ onChange: ... })`，在 `onChange` 里 `formApi.setFieldValue` 联动赋值，别手写 `watch`。
- **跨字段上下文**：`setValues(data, false)` 可写入 schema 外的字段供 `dependencies` 读取；建议用 `__` 前缀命名避免冲突，`resetForm()` 后需重新写入。
- **Schema 放 `config.ts`**，不要写在 `.vue` 里；与 `searchFormSchema` / `tableColumns` 集中管理。
- **组件用 `markRaw` 标记**（如 `markRaw(SunnyBusinessSearch)`），避免 Vue 把组件转成响应式对象。
- **不直接依赖 `requestClient`**：表单只负责数据收集，提交走 API 层函数；`requestClient` 已内置全局错误拦截，业务 `catch` 里别再 `Message.error()`。

## 7. 关联资源

- **相关组件**：`SunnyModal`（表单弹窗外壳）、`SunnyBusinessSearch`（业务搜索字段）、`SunnyCustomizeSelect`（自定义选择字段）
- **标准模板**：[form-modal](../modules/form-modal.md)（新增 / 编辑弹窗表单）、[query-list](../page-patterns/query-list.md)（查询表单 `searchFormSchema`）
- **真实代码**：`packages/@effects/src/views/setting/role/RoleAdd.vue`
