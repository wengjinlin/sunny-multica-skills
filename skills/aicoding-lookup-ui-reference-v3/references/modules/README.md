# 标准业务模块参考

模块级**成套方案**：要么照模板改字段即用（组合模板），要么直接调用（自包含流程）。选型时这是**第 1 层**——命中即用，不要退回 [`../components/`](../components/) 的积木自己拼。

两类模块：

| 类型 | 含义 | 现有 |
|---|---|---|
| 组合模板 | `SunnyModal` 外壳 + 业务组件的标准组合，照着改字段生成 | form-modal / table-modal / form-table-modal |
| 自包含流程 | 一个 hook 内置完整流程，声明后调 `open` 即用 | export（`useExport`）/ import（`useImport`） |

| 模块 | 组成 / 入口 | 文档 |
|---|---|---|
| 表单弹窗 | `SunnyModal` + `SunnyForm`（`useForm`） | [form-modal.md](./form-modal.md) |
| 表格弹窗 | `SunnyModal` + `useSunnyEditGrid`（`useTable`） | [table-modal.md](./table-modal.md) |
| 表单+表格弹窗 | `SunnyModal` + `useFormTable` | [form-table-modal.md](./form-table-modal.md) |
| Excel 导出 | `useExport`（`@sunny-base-web/effects`） | [export.md](./export.md) |
| Excel 导入 | `useImport`（`@sunny-base-web/effects`） | [import.md](./import.md) |

> ⚠️ **没有匹配的标准模块时，用 `SunnyModal` + 你需要的业务组件自行编排即可**——组件文档均在 [`../components/`](../components/)。弹窗就是「外壳 + 内部组件」，组合自由，不必死等模板。
>
> 页面级成套方案（查询列表页等）在 [`../page-patterns/`](../page-patterns/)。
