# SunnyUpload / SunnySimpleUpload 上传

> 两个附件上传组件：`SunnyUpload` 是「附件管理面板」（两段式：先选后传，带进度条 / 批量操作 / 签名下载），`SunnySimpleUpload` 是「轻量即选即传」（tag 展示，适合表格行内）。
>
> 来源库：`@sunny-base-web/ui` ｜ 分类：Data / 数据展示 ｜ API 已对照源码 `packages/@ui/src/data/upload/index.vue`、`packages/@ui/src/data/simple-upload/index.vue`、`packages/@ui/src/data/upload/storage.ts` 核对（2026-08-24）

## 1. 何时使用

**选型对比：**

| 维度 | SunnyUpload | SunnySimpleUpload | Arco 原生 `Upload` |
|------|-------------|-------------------|--------------------|
| 形态 | 附件管理面板（选择 / 上传 / 全选 / 批量删除 / 进度条 / 折叠） | 上传按钮 + tag 列表 | Arco 原生 |
| 上传时机 | **两段式**：选文件只入本地暂存，点「上传附件」才真正 POST | **一段式**：选中即上传 | auto-upload 可配 |
| 下载 | 文件名可点击，支持后端签名 URL（`downAction`） | 无内置下载入口 | 自理 |
| 适用 | 表单弹窗附件字段（多附件、需管理） | 表格行内附件列、一两个附件的轻量场景 | 无 S3 参数需求时兜底 |
| schema 写法 | `component: 'SunnyUpload'` | `component: 'SunnySimpleUpload'` | `component: 'Upload'` |

- 表单里的附件字段 → `SunnyUpload`（进度 / 批量 / 下载齐全）
- 表格行内 / 编辑格里的附件 → `SunnySimpleUpload`（`EditRender.UploadRender` 内置用它）
- 不适用：不需要 S3 自定义参数的简单上传 → Arco 原生 `Upload`（第 3 层兜底）

## 2. 导入

```typescript
// 组件（独立使用时）
import { SunnyUpload, SunnySimpleUpload } from '@sunny-base-web/ui';

// 后端存储格式互转工具（编辑回填 / 提交转换，见 §5）
import { toStorageString, fromStorageString } from '@sunny-base-web/ui';
```

> 在 `SunnyForm` 的 schema 里**用字符串** `component: 'SunnyUpload'` / `'SunnySimpleUpload'`（已在 `COMPONENT_MAP` 注册，异步加载），不需要 `markRaw` 导入组件。上传接口地址 `action` / `downAction` / `httpClient` 全局已配（见 §4.4），schema 里通常只写 `accept` / `limit` / `maxSize`。

## 3. 代码演示

### 3.1 表单里的附件字段（form-modal / form-table-modal）

```typescript
// config.ts —— addFormSchema 追加附件字段
{
  fieldName: 'cAttachment',
  label: '附件',
  component: 'SunnyUpload',
  componentProps: {
    accept: '.pdf,.doc,.docx,.xls,.xlsx', // 全局 accept 是 ''（不限制），需要过滤时必须显式给
    limit: 5,       // apps/web 全局默认 5
    maxSize: 10,    // MB，全局默认 10
    // showEncrypt: true,  // 需要运行时勾选「是否加密」时打开
  },
  colProps: { span: 16 }, // 附件面板较宽，别用默认窄列
}
```

### 3.2 编辑回填 + 提交转换（与后端 `"name:url,name:url"` 格式互转）

```typescript
import { toStorageString, fromStorageString } from '@sunny-base-web/ui';

// 编辑打开：后端 "a.pdf:BASE/2026/a.pdf,b.txt:BASE/2026/b.txt" → 组件 JSON
const detail = await getById(record.id);
formApi.setValues({
  ...detail,
  cAttachment: fromStorageString(detail.cAttachment),
});

// 提交：组件 JSON → 后端存储格式
const values = await formApi.getValues();
await save({ ...values, cAttachment: toStorageString(values.cAttachment) });
```

### 3.3 表格行内附件列（table-modal / form-table-modal）

```typescript
import { h } from 'vue';
import { EditRender } from '@sunny-base-web/ui';

// 展示态把 JSON 转成文件名列表（UploadRender 默认展示是 JSON 原文，见 §6）
const fileNames = (val: any): string => {
  try {
    return JSON.parse(val || '[]').map((i: any) => i.name).join(', ');
  } catch {
    return '';
  }
};

// 列配置：编辑态自动渲染 SunnySimpleUpload（即选即传），params 即组件 props
{
  field: 'cFile',
  title: '附件',
  minWidth: 200,
  ...EditRender.UploadRender,
  params: { accept: '.pdf,.doc,.docx', limit: 3 },
  slots: {
    ...EditRender.UploadRender.slots,            // 保留 edit 插槽
    default: ({ row, column }: any) => [h('span', fileNames(row[column.field]))], // 覆盖展示
  },
}
```

```typescript
// 提交：明细行的附件字段同样要转换（getFullData 是类型化 async 方法）
const rows = await gridApi.getFullData();
await saveDetailData(rows.map((row: any) => ({ ...row, cFile: toStorageString(row.cFile) })));
```

## 4. API

### 4.1 SunnyUpload Props

> 已对照组件源码核对；有出入以 `packages/@ui/src/data/upload/index.vue` 为准。「默认」= 组件内置兜底值；apps/web 全局配置（§4.4）会优先于内置兜底生效。

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | `string` | `''` | 附件列表 **JSON 字符串**（`FileItem[]` 序列化，见 §4.3），不是数组 |
| `action` | `string` | 全局已配 | 上传接口地址（FormData POST，见下方「上传请求约定」） |
| `downAction` | `string` | 全局已配 | 下载签名接口：POST `{ filePath, storeType }`，期望 `{ code: 200, result: '签名URL' }`，拿到后 `window.open` |
| `accept` | `string` | 内置 `'.csv,.pdf,.xls,.xlsx'`；**apps/web 全局为 `''`（不限制）** | 可选文件类型 |
| `limit` | `number` | 内置 `10`；apps/web 全局 `5` | 最大文件数 |
| `maxSize` | `number` | `10`（MB） | 单文件大小上限 |
| `storeType` | `string` | `'amazon'` | 存储类型 |
| `s3FileDir` | `string` | `''` | S3 目录 |
| `preSigned` | `string` | `''` | 是否生成预签名 URL（`'1'` / `'0'`，注意是 **string**） |
| `preSignedExpire` | `string` | `''` | 预签名 URL 过期时间（注意是 **string**） |
| `readonly` | `boolean` | `false` | 只读：隐藏「选择 / 上传 / 删除」入口，**文件名仍可点击下载** |
| `disabled` | `boolean` | `false` | 禁用，行为同 `readonly`；表单五层 disabled（依赖/Schema/Props/表单级/全局）会自动传入 |
| `showEncrypt` | `boolean` | `false` | 显示「是否加密」checkbox |
| `encryptFile` | `boolean` | `false` | ⚠️ **SunnyUpload 实际不读此 prop**（上传时取面板 checkbox 状态）；只在 SunnySimpleUpload 生效 |

**上传请求约定**（两个组件一致）：POST `action`，`FormData`：`fileName`(文件) + `encryptFile`(`'1'`/`'0'`) + `storeType`（有值才带）+ `s3FileDir` / `preSigned` / `preSignedExpire`（配置了才带）。响应 `{ code: 200, message, result }`，`result` 字段会被合并进对应 `FileItem`（至少含 `url`）。

### 4.2 SunnySimpleUpload Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | `string` | - | 同上，JSON 字符串 |
| `action` | `string` | 全局已配 | 上传接口地址 |
| `accept` | `string` | 全局（apps/web 为 `''`） | 可选文件类型 |
| `encryptFile` | `boolean` | `false` | 上传时是否加密（**此组件生效**） |
| `storeType` / `s3FileDir` | `string` | `'amazon'` / `''` | 同 SunnyUpload |
| `preSigned` | `boolean` | `false` | 是否生成预签名 URL（注意是 **boolean**，与 SunnyUpload 不同） |
| `preSignedExpire` | `number` | `7`（天） | 签名过期时间（**number**） |
| `limit` | `number` | 全局 `5` | 超出弹错、不上传 |
| `maxSize` | `number` | 全局 `10`（MB） | 超出弹错、不上传 |
| `disabled` | `boolean` | `false` | 上传按钮与 tag 删除全部禁用 |

### 4.3 Events（两者相同）

| Event | Parameters | Description |
|-------|------------|-------------|
| `update:modelValue` | `(value: string)` | 附件列表变化（JSON 字符串），表单回写主通道 |
| `change` | `(value: string)` | 同 `update:modelValue` |

**`FileItem` 结构**（JSON 字符串的元素）：

```typescript
interface SunnyUploadFileItem {
  uid: string;          // 唯一 key（v-for 用）
  name: string;         // 文件名（展示 + 后端存储用）
  url: string;          // 上传成功后的存储地址（有 url = 已上传；无 url = 还在本地暂存）
  size?: number;
  type?: string;        // mime type
  percentage?: number;  // 上传进度 0-100
  status?: string;      // 'done' 等
  checked?: boolean;    // SunnyUpload 勾选态（批量删除用）
}
```

### 4.4 全局配置（uploadConfig）

应用入口 `setupBusinessForm({ config: { uploadConfig } })` 统一配置，**优先级：组件 props > 全局 > 内置兜底**。apps/web 已在 `apps/web/src/plugin/effects/index.ts` 配好：

| 键 | apps/web 实际值 | 说明 |
|----|----------------|------|
| `httpClient` | `requestClient` | 走项目拦截器（自动带 token）；**不配则降级裸 axios，无鉴权** |
| `action` | `'/upload/commonFileUpload'` | 上传接口 |
| `downAction` | `'/upload/commonFileDownload'` | 签名下载接口 |
| `storeType` | `'amazon'` | 存储类型 |
| `limit` / `maxSize` | `5` / `10` | 数量 / 单文件 MB |
| `accept` | `''` | **空 = 不限制类型**；要过滤必须每处 `componentProps` 显式给 |
| `s3FileDir` / `preSigned` / `preSignedExpire` | `''` / `false` / `7` | S3 目录 / 签名开关 / 过期天数 |

## 5. 工具函数（后端存储格式互转）

`modelValue`（JSON 字符串）与后端约定格式 `"name1:url1,name2:url2"` 互转，入口 `packages/@ui/src/data/upload/storage.ts`：

| 函数 | 方向 | 规则 |
|------|------|------|
| `toStorageString(json)` | 提交前：组件 → 后端 | 非法 JSON / 非数组 → `''`；**元素无 `url` 直接跳过（未上传的文件被丢弃）**；无 `name` 用空串占位 |
| `fromStorageString(str)` | 回填前：后端 → 组件 | 空值 → `'[]'`；用 `lastIndexOf(':')` 切分（兼容 `name:https://...`）；自动生成 `uid`、`percentage: 100`、`status: 'done'` |

## 6. 注意事项 / FAQ

- **`modelValue` 是 JSON 字符串不是数组** —— 表单字段、表格行字段的类型都是 `string`；与后端通信的边界（回填前 / 提交前）必须用 `fromStorageString` / `toStorageString` 转换，schema 阶段不做任何转换。
- **SunnyUpload 是两段式：选了 ≠ 传了** —— 选附件只入本地暂存，**必须点「上传附件」才真正 POST**；没点上传的文件不进 `modelValue`，提交时被 `toStorageString` 静默丢弃。提交前应检查并提示用户先上传（或组件外层自行校验）。
- **删除不调接口** —— 两个组件删除都只改本地列表（无 `delAction`）；S3 物理清理约定由表单保存流程统一处理（编辑打开时拍快照，提交前 diff 出待删 `url` 集合随保存请求交给后端）。
- **只读 / 禁用不影响下载** —— `readonly` / `disabled` 只隐藏「上传 / 删除」入口，`SunnyUpload` 的文件名链接仍可点击下载（详情只读场景的常见诉求）。
- **`accept` 默认不限制** —— apps/web 全局配的是 `''`，组件内置的 `'.csv,.pdf,.xls,.xlsx'` 兜底被全局空串覆盖；要限制类型必须在 `componentProps`（表格列在 `params`）显式传。
- **表格列展示默认是 JSON 原文** —— `EditRender.UploadRender` 的展示插槽直接 `JSON.stringify`；要显示文件名需覆盖 `slots.default`（见 §3.3），编辑插槽保留即可。
- **表格上传列即选即传** —— `EditRender.UploadRender` 编辑态渲染的是 `SunnySimpleUpload`（一段式，无「上传附件」按钮），不存在两段式的丢文件问题。
- **`preSigned` / `preSignedExpire` 类型不一致** —— SunnyUpload 是 `string`、SunnySimpleUpload 是 `boolean` / `number`；跨场景复制配置时注意。
- **`encryptFile` prop 在 SunnyUpload 不生效** —— 加密由面板 checkbox（`showEncrypt: true` 时显示）控制；prop 只在 SunnySimpleUpload 参与请求。
- **组件不直接依赖 `requestClient`** —— 通过全局 `uploadConfig.httpClient` 注入；留空降级裸 axios（无 token，生产会 401）。
- **未配 `action` 会 console.warn** —— 全局没配又没传 props 时组件仅在控制台警告，上传按钮点了没反应，注意排查。

## 7. 关联资源

- **标准模块**：[form-modal](../modules/form-modal.md)（表单附件字段 + 回填/提交转换）、[table-modal](../modules/table-modal.md)（行内附件列）、[form-table-modal](../modules/form-table-modal.md)（两者组合）
- **相关组件**：`SunnyForm` / `useForm`（schema 宿主）、`useSunnyEditGrid` / `useTable`（`EditRender.UploadRender` 的宿主）
- **组件源码**：`packages/@ui/src/data/upload/index.vue`、`packages/@ui/src/data/simple-upload/index.vue`、`packages/@ui/src/data/upload/storage.ts`（API 有出入时以源码为准）
- **详细文档**：`docs/src/components/data/upload.md`、`docs/src/components/data/simple-upload.md`（组件库文档站）
