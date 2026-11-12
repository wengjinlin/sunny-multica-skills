# useExport 数据导出

> 导出弹窗 Hook：返回 `{ ExportModal, open, exportModalApi }`，提供「条件筛选 + 列配置 + 导出 Excel」的完整导出流程。通常配 query-list 工具栏的「导出」按钮，按当前搜索条件导出。
>
> 来源库：`@sunny-base-web/effects`（`useExport`，业务统一用这个）｜ 内部封装 ui 层 `useExportModalLight`（`@sunny-base-web/ui`）｜ ⚠️ `docs/src/public/llms-full.txt` 把底层 hook 写成了 `useExportModal`，实际是 `useExportModalLight`，以源码为准

## 1. 何时使用

- 查询列表工具栏「导出」按钮 → 弹窗导出 Excel
- 需要按当前搜索条件导出筛选后的数据（`conditionMap`）
- 需要用户选择导出列 / 配置导出偏好（`tableColumns`）

不适用：

- 数据**导入** → 用 `SunnyImportModal` / `useImportModal`（见 [SunnyImportModal.md](../components/SunnyImportModal.md)）
- 单条/明细展示 → 用 [table-modal](./table-modal.md)
- 纯文件下载（无列配置/条件）→ 直接调下载接口

> **业务统一用 `useExport`（effects）**，不要直接用底层 `SunnyExportModal` 组件或 `useExportModalLight`。`useExport` 已把路由（`useRouter`）和参数合并处理好了。

## 2. 导入

```typescript
import { useExport } from '@sunny-base-web/effects';
```

## 3. 代码演示

### 3.1 基础用法（配 query-list 导出按钮）

`useExport` 返回 `ExportModal`（渲染）+ `open`（打开）；在工具栏按钮事件里调 `open`，传入搜索条件 + 列配置：

```typescript
import { useList, useExport } from '@sunny-base-web/effects';
import { searchFormSchema, tableColumns, resourceConfig } from './config';

defineOptions({ name: 'DemoQuery' });

// 导出 Hook（可传自定义导出地址）
const { ExportModal, open: openExport } = useExport({
  customExportUrl: '/demo/export',
});

const { QueryForm, formApi, Grid } = useList({
  searchFormSchema,
  tableColumns,
  resourceConfig,
  queryFunction,
  gridEvents: {
    async toolbarButtonClick(params: any) {
      if (params.button.code === 'daochu/show') {
        const formValues = await formApi.getValues(); // 取搜索条件
        openExport({
          conditionMap: formValues,  // 按搜索条件导出
          tableColumns,              // 弹窗据此生成可选导出列
        });
      }
    },
  },
});
```

```vue
<template>
  <QueryForm />
  <Grid />
  <!-- 导出弹窗（全局一个即可） -->
  <ExportModal />
</template>
```

> 工具栏「导出」按钮本身由后端资源系统按 `resourceConfig` 注入（页面级 useList 的规则），前端只在 `toolbarButtonClick` 里按 `code`（通常 `daochu/show`）触发 `openExport`。

### 3.2 导出回调与多地址

成功/失败回调 + 多页面用不同导出地址：

```typescript
const { ExportModal, open } = useExport({
  onExportSuccess: (res: any) => {
    Message.success('导出成功');
    console.log('导出结果：', res);
  },
  onExportError: (err: any) => {
    console.error('导出失败：', err);
  },
});

// 也可在 open 时临时指定地址 / 模块按钮 ID
open({
  conditionMap: formValues,
  tableColumns,
  exportUrl: '/demo/export-special', // 覆盖初始化地址
  nmodid: 2845,
  nButtonid: 3526,
});
```

## 4. API

> 本节按 Hook 的「入参 → 返回 → open 参数」组织。

### 4.1 入参 UseExportOptions

```typescript
useExport(options?: UseExportOptions): { ExportModal, exportModalApi, open }
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `exportUrl` | `string` | 默认导出接口地址 |
| `customExportUrl` | `string` | 自定义导出接口地址（每个页面不同时用） |
| `exportUserWebConfig` | `ExportUserWebConfig` | 用户导出偏好（行号、最大行数等） |
| `onExportSuccess` | `(res) => void` | 导出成功回调 |
| `onExportError` | `(err) => void` | 导出失败回调 |
| `nmodid` | `number \| string` | 模块 ID（后端接口鉴权/路由） |
| `nButtonid` | `number \| string` | 按钮 ID（后端接口鉴权/路由） |

### 4.2 返回值

```typescript
const { ExportModal, exportModalApi, open } = useExport(options);
```

| 返回 | 类型 | 说明 |
|------|------|------|
| `ExportModal` | `Component` | 导出弹窗组件，模板里 `<ExportModal />`（全局放一个） |
| `open` | `(params) => void` | 打开弹窗，传入条件 + 列（见 4.3） |
| `exportModalApi` | `api` | 底层弹窗 api（一般用不到，`open` 已够用） |

### 4.3 open() 参数

| 属性 | 类型 | 说明 |
|------|------|------|
| `conditionMap` | `Record<string, any>` | 导出条件，通常为搜索表单 `formApi.getValues()`；不传则导全量 |
| `tableColumns` | `VxeGridProps['columns']` | 当前页表格列配置，弹窗据此生成「可选导出列」 |
| `exportUrl` | `string` | 临时覆盖导出地址（优先于初始化的 `exportUrl`） |
| `nmodid` / `nButtonid` | `number \| string` | 临时覆盖模块/按钮 ID |

## 5. 类型定义

```typescript
interface UseExportOptions {
  exportUrl?: string;
  customExportUrl?: string;
  exportUserWebConfig?: ExportUserWebConfig;
  onExportSuccess?: (res: any) => void;
  onExportError?: (err: any) => void;
  nmodid?: number | string;
  nButtonid?: number | string;
}

// useExport 返回
interface UseExportReturn {
  ExportModal: Component;
  exportModalApi: ExportModalApi;
  open: (params: { conditionMap?: Record<string, any>; tableColumns?: any[]; exportUrl?: string; nmodid?; nButtonid? }) => void;
}
```

## 6. 注意事项 / FAQ

- **业务用 `useExport`（effects）**，不要直接用 `SunnyExportModal` 组件或 `useExportModalLight`；`useExport` 内部已处理路由和参数合并。
- **请求鉴权（重要）**：导出请求优先走应用注入的 `exportAdapter`（基于 requestClient，自动携带 token / 签名），未注入时降级裸 axios（无鉴权场景，会 401）。适配器由应用入口 **`setupImportExport()`**（`@sunny-base-web/effects`）注入——与 `setupBusinessForm`（表单适配器）是两个独立入口，且须在其**之后**调用（后者全量重算配置会清掉未传的键）；apps/web 已在 `apps/web/src/plugin/effects/index.ts` 配好。
- **`conditionMap` 传搜索表单值**：`const formValues = await formApi.getValues(); openExport({ conditionMap: formValues, tableColumns })`，这样只导筛选后的数据；不传则导全量。
- **`tableColumns` 传当前页列**：弹窗据此生成可选导出列，让用户勾选要导出的列。
- **导出按钮是资源驱动**：页面级（useList）的「导出」按钮由后端按 `resourceConfig` 注入，前端只在 `toolbarButtonClick` 里按 `code`（通常 `daochu/show`）触发；组件级直接用本 Hook 时按钮走 `toolbarConfig.buttons`。
- **llms-full.txt 笔误**：底层 hook 实际是 `useExportModalLight`，不是文档写的 `useExportModal`，以源码为准。
- **`ExportModal` 全局放一个即可**，多次 `open` 复用同一弹窗实例。

## 7. 关联资源

- **兄弟组件**：[SunnyImportModal.md](../components/SunnyImportModal.md)（数据导入，自包含组件）
- **常用搭配**：`useList`（query-list 工具栏集成导出按钮，见 [query-list.md](../page-patterns/query-list.md) 变体「带导出」）
- **底层**：`useExportModalLight` / `SunnyExportModal`（`@sunny-base-web/ui`，业务一般不直接用）
