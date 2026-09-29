# 页面模式参考

页面级业务页面的标准实现模板（选型**第 1 层**：命中即用，不要用组件层积木自己拼）。模板源头是代码生成器官方模板 [`src/template/`](../../../../../src/template/)，每个模板自包含（文件结构 + 代码骨架 + 关键约定），照着改 `name` / `modnumb` / api 即可生成；配套零业务噪声 demo 在 [`src/views/demo/querylist/`](../../../../../src/views/demo/querylist/)。

| 页面类型 | 标准模板 | 说明 |
|---|---|---|
| 查询列表页 | [query-list.md](./query-list.md) | `queryListTemplate.vue` + `list` mixin：搜索栏 + 表格 + 分页 + 工具栏 + 导入导出，全资源驱动 |

**待添加**：表单页、左右分栏、Tab 页（`@/mixins/tabs`）等。

> 弹窗类模板（表单弹窗 / 表单+表格弹窗 / 多 Tab 弹窗）归在 [`../modules/`](../modules/)。
