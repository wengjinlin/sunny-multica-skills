# useImport 数据导入

> 导入弹窗 Hook（effects 层，**业务统一入口**，与 [useExport](./export.md) 对称）：返回 `{ ImportModal, open, importModalApi }`，内置完整流程——模板下载 + 文件上传 + 类型/大小/数量校验 + 解码模式开关。通常配 query-list 工具栏的「导入」按钮（code `daoru/show`）。
>
> 来源库：`@sunny-base-web/effects`（`useImport`，业务统一用这个）｜ 底层封装 ui 层 `useImportModal` / `SunnyImportModal`（`@sunny-base-web/ui`，见 [SunnyImportModal.md](../components/SunnyImportModal.md)）

## 1. 何时使用

- 工具栏「导入」按钮 → Excel 批量导入数据
- 需要下载导入模板 + 上传填写后的文件
- 需要解码模式（文件编码转换场景，弹窗内置开关）

不适用：

- 数据**导出** → 用 [export.md](./export.md)（`useExport`）
- 单条录入 → 用 [form-modal](./form-modal.md)
- 非 Excel 的附件上传 → 用 `SunnyUpload`（见 [SunnyUpload.md](../components/SunnyUpload.md)）

> **业务统一用 `useImport`（effects）**，不要直接用底层 `SunnyImportModal` / `useImportModal`。

## 2. 导入

```typescript
import { useImport } from '@sunny-base-web/effects';
```

## 3. 代码演示

### 3.1 基础用法（配 query-list 导入按钮）

`useImport` 返回 `ImportModal`（渲染）+ `open`（打开）；在工具栏按钮事件里按 `code` 触发。**最简只需 `nModid` + `nButtonid`**，模板下载和上传地址由组件自动拼：

```typescript
import { useList, useImport } from '@sunny-base-web/effects';

defineOptions({ name: 'DemoQuery' });

const { ImportModal, open: openImport } = useImport({
  nModid: 2845,
  nButtonid: 3526,
});

const { QueryForm, formApi, Grid } = useList({
  searchFormSchema,
  tableColumns,
  resourceConfig,
  queryFunction,
  gridEvents: {
    toolbarButtonClick(params: any) {
      // ⚠️ 导入按钮 code 用框架标准 daoru/show，禁止 'import'（vxe 保留字会被静默拦截）
      if (params.button.code === 'daoru/show') {
        openImport({ nButtonid: params.button.nButtonid }); // 运行期按资源按钮覆盖
      }
    },
  },
});
```

```vue
<template>
  <QueryForm />
  <Grid />
  <!-- 导入弹窗（全局放一个即可） -->
  <ImportModal />
</template>
```

### 3.2 成功回调刷新 + 自定义地址

```typescript
const { ImportModal, open } = useImport({
  // 默认地址不满足时覆盖（POST {templateUrl}/export/fileDownload、POST {uploadUrl}/upload/fileUpload）
  templateUrl: '/demo/importTemplate',
  uploadUrl: '/demo/importUpload',
  params: { type: 'batch', category: 'IQC' }, // 附加业务参数 → 序列化为 paramMap 提交
  onUploadSuccess: () => {
    // 导入后必须刷新列表
    gridApi.commitProxy('query');
  },
  onUploadError: (err: any) => {
    console.error('导入失败：', err);
  },
});
```

## 4. API

### 4.1 入参 UseImportOptions（= SunnyImportModal 全部选项的 Partial）

| 属性 | 类型 | 说明 |
|------|------|------|
| `nModid` | `number \| string` | 模块 ID（最简用法必填，模板/上传地址按它自动拼） |
| `nButtonid` | `number \| string` | 按钮 ID（同上，随表单一并提交） |
| `templateUrl` | `string` | 模板下载地址（空则按 nModid/nButtonid 自动拼） |
| `uploadUrl` | `string` | 上传地址（空则用默认 `/upload/fileUpload`） |
| `accept` | `string` | 接受的文件扩展名，默认 `.xlsx,.xls` |
| `maxSize` | `number` | 最大文件大小（MB），默认 10 |
| `limit` | `number` | 最大文件数量，默认 1 |
| `params` | `Record<string, any>` | 上传附加参数（→ `paramMap`） |
| `onUploadSuccess` | `(response) => void` | 上传成功（在此刷新列表） |
| `onUploadError` | `(error) => void` | 上传失败 |
| `onDownloadSuccess` / `onDownloadError` | `() => void` / `(error) => void` | 模板下载回调 |

### 4.2 返回值

| 返回 | 类型 | 说明 |
|------|------|------|
| `ImportModal` | `Component` | 导入弹窗组件，模板里 `<ImportModal />`（全局放一个） |
| `open` | `(params?) => void` | 打开弹窗，参数覆盖初始化默认值 |
| `importModalApi` | `api` | 底层控制器（`open` / `close`，一般用不到） |

### 4.3 open() 参数

同入参（Partial）——运行期覆盖 `nModid` / `nButtonid` / `templateUrl` / `uploadUrl` / `params` 等。

## 5. 注意事项 / FAQ

- **业务用 `useImport`（effects）**，与 `useExport` 对称；不要直接用底层 `SunnyImportModal` / `useImportModal`。
- **导入按钮 code 用 `daoru/show`**（框架标准），**禁止 `'import'`**——vxe 保留字会被静默拦截，`toolbarButtonClick` 永远不触发。
- **最简用法**：只传 `nModid` + `nButtonid`，地址自动拼；`@upload-success`（即 `onUploadSuccess`）里刷新列表。
- **内置校验**：类型（`accept`）、大小（`maxSize` MB）、数量（`limit`），不通过自动提示。
- **解码模式**：弹窗内置开关，开启后走 `fileUploadDecode` 接口。
- **导入后必须刷新**：`onUploadSuccess` 里 `gridApi.commitProxy('query')` 或重查列表。
- **请求鉴权（重要）**：模板下载/上传优先走应用注入的 `importAdapter`（基于 requestClient，自动携带 token / 签名），未注入时降级裸 axios + `apiPrefix`（无鉴权场景，会 401）。适配器由应用入口 **`setupImportExport()`**（`@sunny-base-web/effects`）注入——与 `setupBusinessForm`（表单适配器）是两个独立入口，且须在其**之后**调用（后者全量重算配置会清掉未传的键）；apps/web 已配好。⚠️ 适配器分支组件传的是**相对路径**（requestClient 的 baseURL 已含 apiPrefix，自行拼接会产生双前缀）；错误提示组件内自理。

## 6. 关联资源

- **兄弟模块**：[export.md](./export.md)（导出，`useExport`）
- **底层组件**：[SunnyImportModal.md](../components/SunnyImportModal.md)（`useImportModal` / `SunnyImportModal`，`@sunny-base-web/ui`）
- **页面集成**：[query-list.md](../page-patterns/query-list.md)（工具栏导入按钮，code `daoru/show`）
