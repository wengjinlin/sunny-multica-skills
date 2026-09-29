# Excel 导出（exportDialog）

> 工具栏导出 Excel 的**自包含模块**：页面放一个全局组件 + 后端资源配一个按钮，列选择 / 列排序 / 导出类型 / 文件流保存全部内置，业务代码几乎为零。

> 组件源码：[src/components/Sunnyoptical/exportDialog/index.vue](../../../../../src/components/Sunnyoptical/exportDialog/index.vue)（全局注册于 [src/plugins/sunnyoptical.js](../../../../../src/plugins/sunnyoptical.js)）｜ 接口：[src/api/daochu.js](../../../../../src/api/daochu.js)（`exportOpenInit`）｜ 文件保存：[src/utils/file-saver.js](../../../../../src/utils/file-saver.js)（`FileSaverDoExport`）

## 1. 何时使用

- 查询列表页工具栏「导出」按钮：勾选导出列、拖拽排序列、选导出类型后导出当前模块数据

不适用：

- 前端本地生成简单文件（不涉后端导出服务） → `file-saver.js` 直接用
- 把附件传给后端 → [CommonFileUpload.md](../components/CommonFileUpload.md)

## 2. 标准用法（两步）

### 2.1 资源配按钮

资源管理给查询页模块加按钮：`cArea='searchTable'`、**`cStoremethod`（handle）= `daochu/show`**。`list` mixin 会把这类按钮收进 `tableAttrs.exportBtns`，点击时 `dispatch('daochu/show', {...})` 打开导出弹窗（同样按 `nButtonid` 归属当前模块）。

### 2.2 页面放组件

```vue
<template>
  <div class="xxxQuery commonQueryDiv">
    <kunkka-ux-grid ... />
    <!-- 导出组件：无参无事件，打开由 Vuex daochu 模块驱动 -->
    <exportDialog />
  </div>
</template>
```

没有回调要写——导出成功后组件自己保存文件（`FileSaverDoExport` 流式写出），失败走 `request.js` 全局报错。

## 3. 弹窗内置能力（无需配置）

| 能力 | 说明 |
|------|------|
| 列选择 | 按当前模块表格列勾选是否导出 |
| 列排序 | el-table + sortablejs 拖拽调整导出列顺序 |
| 列宽 / 数据类型 | 每列可调导出宽与格式 |
| 导出类型 | 流式 / 一次性 / 自定义（选项定义在 [src/utils/select-options.js](../../../../../src/utils/select-options.js) 的 `exportType`） |

## 4. Props

| Prop | 说明 |
|------|------|
| `exportUrl` | 导出服务地址，默认 `process.env.VUE_APP_EXPORTURL`（一般不传；本地联调时 vue.config.js 把 `/expressExport` 代理到 localhost:3000 中转服务，见 `express/` 目录） |

## 5. 关键约定（踩坑高频点）

- **按钮必须配 `cStoremethod='daochu/show'`**：`list` mixin 按它筛选进 `tableAttrs.exportBtns`；配成别的 handle 会当普通按钮走页面 `toggleToolbarClick`，导出弹窗不弹。
- **弹窗打开条件**：`daochu.visible === true` 且按钮 `nButtonid` 属于当前模块导出按钮组——按钮要配在使用页面的模块下。
- **搜索条件自动带上**：导出查询用当前搜索栏条件（`formConfig.model`），用户先查再导。
- **大导出走流式**：默认建议流式（`exportType` 第一项），一次性导出大数据会卡。
- **别自己拼 Excel**：统一走本模块 + 后端导出服务，前端不引 xlsx 类库。

## 6. 关联资源

- **姊妹模块**：[import.md](./import.md)（导入，同一资源体系）
- **页面集成**：[query-list](../page-patterns/query-list.md) §3.3（模板里就有 `<exportDialog />` 位）
- **真实代码**：[src/template/queryListTemplate.vue](../../../../../src/template/queryListTemplate.vue)（`<exportDialog />` 标配位）
