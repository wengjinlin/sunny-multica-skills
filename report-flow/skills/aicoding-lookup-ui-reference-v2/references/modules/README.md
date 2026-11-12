# 成套业务模块参考

模块级**成套方案**：要么照官方模板改字段即用（弹窗组合模板），要么放个全局组件就完事（导入 / 导出自包含流程）。选型时这是**第 1 层**——命中即用，不要退回 [`../components/`](../components/) 的积木自己拼。

| 模块 | 组成 / 入口 | 文档 |
|---|---|---|
| 表单弹窗（新增 / 编辑 / 详情） | `formDialogTemplate.vue` + `@/mixins/formModal` | [form-modal.md](./form-modal.md) |
| 表单 + 明细表格弹窗 | `formTableDialogTemplate.vue` | [table-modal.md](./table-modal.md) |
| 多 Tab 明细弹窗 | `formTabsDialogTemplate.vue` + `@/mixins/formTabsModal` | [table-modal.md](./table-modal.md) §5 变体 |
| Excel 导入 | 全局 `<importDialog />` + 资源按钮 `daoru/show` | [import.md](./import.md) |
| Excel 导出 | 全局 `<exportDialog />` + 资源按钮 `daochu/show` | [export.md](./export.md) |

> 模板源头均在 [`src/template/`](../../../../../src/template/)（代码生成器官方模板，2024.12.10 定稿），零业务噪声 demo 在 [`src/views/demo/querylist/`](../../../../../src/views/demo/querylist/)。
>
> ⚠️ **没有匹配的标准模块时，用 `KunkkaModal` + 你需要的框架组件自行编排即可**——组件文档均在 [`../components/`](../components/)。弹窗就是「外壳 + 内部组件」，组合自由，不必死等模板。
>
> 页面级成套方案（查询列表页等）在 [`../page-patterns/`](../page-patterns/)。
