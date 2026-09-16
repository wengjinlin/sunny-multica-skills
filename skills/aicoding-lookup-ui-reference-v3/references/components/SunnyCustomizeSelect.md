# SunnyCustomizeSelect 自定义选择

> 带附加参数筛选的下拉选择组件：通过 `cNum` 加载选项，再用 `attrParam` 传额外筛选条件，适合「选项依赖其他字段」的级联下拉。返回**标量值**（普通 select 形态，非对象数组）。
>
> 来源库：`@sunny-base-web/ui` ｜ 分类：Composite / 复合 ｜ API 已对照组件源码 `packages/@ui/src/composite/customize-select/CustomizeSelect.vue` 核对（2026-08-14）

## 1. 何时使用

- 选项需要带附加参数筛选（如「按工厂筛项目」「按部门筛用户」）
- 级联下拉：A 字段变化 → B 字段的选项重新加载
- 选项来自后端动态配置（`cNum`），且筛选条件随业务上下文变化

不适用：

- 固定字典选项 → 用 `Select` + `selectOptions.dictCode`（更简单）
- 弹窗选择业务实体（用户/角色/物料）→ 用 `SunnyBusinessSearch`（弹窗 + 对象数组）

### 与 SunnyBusinessSearch 的区别

| 维度 | SunnyCustomizeSelect | SunnyBusinessSearch |
|------|----------------------|---------------------|
| 形态 | 下拉框 | 弹窗（点开搜索） |
| 字段映射 | `fieldNames: { label, value }` | `fieldNames: { label, value, desc }` |
| 附加筛选 | `attrParam`（随上下文变） | `defaultModel` / 弹窗内搜索 |
| 返回值 | **标量**（value 字段） | **对象数组** |
| objectToValueFields | 不需要 | **必须配** |

## 2. 导入

```typescript
import { SunnyCustomizeSelect } from '@sunny-base-web/ui';
import { markRaw } from 'vue';
const CustomizeSelect = markRaw(SunnyCustomizeSelect); // 组件用 markRaw
```

## 3. 代码演示

> 作为表单字段使用时，配置在 `config.ts` 的 `FormSchema` 里，`component: CustomizeSelect`。

### 3.1 基础用法（静态 attrParam）

`cNum` 加载选项，`fieldNames` 映射字段，`attrParam` 传固定筛选条件：

```typescript
{
  fieldName: 'cProject',
  label: '项目名称',
  component: CustomizeSelect,
  componentProps: {
    placeholder: '请选择项目名称',
    allowClear: true,
    cNum: 'CommonAuthDictAttr',                  // 业务编码（必填）
    fieldNames: { label: 'cName', value: 'cXuhao' }, // 字段映射
    attrParam: {                                 // 附加筛选参数（静态）
      xuhao: 'JYRW_XM',
      attrKey: 'FACTORY',
      attrVal: '工厂A',
    },
  },
}
```

### 3.2 级联下拉（动态 attrParam）

`componentProps` 用函数形式，`attrParam` 跟随其他字段变化 —— 字段变化时组件**自动重新查询**选项：

```typescript
{
  fieldName: 'cWtdj',
  label: '问题等级',
  component: CustomizeSelect,
  rules: 'required',
  componentProps: (values: any) => ({
    placeholder: '请选择问题等级',
    allowClear: true,
    cNum: 'CommonAuthDictAttr',
    fieldNames: { label: 'cName', value: 'cXuhao' },
    // 动态筛选：attrVal 随「工厂」字段变化，工厂变 → 选项自动重查
    attrParam: {
      xuhao: 'ZZYC_ZL_WTDJ',
      attrKey: 'FACTORY',
      attrVal: values.cFactory || '',
    },
  }),
}
```

> 也可用解构形式拿表单模型：`componentProps: ({ formModel }) => ({ attrParam: { attrVal: formModel.cFactory } })`。
> 与 `dependencies`（显隐/禁用）可叠加使用，互不冲突。

## 4. API

### 4.1 Props

> 已对照组件源码核对；如有出入以 `packages/@ui/src/composite/customize-select/CustomizeSelect.vue` 为准。

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `cNum` | `string \| number` | `''` | **业务编码（必填）**，据此从后端加载选项列表（如 `'CommonAuthDictAttr'` / `'UserSearch1'`） |
| `fieldNames` | `{ label: string; value: string }` | 内置默认 | 字段映射：选项的显示文本字段与取值字段（注意叫 `fieldNames`，与 `SunnyBusinessSearch` 同名但无 `desc`） |
| `attrParam` | `Record<string, any>` | `{}` | 附加筛选参数，传给后端查询接口；**变化时组件自动重新查询选项** |
| `value` | `string \| number` | `''` | 选中值（标量；组件声明的是 `value` prop，选中变化通过 `update:modelValue` 事件发出） |
| `defaultQuery` | `boolean` | `true` | 挂载时是否自动查询选项（设 `false` 可等 `attrParam` 就绪再查） |
| `defaultConfig` | `{ nType?; cLabelslotcol?; nSearchinterval? }` | `{}` | 查询配置（类型 / label 插槽列 / 搜索间隔） |
| `placeholder` | `string` | `'请选择'` | 占位符 |
| `allowClear` | `boolean` | - | 是否可清除 |
| `disabled` | `boolean` | - | 是否禁用（也常通过 `dependencies.disabled` 控制） |

> `componentProps` 既可是静态对象，也可是函数 `(values, formApi?) => object` 或 `({ formModel }) => object`，用于动态 `attrParam`。

### 4.2 Events

| Event | Parameters | Description |
|-------|------------|-------------|
| `update:modelValue` | `(value: string \| number)` | 选中值变化（表单回写主通道） |
| `selectChange` | `(value, instance)` | 选中变化（带 select 实例） |
| `change` | `({ value, $this })` | 选中变化（带原始实例对象） |

## 5. 类型定义

```typescript
// 字段映射（与 SunnyBusinessSearch 同名，但只有 label/value，无 desc）
interface FieldNames {
  label: string; // 选项显示文本对应的后端字段
  value: string; // 选项取值对应的后端字段
}

// 附加筛选参数：任意键值对，传给后端查询接口
type AttrParam = Record<string, any>;
```

## 6. 注意事项 / FAQ

- **字段映射就是 `fieldNames`（已对照组件源码核实）** —— 与 `SunnyBusinessSearch` 同名、写法一致，但只有 `label` / `value` 两个键、没有 `desc`；不存在 `fieldConfig` 这个 prop，写错会导致选项显示/取值错乱。
- **返回标量值，不需要 `objectToValueFields`** —— 这点与 `SunnyBusinessSearch`（对象数组）相反，别误配。
- **`attrParam` 变化会自动重新查询** —— 做级联下拉时，把依赖字段放进 `attrParam`，用函数式 `componentProps` 让它随表单值变化即可，无需手写 `watch`。
- **`componentProps` 用函数形式才能动态** —— 静态 `attrParam` 用对象；依赖其他字段的 `attrParam` 必须用函数 `(values) => ({ attrParam: {...} })`。
- **组件用 `markRaw` 标记**，避免被 Vue 转成响应式。
- **选型边界**：固定字典 → `Select` + `dictCode`；动态参数下拉 → 本组件；弹窗选业务实体 → `SunnyBusinessSearch`。

## 7. 关联资源

- **相关组件**：`SunnyBusinessSearch`（弹窗选择，常拿来对比）、`SunnyForm` / `useForm`（宿主表单）、`Select`（固定字典下拉）
- **标准模块**：[form-modal](../modules/form-modal.md)（`config.ts` 静态/动态 `attrParam` 写法）
- **组件源码**：`packages/@ui/src/composite/customize-select/CustomizeSelect.vue`（API 有出入时以此为准）
