---
name: lookup-ui-reference
description: 前端 UI 选型速查手册：本仓库标准模块（弹窗 form-modal / table-modal / form-table-modal、导出 useExport、导入 useImport）、页面模板（query-list 查询列表页）、封装组件（SunnyForm / SunnyModal / SunnyBusinessSearch / SunnyCustomizeSelect / useSunnyEditGrid / useSunnyQueryGrid，来自 @sunny-base-web/ui），Arco 仅为最后兜底；只输出查阅结论，不生成业务代码。TRIGGER——写或评审任何 Vue 页面 / 弹窗 / 表单 / 表格 / 选择器 / 导入导出之前，或用户问「该用哪个组件」「有没有现成的」「参考哪个模式」「怎么写查询页 / 弹窗」，或排错定位（弹窗关不掉、回显异常、字典显示原始 ID、工具栏失效）时使用本技能，即使没点名要「查选型」。。
license: MIT
metadata:
  author: sunny-qms-web
  version: '1.2'
---

# 组件与模式选型参考

本技能是**项目前端 UI 的速查手册**：把标准模块（弹窗 / 导出等成套方案）、页面模板、封装组件沉淀成参考表，随时查阅「有没有现成方案」「该用哪个组件」「这个 bug 是不是用法错了」。只输出查阅结论，**不生成业务代码、不写文件**。

## 输入

`$ARGUMENTS` = 可选，用户的需求描述（如「查询列表」「表单弹窗」「一个下拉选择」「上传」）。未提供时直接按「快速定位」表给出候选并追问一句聚焦点，不要空转等待。

---

## 快速定位（任务 → 直接读哪一份）

| 用户要做的事 | 直接读 |
| ------------ | ------ |
| 查询列表页（搜索栏 + 表格 + 分页） | [`references/page-patterns/query-list.md`](references/page-patterns/query-list.md) |
| 新增 / 编辑弹窗（表单） | [`references/modules/form-modal.md`](references/modules/form-modal.md) |
| 弹窗内查看 / 编辑明细表格 | [`references/modules/table-modal.md`](references/modules/table-modal.md) |
| 弹窗内「表单 + 明细表格」一次提交（支持 add/edit/view 三模式） | [`references/modules/form-table-modal.md`](references/modules/form-table-modal.md) |
| 工具栏导出 Excel | [`references/modules/export.md`](references/modules/export.md) |
| 工具栏导入 Excel | [`references/modules/import.md`](references/modules/import.md) |
| 弹窗选择用户 / 角色 / 物料等业务实体 | [`references/components/SunnyBusinessSearch.md`](references/components/SunnyBusinessSearch.md) |
| 下拉选项随另一字段变化（级联 / 带附加参数） | [`references/components/SunnyCustomizeSelect.md`](references/components/SunnyCustomizeSelect.md) |
| 表单 / 表格里传附件（上传） | [`references/components/SunnyUpload.md`](references/components/SunnyUpload.md) |
| 任何表单（字段联动 / 字典 / 权限下拉） | [`references/components/SunnyForm.md`](references/components/SunnyForm.md) |
| 弹窗外壳 / 底部按钮 / 提交关闭时机 | [`references/components/SunnyModal.md`](references/components/SunnyModal.md) |
| 一块独立的可编辑 / 可查询表格 | [`references/components/useSunnyEditGrid.md`](references/components/useSunnyEditGrid.md)、[`references/components/useSunnyQueryGrid.md`](references/components/useSunnyQueryGrid.md) |
| 表格行内操作列（删除 / 编辑按钮） | [`references/components/useSunnyEditGrid.md`](references/components/useSunnyEditGrid.md) §3.4 |
| 表格区域选择 / 复制粘贴 / 拖动填充 / 组合筛选 | [`references/components/useSunnyEditGrid.md`](references/components/useSunnyEditGrid.md) §3.5–3.6 |
| 以上都不是的基础组件（Input / Tag / Tree / Tabs …） | 走下方第 3 层 Arco 兜底流程 |

---

## 选型决策（三层，自上而下，命中即停）

```
第 1 层 标准模块 / 页面模板（成套方案） → 第 2 层 封装组件（@ui 积木） → 第 3 层 Arco 原生
```

为什么分层：成套方案内置了布局 / 权限 / 事件分发体系（工具栏按钮资源注入、查询方案、字典自动加载），退回积木自拼会脱离这套体系、逐项踩坑；封装组件内置权限 / 字典 / 数据格式转换，Arco 原生没有。所以**上层命中就不用下层**。

### 第 1 层 — 标准模块 / 页面模板（成套方案，命中即用）

**模块级**（弹窗、导入导出等，[`references/modules/`](references/modules/)）：

| 业务场景 | 标准方案 | 文档（按需读） |
| -------- | -------- | -------------- |
| 表单弹窗（新增 / 编辑） | `SunnyModal` + `SunnyForm`（`useForm`） | [`references/modules/form-modal.md`](references/modules/form-modal.md) |
| 表格弹窗（明细查看 / 编辑 / 勾选返回） | `SunnyModal` + `useSunnyEditGrid`（`useTable`） | [`references/modules/table-modal.md`](references/modules/table-modal.md) |
| 表单 + 表格弹窗 | `SunnyModal` + `useFormTable` | [`references/modules/form-table-modal.md`](references/modules/form-table-modal.md) |
| Excel 导出 | `useExport`（`@sunny-base-web/effects`，自包含流程） | [`references/modules/export.md`](references/modules/export.md) |
| Excel 导入 | `useImport`（`@sunny-base-web/effects`，自包含流程） | [`references/modules/import.md`](references/modules/import.md) |

**页面级**（[`references/page-patterns/`](references/page-patterns/)）：

| 业务场景 | 标准方案 | 文档（按需读） |
| -------- | -------- | -------------- |
| 查询列表页 | `useList` + 四件套 | [`references/page-patterns/query-list.md`](references/page-patterns/query-list.md) |

> ⚠️ **没有匹配的标准模板时**：弹窗 = `SunnyModal` 外壳 + [`references/components/`](references/components/) 里需要的业务组件自行编排（组合自由，不必死等模板）；页面同理自行组合。导入 / 导出是自包含的，直接用，不需要组合。

### 第 2 层 — 封装组件（@sunny-base-web/ui）

第 1 层未覆盖时，用这些积木组装。封装了权限 / 字典 / 数据格式转换等业务逻辑，**命中则强制使用，禁止用 Arco 对应组件**：

| 业务场景   | 必须使用                            | API/用法详情（按需读）                                                                           |
| ---------- | ----------------------------------- | ------------------------------------------------------------------------------------------------ |
| 表单       | `SunnyForm`                         | [`references/components/SunnyForm.md`](references/components/SunnyForm.md)                       |
| 弹窗外壳   | `SunnyModal`（组件名 `Modal`）      | [`references/components/SunnyModal.md`](references/components/SunnyModal.md)                     |
| 业务搜索   | `SunnyBusinessSearch`               | [`references/components/SunnyBusinessSearch.md`](references/components/SunnyBusinessSearch.md)   |
| 自定义选择 | `SunnyCustomizeSelect`              | [`references/components/SunnyCustomizeSelect.md`](references/components/SunnyCustomizeSelect.md) |
| 上传       | `SunnyUpload` / `SunnySimpleUpload` | [`references/components/SunnyUpload.md`](references/components/SunnyUpload.md)                   |
| 可编辑表格 | `useSunnyEditGrid`                  | [`references/components/useSunnyEditGrid.md`](references/components/useSunnyEditGrid.md)         |
| 查询表格   | `useSunnyQueryGrid`                 | [`references/components/useSunnyQueryGrid.md`](references/components/useSunnyQueryGrid.md)       |
| 搜索弹窗   | `SunnySearchModal`                  | references/components/SunnySearchModal.md（待补，文件未创建）                                     |

> Vue 组件**不直接依赖 `requestClient`**，一律通过 API 层函数调用。

### 第 3 层 — 基础组件兜底（Arco Design Vue）

上两层都没有的基础组件（`Input` / `Select` / `DatePicker` / `Tag` / `Radio` / `Checkbox` / `Switch` / `Tree` / `Tabs` / `Steps` / `Pagination` / `Table` …）按顺序查：

1. `docs/src/public/llms.txt` 找是否有 Sunny 包装组件；
2. 没有 → `docs/src/public/arco-llm.txt` 找 Arco 原生（附官网链接）；
3. 完整 API/Props/Events → `docs/src/public/llms-full.txt`（Sunny）或 `docs/src/public/arco-llms-full.txt`（Arco）对应章节。

> ⚠️ `docs/src/public/` 下的 `llms*.txt` / `arco-llm*.txt` 由组件库自动生成（文件头标注 "Do not edit manually"），**只读、不要手改**；本仓库不含生成脚本，更新到 `@sunny-base-web/ui` 侧处理。

---

## 高频踩坑速查（排错定位）

| 症状 | 原因与解法 | 详见 |
| ---- | ---------- | ---- |
| 弹窗能打开、确定/取消关不掉 | 给 `SunnyModal` 传了 `:visible`；受控入口只有 `modelValue`，改 `:model-value` + `@update:model-value` | [SunnyModal.md](references/components/SunnyModal.md) |
| 业务搜索字段回显成序列化字符串 | 组件返回对象数组，`useForm` 必须配 `objectToValueFields: ['字段名']` | [SunnyBusinessSearch.md](references/components/SunnyBusinessSearch.md) |
| 字典下拉显示原始 ID 而非标签 | 字典 value 恒为字符串（联动比较 / 默认值都用 string，不能 `=== 1`），且需等字典加载完成后再赋默认值 | [SunnyForm.md](references/components/SunnyForm.md)、[rules/packages/ui.md](../../rules/packages/ui.md) §8.7–8.8 |
| 自拼 `<div>` + 按钮工具栏后，刷新 / 列自定义 / 权限全失效 | 工具栏按钮必须走 `toolbarConfig.buttons` 声明 + `gridEvents.toolbarButtonClick` 按 `code` 分发 | [query-list.md](references/page-patterns/query-list.md) |
| 工具栏按钮看得见、点击毫无反应（handler 不触发） | 按钮 code 为空（资源表 `C_STOREMETHOD` 未回填）或撞 vxe 保留字（`import`/`export`/`print`/`zoom`/`refresh`/`custom` 等）——vxe 静默拦截；导入用 `daoru/show`、导出用 `daochu/show` | [query-list.md](references/page-patterns/query-list.md) |
| 表格编辑列提交后丢显示字段 / 值格式错乱 | 业务搜索列（配了 `params.fieldNames`）取数用 `gridApi.getFullData()`（自动对象数组↔字符串互转），别手动转换 | [useSunnyEditGrid.md](references/components/useSunnyEditGrid.md) |
| 表格代码运行正常但 vue-tsc 报 `Property 'getTableData'/'removeCheckboxRow' does not exist` | `gridApi` 未定义方法运行期经 Proxy 委托 vxe 实例但**无类型**：取数用 `await getFullData()`、取勾选用 `await getCheckboxRecords()`、删勾选用 `await deleteSelection()` | [table-modal.md](references/modules/table-modal.md) |
| 弹窗校验失败仍然关闭 | `@ok` 是提交即自动关闭；要「失败保留弹窗」改 `:on-before-ok` 并在失败时 `return false` | [form-modal.md](references/modules/form-modal.md) |
| 弹窗内表格高度逐轮缩小 / 无限变长 | Grid 的 `height:'auto'` 取**父元素**高度，父链不定高时与内容高度互相反馈成循环。⚠️ SunnyModal 常态 body **非定高**（弹窗由内容撑开、仅 max-height 封顶），纯三层 flex 链 + `h-full` 常态无效。正解：常态根容器固定高度（`h-[520px]`）；最大化时弹窗才定高，用 `@fullscreen-change` 同步状态切回 `h-full` 填满（确认/取消关闭时 Modal 内部复位最大化**不发**该事件，须在 `visible=false` 分支复位本地 ref）；不需要跟随弹窗高度就传 `useFormTable` 的 `tableHeight: 400` | [form-table-modal.md](references/modules/form-table-modal.md) §3.3 |
| 导入/导出弹窗请求 401 / token 失效 | 弹窗请求走了裸 axios 兜底（不带 token）：应用入口须调 `setupImportExport()`（`@sunny-base-web/effects`）注入基于 requestClient 的 `importAdapter` / `exportAdapter`，且在 `setupBusinessForm` **之后**调用（其配置全量重算会清掉未传的键）。apps/web 已配置 | [import.md](references/modules/import.md)、[export.md](references/modules/export.md) |
| SunnyUpload 选了附件保存后文件丢了 | 两段式组件：选文件只入本地暂存，**必须点「上传附件」**；没上传的文件不进表单值，提交时被 `toStorageString` 静默丢弃 | [SunnyUpload.md](references/components/SunnyUpload.md) |
| 页面弹出重复错误提示 | `requestClient` 已全局拦截报错，业务 `catch` 里不要再 `Message.error()` | [query-list.md](references/page-patterns/query-list.md) |

---

## 查找流程

1. **识别意图** — 做「一块 UI」（页面 / 弹窗 / 字段 / 表格 / 导入导出）、确认选型，还是排错。
2. **定位** — 先查「快速定位」表，命中即得答案与该读的那一份文档；未命中按「选型决策」三层表自上而下推荐；排错先查「高频踩坑速查」。
3. **按需深读** — 只有需要完整 API / 示例代码 / 元数据时才读对应 references 文件或 `docs/src/public`；普通问题用本文件表内信息即可回答。
4. **只输出查阅结论** — 推荐「用哪个方案 / 哪个组件 / 参考在哪」，不生成业务代码。用户确认后要写代码，交给生成类技能（见上方边界表）。

## 输出格式

简洁、事实化，每条推荐给出可点击的路径：

```
推荐方案：<模块/模板名>（命中第 1 层）或 推荐组件：<组件名>（来自 <库>）
理由：<一句话>
深入查阅：<文件路径>
```

## 规则

- **只读**：不写文件、不生成业务代码、不修改 `docs/src/public` 下的 llm 文档。
- **配置集中**：表单 Schema（`searchFormSchema` / `addFormSchema` / `formTableFormSchema` …）与表格列（`tableColumns` / `tableModalColumns` …）一律写在模块 `config.ts` 导出，**禁止内联在 `.vue` 里**；`.vue` 只负责 import、状态与事件分发（各模板 §2 文件结构为准）。
- **选型优先级**：三层自上而下——标准模块 / 页面模板 > 封装组件（命中即强制，禁止 Arco 对应组件兜底）> Arco 原生。上层命中禁止退回下层自己拼。
- **路径准确**：只引用实际存在的目录/文件。
- **查无匹配**：如实说明，并给兜底建议（Arco 基础组件 / 最接近的标准模板），不要编造不存在的组件或模式。
- **自包含参考**：`references/` 下是自包含参考文档——`modules/`（标准业务模块）、`page-patterns/`（页面模板）、`components/`（封装组件 API），按需读对应那份即可；`docs/src/public` 下的 llm 文档是组件库自动生成的 API 源（只读、对账用）。
