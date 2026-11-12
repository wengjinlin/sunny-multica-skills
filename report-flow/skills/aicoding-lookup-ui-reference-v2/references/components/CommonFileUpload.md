# CommonFileUpload 附件上传

> 表单 / 表格里传附件的框架标准组件：`el-upload` + 自定义 `http-request`（对接后端上传服务 / S3 预签名），**两段式交互**（选文件 → 点「上传附件」），v-model 为 JSON 字符串。配套 `<FileList />` 展示附件列表。**不要用组件库的 `kunkka-upload`**（工程内 0 使用）或裸 `el-upload`。

> 来源：[src/components/Sunnyoptical/commonFileUpload/index.vue](../../../../../src/components/Sunnyoptical/commonFileUpload/index.vue) + [fileList/index.vue](../../../../../src/components/Sunnyoptical/fileList/index.vue)（[src/plugins/sunnyoptical.js](../../../../../src/plugins/sunnyoptical.js) 全局注册）

## 1. 何时使用

- 表单附件字段（合同 / 凭证 / 说明文件）
- 需要限制类型 / 大小 / 数量的业务上传

不适用：

- Excel 批量导入数据 → [import.md](../modules/import.md)（importDialog，走导出服务）
- 纯前端文件处理（不落服务端） → 无（浏览器限制）

## 2. 导入

全局注册，模板直接写 `<CommonFileUpload>` / `<FileList>`。

## 3. 代码演示

### 3.1 基础用法（表单字段）

```vue
<template>
  <!-- v-model 是 JSON 字符串（如 '[{"filename":"a.pdf","fileurl":"https://..."}]'） -->
  <CommonFileUpload
    v-model="formData.model.cAttachment"
    accept=".pdf,.doc,.docx,.xls,.xlsx"
    :limit="5"
    :max-size="10"
  />
</template>
```

### 3.2 只读回显（详情弹窗）

```vue
<CommonFileUpload v-model="cAttachment" readonly />
<!-- 或纯展示用 FileList -->
<FileList :value="cAttachment" />
```

## 4. API

### 4.1 Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `String` | `''` | v-model，**JSON 字符串**（文件名 / 地址数组序列化） |
| `accept` | `String` | `'.csv,.pdf,.xls,.xlsx'` | 接受的文件类型 |
| `limit` | `Number` | `10` | 最多文件数 |
| `maxSize` | `Number` | `10` | 单文件上限（MB） |
| `storeType` | - | - | 存储方式（对接不同后端存储） |
| `readonly` | `Boolean` | `false` | 只读（隐藏按钮，仅展示） |
| `showEncrypt` | `Boolean` | `false` | 显示「是否加密」勾选 |

> 其余 `el-upload` attrs 透传（`headers` 等）。

### 4.2 交互（两段式，同款高频坑）

1. **「选择附件」**：文件进本地暂存列表（此时不在 v-model 里）；
2. **「上传附件」**：暂存文件逐个走 `http-request` 上传，成功后才写入 value。

**没点「上传附件」的文件不进表单值，提交时静默丢失**——提交前如需强提示，检查暂存列表。

### 4.3 FileList

| Prop | Description |
|------|-------------|
| `value` | 同上 JSON 字符串 |

纯展示附件（名称 + 下载 / 预览），详情页用它。

## 6. 注意事项 / FAQ

- **v-model 是 JSON 字符串不是数组**：回显时后端若存 `"name:url,..."` 之类格式，边界处先转成组件格式再赋值；提交时按后端要求反向转换（转换只发生在边界，别在组件里hack）。
- **两段式丢文件**：见上；用户体验上按钮文案已区分「选择附件」/「上传附件」。
- **加密**：`showEncrypt` 开启后勾选「是否加密」按加密通道上传。
- **表格单元格里的附件**：用插槽自嵌本组件（CommonTable 无内置 Upload 列控件）。
- **el-upload 原生 `action` 不用管**：组件已 `action="#"` + `:http-request` 接管，不要另传 `action`。

## 7. 关联资源

- **相关组件**：`FileList`（展示）、[KunkkaForm.md](KunkkaForm.md)（表单宿主）
- **姊妹模块**：[import.md](../modules/import.md)（Excel 数据导入，别混用）
- **真实代码**：[src/components/Sunnyoptical/commonFileUpload/index.vue](../../../../../src/components/Sunnyoptical/commonFileUpload/index.vue)
