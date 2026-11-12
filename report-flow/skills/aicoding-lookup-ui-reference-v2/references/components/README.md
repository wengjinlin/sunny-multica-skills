# 框架组件参考

第 2 层「框架组件」的 API 速查（选型第 1 层模板 / 成套模块未覆盖时的积木）：kunkka-*（sunnygroup-components，全局注册）与工程内全局业务组件。**命中即强制使用，禁止用 Element 对应组件兜底**；两三层选型与强制规则见 [`../../SKILL.md`](../../SKILL.md)。

| 组件 | 一句话定位 | 文档 |
|---|---|---|
| `KunkkaModal` | 弹窗外壳（拖拽 / 全屏 / 底部按钮扩展位，所有弹窗强制用它） | [KunkkaModal.md](./KunkkaModal.md) |
| `KunkkaForm` | 资源 schema 驱动表单（所有表单场景强制） | [KunkkaForm.md](./KunkkaForm.md) |
| `KunkkaSearchDialog` | 公共查询弹窗（cNum 配置驱动，放大镜字段标配） | [KunkkaSearchDialog.md](./KunkkaSearchDialog.md) |
| `MulSearchDialog` | 多选搜索弹窗（增强拷贝：右侧已选栏 / 回显 / 去重） | [MulSearchDialog.md](./MulSearchDialog.md) |
| `KunkkaCustomizeSelect` | 自定义下拉（cNum 远程选项 / attrParam 级联） | [KunkkaCustomizeSelect.md](./KunkkaCustomizeSelect.md) |
| `KunkkaUxGrid` / `KunkkaYjyGrid` | 查询列表页表格主体（内嵌搜索栏 + 工具栏 + 分页） | [KunkkaUxGrid.md](./KunkkaUxGrid.md) |
| `CommonTable` | 可编辑明细表格（vxe 封装，弹窗内明细标准件，工程内置） | [CommonTable.md](./CommonTable.md) |
| `CommonFileUpload` + `FileList` | 附件上传 / 展示（两段式交互，工程内置） | [CommonFileUpload.md](./CommonFileUpload.md) |

> kunkka-* 组件权威源：`E:\kunkka组件库\kunkka`（`packages/components/llms*.txt`，只读参考）；实装版本以所在工程 `node_modules` 为准。工程内全局组件源码在 `src/components/Sunnyoptical/`（[src/plugins/sunnyoptical.js](../../../../../src/plugins/sunnyoptical.js) 注册）。
>
> 新增组件文档：复制 [`_template.md`](./_template.md) 按占位符填写。
>
> 成套方案（模板 / 导入导出）优先看 [`../modules/`](../modules/) 与 [`../page-patterns/`](../page-patterns/)，命中第 1 层就不要退回本层自己拼。
