# SunnyImportModal 导入弹窗

> Excel 文件批量导入弹窗组件。`SunnyImportModal`（`@sunny-base-web/ui`）**内置完整流程**：模板下载 + 文件上传 + 类型/大小/数量校验 + 解码模式开关，开箱即用。
>
> **业务统一入口是 effects 层的 `useImport`**（与 `useExport` 对称），见 [import.md](../modules/import.md)；本文档为底层组件细节，直接用组件 / `useImportModal` 仅在无 effects 的纯 ui 场景。

## 1. 何时使用

- 工具栏「导入」按钮 → Excel 批量导入数据
- 需要下载导入模板 + 上传填写后的文件
- 需要解码模式（文件编码转换）

不适用：

- 单条录入 → 用 [form-modal](../modules/form-modal.md)
- 非 Excel 的附件上传 → 用 `SunnyUpload`（见 [组件选型](../components/)）
- 数据**导出** → 用 [export.md](../modules/export.md)（`useExport`）

## 2. 文件结构

**无需新建文件**，在调用方（如 `{Name}Query.vue`）导入组件即可：

```typescript
import { SunnyImportModal } from '@sunny-base-web/ui';
```

## 3. 标准实现

### 3.1 组件方式（推荐）

模板里放 `<SunnyImportModal ref />`，按钮点击调 `ref.open()`。**最简只需 `nModid` + `nButtonid`**，模板下载和上传地址由组件按这两个 ID 自动拼接：

```vue
<script setup lang="ts">
import { ref } from 'vue';
import { SunnyImportModal } from '@sunny-base-web/ui';

defineOptions({ name: 'DemoQuery' });

const importModalRef = ref();

/** 导入成功后刷新列表 */
function handleUploadSuccess(response: any) {
  console.log('导入成功：', response);
  // gridApi.commitProxy('query') 或 loadData()
}

function handleImport() {
  importModalRef.value?.open();
}
</script>

<template>
  <a-button type="primary" @click="handleImport">导入</a-button>

  <SunnyImportModal
    ref="importModalRef"
    :n-modid="2845"
    :n-buttonid="3526"
    @upload-success="handleUploadSuccess"
  />
</template>
```

### 3.2 在 query-list 工具栏集成

「导入」按钮由后端资源系统按 `resourceConfig` 注入，前端在 `toolbarButtonClick` 里按 `code` 触发 `open()`：

```typescript
const gridEvents = {
  toolbarButtonClick(params: any) {
    if (params.button.code === 'daoru/show') { // 框架标准导入 code，别用 'import'（vxe 保留字）
      importModalRef.value?.open();
    }
  },
};
```

### 3.3 Hook 方式（动态参数）

需要 JS 里灵活控制 / 运行时传参时用 `useImportModal`，返回 `[组件, 控制器]`：

```vue
<script setup lang="ts">
import { useImportModal } from '@sunny-base-web/ui';

const [ImportModal, importControls] = useImportModal({
  accept: '.xlsx,.xls',
  maxSize: 10,
});

function handleImport() {
  importControls.open({
    nModid: 2845,
    nButtonid: 3526,
    params: { batchNo: 'BATCH_001' }, // 附加业务参数 → 序列化为 paramMap
  });
}
</script>

<template>
  <a-button @click="handleImport">导入</a-button>
  <ImportModal @upload-success="loadData" />
</template>
```

### 3.4 自定义地址 + 附加参数

默认地址不满足时覆盖 `template-url` / `upload-url`；业务参数走 `params`：

```vue
<SunnyImportModal
  ref="importModalRef"
  template-url="/demo/importTemplate"
  upload-url="/demo/importUpload"
  :params="{ type: 'batch', category: 'IQC' }"
  :n-modid="2845"
  :n-buttonid="3526"
  @upload-success="handleUploadSuccess"
/>
```

> 默认地址：模板下载 `/export/fileDownload?nModid=xxx&nButtonid=xxx`，上传 `/upload/fileUpload`（解码模式走 `/upload/fileUploadDecode`，弹窗内有开关）。

## 4. 关键约定

- **最简用法**：只传 `nModid` + `nButtonid`，模板/上传地址自动拼，`@upload-success` 里刷新列表。
- **`params` → `paramMap`**：附加业务参数会被序列化为 `paramMap` 字段提交到后端。
- **内置校验**：文件类型（`accept`，默认 `.xlsx,.xls`）、大小（`maxSize`，默认 10MB）、数量（`limit`，默认 1），不通过自动提示。
- **解码模式**：弹窗内置开关，开启后走 `fileUploadDecode` 接口（编码转换场景）。
- **请求鉴权（重要）**：组件请求优先走全局注入的 `importAdapter`（`DEFAULT_FORM_COMMON_CONFIG.importAdapter`，由应用入口 `setupImportExport()`（`@sunny-base-web/effects`）注入，基于 requestClient 自动携带 token），未注入时降级裸 axios + `apiPrefix`（无鉴权场景，会 401）。适配器分支组件传的是**相对路径**（requestClient 的 baseURL 已含 apiPrefix，勿自行拼接避免双前缀）。
- **导入后必须刷新**：`@upload-success` 里 `gridApi.commitProxy('query')` 或重查列表。
- **导入按钮资源驱动**：页面级（useList）按钮由后端按 `resourceConfig` 注入，前端只按 `code` 触发。
- **⚠️ 按钮 code 禁止用 vxe 保留字**：`import` / `export` / `print` / `open_import` / `open_export` / `open_print` / `custom` / `zoom` / `refresh`——vxe 工具栏会静默拦截这些 code 自己处理，`toolbarButtonClick` **永远不触发**（症状：按钮看得见、点击毫无反应）。导入按钮 code 用框架标准 **`daoru/show`**（资源表 `C_STOREMETHOD` 字段）。

## 5. API

### 5.1 Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `nModid` | `any` | — | 模块 ID（鉴权/路由，最简必填） |
| `nButtonid` | `any` | — | 按钮 ID（鉴权/路由，最简必填） |
| `templateUrl` | `string` | `''` | 模板下载地址（空则按 nModid/nButtonid 自动拼） |
| `uploadUrl` | `string` | `''` | 上传地址（空则用默认 `/upload/fileUpload`） |
| `accept` | `string` | `.xlsx,.xls` | 接受的文件扩展名 |
| `maxSize` | `number` | `10` | 最大文件大小（MB） |
| `limit` | `number` | `1` | 最大文件数量 |
| `params` | `object` | — | 上传附加参数（→ `paramMap`） |

### 5.2 Events

| 事件 | 参数 | 说明 |
|------|------|------|
| `upload-success` | `(response)` | 上传成功（在此刷新列表） |
| `upload-error` | `(error)` | 上传失败 |
| `download-success` | — | 模板下载成功 |
| `download-error` | `(error)` | 模板下载失败 |
| `close` | — | 弹窗关闭 |

### 5.3 ref 方法

| 方法 | 说明 |
|------|------|
| `open()` | 打开导入弹窗 |
| `close()` | 关闭导入弹窗 |

### 5.4 useImportModal Hook

```typescript
const [ImportModal, controls] = useImportModal(defaultOptions);
// controls.open(options?) / controls.close()
```

返回 `[组件, { open, close }]`；`open` 可传部分 props 覆盖默认值。

## 6. 关联资源

- **业务入口**：[import.md](../modules/import.md)（`useImport`，`@sunny-base-web/effects`）
- **组件**：`SunnyImportModal` / `useImportModal`（`@sunny-base-web/ui`，本文档）
- **兄弟模块**：[export.md](../modules/export.md)（导出，`useExport`）
- **页面集成**：[查询列表页标准模板](../page-patterns/query-list.md)（工具栏导入按钮）
