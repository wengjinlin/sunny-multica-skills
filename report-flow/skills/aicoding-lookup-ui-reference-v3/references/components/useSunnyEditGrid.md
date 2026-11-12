# useSunnyEditGrid 可编辑表格（组件级）

> 组件级可编辑表格 Hook：返回 `[Grid, api]`，基于 vxe-table，内置单元格编辑、鼠标区域选取、复制/剪切/粘贴、查找/替换、撤销等能力；并按列配置自动做「对象数组 ↔ 字符串」互转。适合明细编辑、批量录入、表格内业务搜索等场景。
>
> 来源库：`@sunny-base-web/ui` ｜ 分类：Data Display / 数据展示 ｜ 实现来自组件库源码 `packages/@ui/src/data/edit-grid`（权威）

## 1. 何时使用

- 弹窗 / 分区内的可编辑表格（明细编辑、批量录入）
- 表格内含业务搜索列、字典下拉列、数字/日期列
- 需要复制粘贴、查找替换、撤销等表格编辑操作

不适用：

- **整页查询列表**（只读 + 搜索栏 + 查询方案）→ 用 `useList`
- **只读可查询表格**（无编辑）→ 用 `useSunnyQueryGrid`
- **表单**（字段式录入）→ 用 `SunnyForm`

> 本 Hook 是 `useTable`（+ 字典自动加载）/ `useFormTable` 的底层依赖；业务做表格弹窗时通常用上层 `useTable`，只有在「组件级」需要一块独立可编辑表格、且自行管理字典/数据时才直接使用。

## 2. 导入

```typescript
import { useSunnyEditGrid, EditRender } from '@sunny-base-web/ui';
```

## 3. 代码演示

### 3.1 基础用法（可编辑列 + 校验）

`gridOptions.columns` 里用 `...EditRender.XxxRender` 声明每列的编辑控件，`editRules` 配校验：

```typescript
import { reactive } from 'vue';
import { useSunnyEditGrid, EditRender } from '@sunny-base-web/ui';

const gridOptions = reactive({
  id: 'demoEditGrid',
  border: true,
  height: 400,
  columns: [
    { type: 'checkbox', width: 50 },
    { type: 'seq', title: '序号', width: 60 },
    { field: 'cName', title: '名称', minWidth: 150, ...EditRender.InputRender },
    { field: 'nQty', title: '数量', width: 100, ...EditRender.InputNumberRender, params: { min: 0 } },
    { field: 'cRemark', title: '备注', minWidth: 150, ...EditRender.TextareaRender },
  ],
  editRules: {
    cName: [{ required: true, message: '名称不能为空' }],
  },
});

const [Grid, gridApi] = useSunnyEditGrid({ gridOptions, gridEvents: {} });
```

```vue
<template>
  <Grid />
</template>
```

> 单元格编辑模式内置为 `{ mode: 'cell', trigger: 'click' }`（点击即编辑），无需手动配 `editConfig`。

### 3.2 新增 / 删除 / 校验 / 取数

编辑表格一般不配服务端 `proxyConfig`，手动 `reloadData` 加载、`getFullData` 取数：

```typescript
// 加载初始数据（字符串会自动转对象数组用于编辑）
await gridApi.reloadData(rows);

// 新增行：index = -1 末尾 / null 第一行；自动进入编辑态
await gridApi.addEvent({}, -1);

// 删除勾选行
await gridApi.deleteSelection();

// 提交前校验（返回 null 表示通过）
const errMap = await gridApi.validate();
if (errMap) return;

// 取全量数据（对象数组自动转回字符串）→ 提交
const data = await gridApi.getFullData();
await saveDetail(data);
```

工具栏「新增行 / 删除行」按钮同样走声明式 `toolbarConfig.buttons`，在 `gridEvents.toolbarButtonClick` 里调上面的 api（按钮配置规则与 `useSunnyQueryGrid` 一致，见该文档）。

### 3.3 业务搜索列 + 字符串自动互转

表格内业务搜索列用 `BusinessSearchRender`，在 `params` 里配 `cNum` / `fieldNames` / `displayField`：

```typescript
{
  field: 'cWlbm',
  title: '物料',
  minWidth: 160,
  ...EditRender.BusinessSearchRender,
  params: {
    cNum: 'COMMON_WL',          // 业务编码（必填）
    multiple: false,
    displayField: 'cWlmc',      // 回填目标字段（存物料名称）
    fieldNames: { label: 'cWlmc', value: 'cWlbm', desc: 'cWlmc' },
  },
}
```

> 列配了 `params.fieldNames` 后，api 会自动做格式互转：
> - `reloadData` 时：后端字符串 → 对象数组（供组件编辑）
> - `getFullData` / `getCheckboxRecords` 时：对象数组 → 字符串，并回写 `displayField`
>
> 即「后端存字符串、表格编辑用对象」，调用方无需手动 `toStorageString` / `fromStorageString`。

### 3.4 操作列（行内删除 / 编辑按钮）

列声明用 `slots.default` 指向插槽名，按钮写在 `<Grid>` 的具名插槽里，点击**直接调父组件函数**（行级按钮不走 `gridEvents`——那是表格级事件）：

```typescript
// config.ts — 列声明（操作列不要配 EditRender，它不是编辑列）
{ field: 'action', title: '操作', width: 80, fixed: 'right', slots: { default: 'actionSlot' } }
```

```vue
<Grid>
  <template #actionSlot="{ row }">
    <button class="text-[rgb(var(--primary-6))] hover:text-[rgb(var(--primary-5))] mr-2"
            @click="handleDeleteRow(row)">删除</button>
  </template>
</Grid>
```

```typescript
// 删除指定行：vxe 原生 remove（gridApi.deleteSelection 内部同款）
async function handleDeleteRow(row: any) {
  await gridApi.$grid?.remove(row); // useTable 的 Proxy 下可直接 gridApi.remove(row)
}
```

> **通用性**：`useSunnyEditGrid` / `useTable` / `useFormTable` / `useList`（query-grid）返回的 Grid 都透传插槽，同一写法通用。按模式显隐按钮用 `v-if` 或先过滤（如 `filterColumnHandle(row)`）。
> **真实用例**：`packages/@effects/src/views/setting/dsrw/jobgroup/`（config.ts 列声明 + JobGroupQuery.vue 插槽渲染）。

### 3.5 区域选择与复制粘贴（edit-grid 内置，2026-08-24 恢复）

区域选择（extend-cell-area 插件）已在**可编辑表格**侧恢复启用，与单击编辑共存（vxe 按「有无拖动位移」区分意图）：

| 操作 | 效果 |
|------|------|
| **单击**单元格 | 直接进入编辑 + **自动聚焦输入框**（文本类编辑器挂载即 focus，无需再点一次） |
| **按住拖动** | 区域选择（拖蓝一片，列头/行头显示选中状态） |
| 拖蓝后 Ctrl+C → 点目标格 Ctrl+V | 区域复制粘贴（**不可编辑列自动跳过**，下拉列按 label↔value 匹配） |
| Ctrl+X | 区域剪切（可编辑列清空） |
| 拖动选中区域**右下角填充柄** | 拖动复制（`extendByCopy`，可编辑列生效） |

参与规则（**列配置无需任何新增项**）：
- 配了 `EditRender.*` 的列 → 可编辑，参与粘贴 / 剪切 / 拖动填充
- 纯展示列（SpanRender / 无 EditRender）→ 可被拖蓝选中，复制粘贴自动跳过
- 插件开关与参数（`mouseConfig.area` / `areaConfig` / `clipConfig`）全部在库层注入，业务侧零配置

> ⚠️ **只有可编辑表格（edit-grid / useTable / useFormTable）有此能力**；查询表格（`useSunnyQueryGrid` / `useList`）侧插件仍停用——查询页没有区域选择，且两边共用配置 helper 已按 grid 区分，不会互相影响。
>
> **编辑触发保持 `click`**（单击直编）。若业务改成 `dblclick`，文本类编辑器仍会自动聚焦。

### 3.6 组合筛选（edit-grid 侧 filters-combination）

组合筛选渲染器已在**可编辑表格**侧注册。**规范：生成列配置时，数据列默认统一配 `FilterCombination`（完整条件结构：多选 + 搜索 + 大于/小于/区间/日期前后组合）**（checkbox / seq / 操作列不配）；筛选为前端本地过滤，明确不需要筛选的列可去掉。

```typescript
/** 组合筛选默认项（工厂函数——每列独立 data，避免共享引用被 vxe 原地修改） */
const combinationFilter = () =>
  [{ data: { checks: [], sVal: '', sMenu: '', fType1: '', fVal1: '', fMode: 'and', fType2: '', fVal2: '' } }];

// 数据列默认写法（所有类型列统一 FilterCombination）
{
  field: 'nQty', title: '数量',
  filters: combinationFilter(),
  filterRender: { name: 'FilterCombination' },
}
```

> `FilterAggregation` 是简化备选（仅多选 + 搜索，data 为 `{ checks, sVal }`），一般不默认使用。

> ⚠️ 渲染器名**两边不通用**：可编辑表格用 `FilterAggregation` / `FilterCombination`；查询表格（query-grid）侧的 `MyFilterComplex` / `FilterSimpleInput` / `FilterComplexInput` **未注册**（插件停用中），查询页列筛选当前不可用——不要在查询页列上配 `filterRender`。
>
> 透视表插件（extend-pivot-table）虽已 import，但属商业付费件（无公开文档、d.ts 空壳），**不建议使用**。

## 4. API

> 本节按 Hook 的「入参 → 返回 → api 方法 → EditRender → 插槽」组织。

### 4.1 入参 Options

```typescript
useSunnyEditGrid(options: { gridOptions?: GridOptions; gridEvents?: GridEvents }): [Grid, api]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `gridOptions` | `object`（vxe-grid 配置） | 表格配置，见下表 |
| `gridEvents` | `Record<string, Function>` | 事件处理对象，内部转 `onXxx` 挂到 Grid |

**`gridOptions` 常用子项**：

| 子项 | 说明 |
|------|------|
| `id` | Grid 标识（列自定义持久化 key） |
| `columns` | 列配置；可编辑列用 `...EditRender.XxxRender` 声明，业务搜索/字典列在 `params` 里配 `cNum` / `fieldNames` / `displayField` |
| `editRules` | 校验规则：`{ [field]: [{ required, message }] }`，由 `api.validate()` 触发 |
| `checkboxConfig` | 勾选配置（删行依赖勾选） |
| `toolbarConfig` | 工具栏：`{ buttons: [{ code, name, icon }], ... }`，与 `gridEvents.toolbarButtonClick` 的 `code` 对应 |
| `height` / `border` / `stripe` / `size` | 其他 vxe 标准属性 |

> 编辑模式（`editConfig: { mode: 'cell', trigger: 'click' }`）、剪贴板（`clipConfig`）、查找替换（`fnrConfig`）、鼠标区域选取、键盘导航等均由 Hook 内置注入，无需手动配。

### 4.2 返回值

```typescript
const [Grid, api] = useSunnyEditGrid(options);
```

| 返回 | 类型 | 说明 |
|------|------|------|
| `Grid` | `Component` | 渲染组件，`<Grid />` 直接用；已内置编辑/剪贴板/查找替换/区域选取/平板适配 |
| `api` | `VxeGridApi` | 命令式 API（见 4.3） |

### 4.3 api 方法（VxeGridApi）

| Method | Signature | Description |
|--------|-----------|-------------|
| `reloadData` | `(data: any[]) => Promise<void>` | 加载数据；按列 `fieldNames` 自动把字符串转对象数组 |
| `getFullData` | `() => Promise<any[]>` | 取全量表体数据；自动把对象数组转回字符串 + 回写 `displayField` |
| `getCheckboxRecords` | `() => Promise<any[]>` | 取勾选行（同样自动转字符串） |
| `addEvent` | `(record?, index?) => Promise<void>` | 插入行并进入编辑态；`index = -1` 末尾、`null` 第一行 |
| `deleteSelection` | `() => Promise<void>` | 删除当前勾选行 |
| `validate` | `(full = true) => Promise<null \| ErrMap>` | 校验表格；返回 `null` 表示通过 |
| `$grid` | `→ VxeGridInstance` | 原始 vxe-table 实例，可调任何 vxe 方法 |

### 4.4 EditRender 渲染器

用展开运算符注入列，声明该列的编辑控件：

| 渲染器 | 用途 |
|--------|------|
| `...EditRender.InputRender` | 文本输入 |
| `...EditRender.InputNumberRender` | 数字输入（`params: { min, max, precision }`） |
| `...EditRender.SelectRender` | 下拉选择（配 `selectOptions.dictCode` 走字典） |
| `...EditRender.DatePickerRender` | 日期选择 |
| `...EditRender.TextareaRender` | 多行文本 |
| `...EditRender.SwitchRender` | 开关 |
| `...EditRender.BusinessSearchRender` | 表格内业务搜索（`params: { cNum, fieldNames, displayField, multiple }`） |

> 也兼容 vxe 原始写法 `editRender: { name: '$input' }`，但推荐用 `EditRender.*` 标准渲染器。

### 4.5 内置编辑能力（Grid 自带）

| 能力 | 状态 | 说明 |
|------|------|------|
| 单元格编辑 | ✅ 默认开启 | **单击**直接进入编辑（cell + click），与区域选择共存（见 §3.5） |
| 编辑自动聚焦 | ✅ 内置 | 文本类编辑器（Input / InputNumber / Textarea / 区间第一个框）激活即自动 focus，双击/单击进入编辑后可直接输入 |
| 复制/剪切/粘贴 | ✅ 默认开启 | Ctrl+C / X / V（vxe 核心能力 + `clipConfig`），自动跳过不可编辑或禁用的列，下拉列粘贴按 label↔value 匹配 |
| 查找/替换 | ✅ 默认开启（桌面端） | Ctrl+F / Ctrl+H（`fnrConfig` 内置注入） |
| 撤销 | ✅ 默认开启 | Ctrl+Z |
| 键盘导航 | ✅ 默认开启 | Tab / 方向键 / Shift+方向键；Ctrl+A 全选 |
| 鼠标区域选取（拖蓝一片 / 拖动填充复制） | ✅ edit-grid 已恢复（2026-08-24） | 见 §3.5；**仅可编辑表格**，查询表格（query-grid / useList）侧插件停用中 |
| 组合筛选 | ✅ edit-grid 可用 | **数据列默认统一配 `FilterCombination`**（完整条件结构，见 §3.6）；`FilterAggregation` 为简化备选 |
| 透视表 | ⛔ 不建议 | 商业付费插件（无公开文档），已 import 但不要用 |

## 5. 类型定义

```typescript
function useSunnyEditGrid(options: {
  gridOptions?: Record<string, any>;
  gridEvents?: Record<string, Function>;
}): readonly [Component, VxeGridApi];

// 业务搜索列参数（驱动对象数组↔字符串自动互转）
interface BusinessSearchColumnParams {
  cNum: string;               // 业务编码（必填）
  multiple?: boolean;
  fieldNames?: { label: string; value: string; desc?: string }; // 触发自动互转
  displayField?: string;       // 互转时回写的显示字段
}
```

## 6. 注意事项 / FAQ

- **层级别混用**：表格弹窗场景用 `useTable`（封装本 Hook + 字典自动加载，`example` 见 table-modal 模式）；表单 + 表格组合用 `useFormTable`；只有「一块独立可编辑表格、自行管理数据/字典」才直接用本 Hook。
- **对象数组 ↔ 字符串自动互转**：列配了 `params.fieldNames` 后，`reloadData` / `getFullData` / `getCheckboxRecords` 会自动转换，**不要**再手动 `toStorageString` / `fromStorageString`，否则双重转换出错。
- **editConfig 默认 `{ mode: 'cell', trigger: 'click' }`**：由 Hook 内置注入，但允许在 `gridOptions.editConfig` 覆盖（用户配置展开在默认值之后，优先级更高）。运行期控制可编辑性的标准做法：覆盖为 `{ mode, trigger, beforeEditMethod: () => editableRef.value }`（vxe 在编辑激活前调用，返回 `false` 拒绝）——`useTable` / `useFormTable` 的 `editable` / `tableEditable` 与 `setEditable` 即基于此实现。
- **可编辑列用 `EditRender.*` 声明**，不要用 vxe 原始 `editRender: { name: '$input' }`（除非有特殊需求）。
- **工具栏按钮统一走 `toolbarConfig.buttons`**，禁止自己写 `<div>` + 按钮拼工具栏（同 `useSunnyQueryGrid` 规则）。
- **校验**用 `api.validate()`，配合 `gridOptions.editRules`；返回非 `null` 即有错，不要提交。
- **新增行用 `addEvent(record, -1)`**：会自动 `insertAt` 并 `setEditRow` 进入编辑态，不要自己调 vxe 的 insert。

## 7. 关联资源

- **上层封装**：`useTable`（表格弹窗，+ 字典自动加载）、`useFormTable`（表单 + 表格）—— 均在 `@sunny-base-web/effects`，内部调本 Hook
- **同级**：`useSunnyQueryGrid`（只读查询表格）、`EditRender` / `Validators` / `createEditableClipConfig`（本目录导出的编辑渲染/校验/剪贴板工具）
- **标准模块**：[table-modal](../modules/table-modal.md)（`useTable` 可编辑弹窗，含 `EditRender` 各渲染器写法）、[form-table-modal](../modules/form-table-modal.md)（`useFormTable`）
