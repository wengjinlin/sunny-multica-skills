# Excel 导入（importDialog）

> 工具栏导入 Excel 的**自包含模块**：页面放一个全局组件 + 后端资源配一个按钮，上传 / 模板下载 / 报错回显全部内置，业务代码只处理「导完刷新」。

> 组件源码：[src/components/Sunnyoptical/importDialog/index.vue](../../../../../src/components/Sunnyoptical/importDialog/index.vue)（[src/plugins/sunnyoptical.js](../../../../../src/plugins/sunnyoptical.js) 全局注册，页面无需 import）｜ 接口：[src/api/daochu.js](../../../../../src/api/daochu.js)（`fileUpload` / `fileUploadDecode` / `fileDownload`）

## 1. 何时使用

- 查询列表页工具栏「导入」按钮：上传 Excel 批量入库 + 下载导入模板

不适用：

- 业务附件上传（保存到单据） → [CommonFileUpload.md](../components/CommonFileUpload.md)
- 页面内小量数据录入 → 表格弹窗行编辑（[table-modal](./table-modal.md)）

## 2. 标准用法（两步）

### 2.1 资源配按钮

资源管理给查询页模块加按钮：`cArea='searchTable'`、**`cStoremethod`（handle）= `daoru/show`**。点击时 kunkka-ux-grid 会 `dispatch('daoru/show', {...})`，弹窗按 `nButtonid` 归属当前模块自动打开。

### 2.2 页面放组件

```vue
<template>
  <div class="xxxQuery commonQueryDiv">
    <kunkka-ux-grid ... />
    <!-- 导入组件：打开由 Vuex daoru 模块驱动（watch daoru.visible），ref 按模板惯例命名 -->
    <importDialog ref="importDialog" @uploadCallback="uploadCallback" />
  </div>
</template>
<script>
export default {
  methods: {
    // 上传完成回调（成功/失败都会回）：刷新列表
    uploadCallback(res) {
      this.$store.dispatch(`${this.name}/queryList`)
    }
  }
}
</script>
```

就这些——上传请求（FormData 带 `fileName` / `nModid`=$route.meta.number / `nButtonid` / `usernumb` / `paramMap`）、目标地址（`process.env.VUE_APP_EXPORTURL`）、失败清文件等全部内置。

## 3. Props / 事件

| 项 | 说明 |
|----|------|
| prop `exportUrl` | 上传地址，默认 `process.env.VUE_APP_EXPORTURL`（一般不传） |
| prop `downloadUrl` | 模板下载地址，默认同 `process.env.VUE_APP_EXPORTURL`（一般不传；下载接口走 `fileDownload`） |
| prop `paramMap` | 上传时附带的额外参数对象（`Object`，内部 `JSON.stringify` 进 FormData） |
| 事件 `uploadCallback(res)` | 上传接口返回后触发（组件内已按结果报错 / 关弹窗），页面在里头刷新列表 |

## 4. 关键约定（踩坑高频点）

- **弹窗打开条件**：`daoru.visible === true` **且** 按钮 `nButtonid` 属于当前模块的导入按钮组（组件 computed 里判断，避免多模块弹窗接口重复调用）——所以资源按钮必须配在**使用页面的模块**下，不能配到公共模块。
- **`$route.meta.number` 必须存在**：上传 FormData 的 `nModid` 取它；资源菜单没挂 id 会直接报「没有获取到模块ID」。
- **「上传并解析」（fileUploadDecode）**：加密 / 编码模板用它，普通模板 `fileUpload`；模板下载按钮走组件内 `fileDownload` + `FileSaverDoExport`（[src/utils/file-saver.js](../../../../../src/utils/file-saver.js)）。
- **刷新列表**：`uploadCallback` 里 `dispatch(`${name}/queryList`)`（照抄 queryListTemplate 的写法）。
- **导入报错信息**由后端经 `request.js` 全局拦截弹出，页面不要再包一层错误提示。

## 5. 关联资源

- **姊妹模块**：[export.md](./export.md)（导出，同一资源体系）
- **页面集成**：[query-list](../page-patterns/query-list.md) §3.3（模板里就有 `<importDialog>` 位）
- **真实代码**：[src/template/queryListTemplate.vue](../../../../../src/template/queryListTemplate.vue)（`<importDialog />` 标配位）
