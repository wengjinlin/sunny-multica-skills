# useSunnyQueryGrid 查询表格（组件级）

> 组件级可查询表格 Hook：返回一个 `[Grid, api]` 元组，Grid 是基于 vxe-table 的可分页/排序/服务端查询表格，可直接嵌进弹窗、分区等任意位置。是项目「不需要整页搜索栏、只要一块可查询表格」场景的底层 Hook。
>
> 来源库：`@sunny-base-web/ui` ｜ 分类：Data Display / 数据展示 ｜ 实现来自组件库源码 `packages/@ui/src/data/query-grid`（权威）；`docs/src/public/llms-full.txt` 仅记录为 `useSunnyQueryGrid(options: any)`

## 1. 何时使用

- 弹窗内的只读 / 可查询表格（如执行前检查、明细查看）
- 页面内嵌套的独立查询表格（不占整页）

不适用：

- **整页查询列表**（搜索栏 + 表格 + 查询方案）→ 用 `useList`（`@sunny-base-web/effects`，内部封装本 Hook）
- **可编辑表格**（行内编辑、新增/删行）→ 用 `useSunnyEditGrid` / `useTable`

> 本 Hook 是 `useList` / `useListV2` 的底层依赖；业务做整页查询时不会直接调它，只有在「组件级」需要一块独立查询表格时才直接使用。

## 2. 导入

```typescript
import { useSunnyQueryGrid } from '@sunny-base-web/ui';
```

## 3. 代码演示

### 3.1 基础用法（服务端查询 + 分页）

`gridOptions` 是完整 vxe-grid 配置，`proxyConfig.ajax.query` 负责服务端取数；返回 `[Grid, api]`，渲染 `<Grid />`：

```typescript
import { reactive } from 'vue';
import { useSunnyQueryGrid } from '@sunny-base-web/ui';
import { fetchList } from '#/api/demo';

const gridOptions = reactive({
  id: 'demoQueryGrid',
  border: true,
  height: 'auto',
  columns: [
    { type: 'checkbox', width: 50 },
    { type: 'seq', title: '序号', width: 60 },
    { field: 'cName', title: '名称' },
    { field: 'dCredate', title: '创建日期', sortable: true },
  ],
  pagerConfig: { enabled: true, pageSize: 20, pageSizes: [10, 20, 50, 100] },
  sortConfig: { remote: true }, // 服务端排序
  proxyConfig: {
    autoLoad: true,
    response: { result: 'result.records', total: 'result.total' },
    ajax: {
      query: async ({ page, sorts }: any) => {
        return fetchList({
          pageNo: page.currentPage,
          pageSize: page.pageSize,
          sortField: sorts?.[0]?.field || '',
          sortOrder: sorts?.[0]?.order || '',
        });
      },
    },
  },
});

const [Grid, gridApi] = useSunnyQueryGrid({
  gridOptions,
  gridEvents: {
    // 排序变化 → 重新查询
    sortChange: () => gridApi.commitProxy('query'),
  },
});
```

```vue
<template>
  <Grid />
</template>
```

### 3.2 工具栏按钮与行选中

`gridEvents.toolbarButtonClick` 处理工具栏按钮，`checkboxChange` / `currentChange` 监听选中：

```typescript
const [Grid, gridApi] = useSunnyQueryGrid({
  gridOptions: {
    /* ...列、分页、proxyConfig 同 3.1... */
    toolbarConfig: {
      refresh: true,
      zoom: true,
      custom: true,
      // 工具栏按钮在这里声明：code 是点击事件的匹配标识
      buttons: [
        { code: 'delete', name: '删除', icon: 'sunnyfont baseicon-delete' },
      ],
    },
    checkboxConfig: { highlight: true, reserve: true, trigger: 'row' },
  },
  gridEvents: {
    // 按钮点击：按 params.button.code 分发
    toolbarButtonClick(params: any) {
      const code = params.button.code;
      const selected = [
        ...params.$grid.getCheckboxReserveRecords(),
        ...params.$grid.getCheckboxRecords(),
      ];
      if (code === 'delete') {
        if (selected.length === 0) return;
        // 调删除 API 后刷新
        gridApi.commitProxy('query');
      }
    },
    checkboxChange: ({ records }: any) => {
      console.log('当前选中：', records);
    },
  },
});
```

> ⚠️ **禁止自己写 `<div>` + `<a-button>` 拼工具栏**。工具栏按钮一律走声明式 `buttons` 配置：
> - **组件级（本 Hook）**：写在 `gridOptions.toolbarConfig.buttons`（`{ code, name, icon }`）
> - **页面级（`useList`）**：由后端资源系统按 `resourceConfig` 自动注入，前端不写
>
> 点击统一在 `gridEvents.toolbarButtonClick` 里按 `params.button.code` 处理。自己拼 DOM 会导致工具栏刷新、列自定义、权限控制、平板适配全部失效。

## 4. API

> 本节按 Hook 的「入参 → 返回 → api 方法 → Grid 插槽」组织（Hook 没有 Props/Events 概念）。

### 4.1 入参 Options

```typescript
useSunnyQueryGrid(options: { gridOptions?: GridOptions; gridEvents?: GridEvents }): [Grid, api]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `gridOptions` | `object`（vxe-grid 配置） | 表格配置，见下表 |
| `gridEvents` | `Record<string, Function>` | 事件处理对象，内部自动转成 `onXxx` 监听器挂到 Grid 上 |

**`gridOptions` 常用子项**（标准 vxe-grid 属性）：

| 子项 | 说明 |
|------|------|
| `id` | Grid 标识（列自定义持久化 key） |
| `columns` | 列配置（含 `type: 'checkbox'` / `'seq'` / `{ field, title, sortable }`） |
| `proxyConfig` | 服务端查询代理：`{ autoLoad, response: { result: 'result.records', total: 'result.total' }, ajax: { query } }` |
| `pagerConfig` | 分页：`{ enabled, pageSize, pageSizes }` |
| `sortConfig` | `{ remote: true }` 服务端排序 |
| `filterConfig` | 列筛选；`{ remote: false }` 前端筛选 |
| `toolbarConfig` | 工具栏：`{ refresh, zoom, custom, buttons: [{ code, name, icon }] }`；`code` 对应 `gridEvents.toolbarButtonClick` 的 `params.button.code` |
| `checkboxConfig` | 勾选：`{ highlight, range, reserve, trigger, checkStrictly }` |
| `rowConfig` | `{ keyField, isCurrent, isHover }` |
| `gridTip` | 工具栏问号提示文本 |
| `height` / `border` / `stripe` / `size` / `treeConfig` / `aggregateConfig` | 其他 vxe 标准属性 |

**`gridEvents` 常用事件**：

| 事件 | 参数 | 说明 |
|------|------|------|
| `toolbarButtonClick` | `(params)` | 工具栏按钮点击；`params.button.code`、`params.$grid` |
| `sortChange` | `()` | 排序变化；通常 `() => api.commitProxy('query')` |
| `currentChange` | `({ row })` | 当前行变化（行切换） |
| `checkboxChange` | `({ records })` | 勾选变化 |

### 4.2 返回值

```typescript
const [Grid, api] = useSunnyQueryGrid(options);
```

| 返回 | 类型 | 说明 |
|------|------|------|
| `Grid` | `Component` | 渲染组件，`<Grid />` 直接用；内部已合并平板/桌面配置、查询前自动清空选中、桌面开启复制 |
| `api` | `VxeGridApi` | 命令式 API（见 4.3） |

### 4.3 api 方法（VxeGridApi）

| Method | Signature | Description |
|--------|-----------|-------------|
| `commitProxy` | `(code: string) => Promise<any>` | 提交代理，`commitProxy('query')` 重新查询（最常用） |
| `getSelection` | `() => any[]` | 获取当前选中行 |
| `clearSelection` | `() => void` | 清空选中（含跨页 reserve 记录） |
| `deleteSelection` | `() => Promise<void>` | 删除选中行 |
| `addEvent` | `({ record?, index? }) => Promise<void>` | 新增数据 |
| `$grid` | `→ VxeGridInstance` | 原始 vxe-table 实例，可调任何 vxe 方法（如 `getCheckboxRecords()`、`getCheckboxReserveRecords()`） |

### 4.4 Slots（Grid 组件）

| Slot | Description |
|------|-------------|
| `#<field>Slot` / `#<field>Cell` | 列自定义渲染插槽，按列 field 命名（如 `#cNameSlot`、`#cName1Cell`），作用域参数 `{ row }` |

## 5. 类型定义

```typescript
// Hook 签名
function useSunnyQueryGrid(options: {
  gridOptions?: Record<string, any>;   // vxe-grid 配置
  gridEvents?: Record<string, Function>; // 事件，转 onXxx
}): readonly [Component, VxeGridApi];

// 查询代理（服务端取数）
interface ProxyConfig {
  autoLoad?: boolean;
  response?: { result: string; total: string }; // 默认 { result: 'result.records', total: 'result.total' }
  ajax: {
    query: (params: { page: { currentPage; pageSize }; sorts: Array<{ field; order }> }, filterValues?: any) => Promise<any>;
  };
}
```

## 6. 注意事项 / FAQ

- **层级别混用**：整页查询列表用 `useList`（含搜索表单 + 查询方案，内部封装本 Hook）；只有「一块独立查询表格」才直接用 `useSunnyQueryGrid`。可编辑表格用 `useSunnyEditGrid` / `useTable`。
- **工具栏按钮在哪声明**：直接用本 Hook 时，按钮在 `gridOptions.toolbarConfig.buttons` 里手动声明（`{ code, name, icon }`），点击在 `gridEvents.toolbarButtonClick` 里按 `params.button.code` 分发。**页面级 `useList` 不一样**——按钮由后端资源系统按 `resourceConfig` 自动加载注入，前端不写。
- **Grid 内置「查询前自动清空选中」**：Hook 拦截了 `proxyConfig.ajax.query`，每次查询前自动 `api.clearSelection()`，无需手动处理。
- **服务端排序/分页**：`sortConfig: { remote: true }` + `proxyConfig.ajax.query` 里读 `sorts[0]`，并在 `gridEvents.sortChange` 里 `commitProxy('query')`。
- **刷新表格**用 `api.commitProxy('query')`；拿原始 vxe 能力（如跨页选中记录）用 `api.$grid.getCheckboxReserveRecords()`。
- **桌面默认开复制、禁剪切/粘贴/替换**（Hook 内置 `clipConfig` / `fnrConfig`），无需手动配。

## 7. 关联资源

- **上层封装**：`useList` / `useListV2`（页面级查询列表）—— 均在 `@sunny-base-web/effects`，内部调本 Hook
- **同级**：`useSunnyEditGrid`（可编辑表格）
- **标准模板**：[query-list](../page-patterns/query-list.md)（`useList` 用法，含完整配置写法可参照）
