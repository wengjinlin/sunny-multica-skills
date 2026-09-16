# 表单+表格弹窗标准模板（form-table-modal）

> 弹窗内同时收集**主表单 + 明细可编辑表格**，一次提交。本质是 `useFormTable`（封装 `useSunnyForm` + `useSunnyEditGrid` + 表单/表格字典与权限自动加载）。本模板自包含。

## 1. 何时使用

- 一次提交「单头表单 + 多行明细」结构（如订单头 + 订单行、检验单 + 检验项）
- 表单字段 + 明细行都需要录入 / 编辑
- 同一弹窗复用新增 / 编辑 / **只读查看**（三模式；view 模式表格只读、隐藏增删行按钮，见 §5）

不适用：

- 纯表单（无明细表格）→ 用 [form-modal](./form-modal.md)
- 纯表格（无主表单）→ 用 [table-modal](./table-modal.md)

## 2. 文件结构

追加到已有模块：

```
src/api/{module}/index.ts                    # 追加 fetchFormTableDetail / saveFormTableData
src/views/{module}/{Name}FormTableModal.vue  # 弹窗组件（新增文件）
src/views/{module}/config.ts                 # 追加 formTableFormSchema + formTableColumns + buttons
src/views/{module}/types.ts                  # 追加明细行 VO（DemoItemVO）
```

## 3. 标准实现

### 3.1 API 追加

后端通常是 `{ header, details }` 结构：

```typescript
/** 查询表单+表格详情 */
export function fetchFormTableDetail(id: number) {
  return requestClient.post<ResponseResult<{ header: Record<string, any>; details: DemoItemVO[] }>>(
    '/{module}/formTableDetail',
    { id },
  );
}

/** 保存表单+表格 */
export function saveFormTableData(data: { header: Record<string, any>; details: DemoItemVO[] }) {
  return requestClient.post<ResponseResult<void>>('/{module}/saveFormTable', data);
}
```

### 3.2 配置追加 — `config.ts`

表单 Schema 同 form-modal；表格列同 table-modal（`EditRender.*` 或原生 `editRender` 均可）：

```typescript
import type { VxeGridProps, FormSchema } from '@sunny-base-web/ui';
import { EditRender } from '@sunny-base-web/ui';

// 表单（主信息）
// 非必填字段默认挂「只看必填项」开关（__onlyRequired 为 useFormTable 保留上下文字段，勿占用）；
// 必填字段（rules: 'required'）不挂，恒显
export const formTableFormSchema: FormSchema[] = [
  { fieldName: 'cName', label: '名称', component: 'Input', rules: 'required', componentProps: { placeholder: '请输入名称', allowClear: true } },
  { fieldName: 'nStatus', label: '状态', component: 'Select', selectOptions: { dictCode: 'SFQY' },
    dependencies: { show: (v: any) => !v.__onlyRequired } },
  { fieldName: 'dDate', label: '日期', component: 'DatePicker',
    dependencies: { show: (v: any) => !v.__onlyRequired } },
  // 附件字段：action/downAction 全局已配；两段式（选完需点「上传附件」），见 components/SunnyUpload.md
  { fieldName: 'cAttachment', label: '附件', component: 'SunnyUpload',
    dependencies: { show: (v: any) => !v.__onlyRequired },
    componentProps: { accept: '.pdf,.doc,.docx,.xls,.xlsx', limit: 5, maxSize: 10 },
    colProps: { span: 16 } },
];

/** 组合筛选默认项（FilterCombination 完整条件结构；工厂函数——每列独立 data，避免共享引用被 vxe 原地修改） */
const combinationFilter = () =>
  [{ data: { checks: [], sVal: '', sMenu: '', fType1: '', fVal1: '', fMode: 'and', fType2: '', fVal2: '' } }];

// 表格（明细，可编辑；数据列默认统一配 FilterCombination 组合筛选，见 useSunnyEditGrid.md §3.6）
export const formTableColumns: VxeGridProps['columns'] = [
  { type: 'checkbox', width: 50 },
  { type: 'seq', title: '序号', width: 60 },
  { field: 'cName', title: '名称', minWidth: 150, ...EditRender.InputRender,
    filters: combinationFilter(), filterRender: { name: 'FilterCombination' } },
  { field: 'nStatus', title: '状态', width: 120, ...EditRender.SelectRender, selectOptions: { dictCode: 'STATUS' },
    filters: combinationFilter(), filterRender: { name: 'FilterCombination' } },
  { field: 'nQty', title: '数量', width: 100, ...EditRender.InputNumberRender, params: { min: 0 },
    filters: combinationFilter(), filterRender: { name: 'FilterCombination' } },
  // 附件列：编辑态渲染 SunnySimpleUpload（即选即传）；展示默认 JSON 原文，见 components/SunnyUpload.md §3.3
  { field: 'cFile', title: '附件', minWidth: 200, ...EditRender.UploadRender, params: { accept: '.pdf,.doc,.docx', limit: 3 } },
];

export const formTableToolbarButtons = [
  { code: 'addRow', name: '新增行', status: 'primary' },
  { code: 'deleteRow', name: '删除行' },
];
```

### 3.3 弹窗组件 — `{Name}FormTableModal.vue`

```vue
<script setup lang="ts">
import { ref, watch } from 'vue';
import { Message } from '@arco-design/web-vue';
import { Modal, toStorageString, fromStorageString } from '@sunny-base-web/ui';
import { useFormTable } from '@sunny-base-web/effects';
import { formTableFormSchema, formTableColumns, formTableToolbarButtons } from './config';
import { fetchFormTableDetail, saveFormTableData } from '#/api/{module}';
import type { DemoItemVO } from './types';

defineOptions({ name: 'DemoFormTableModal' });

const props = defineProps<{ visible: boolean; editData?: { id: number } }>();
const emit = defineEmits<{ (e: 'update:visible', v: boolean): void; (e: 'success'): void }>();

const loading = ref(false);

// 弹窗最大化状态：最大化时弹窗定高，内容根容器切 h-full 填满剩余高度（见模板注释）；
// ⚠️ 确认/取消关闭时 Modal 内部复位最大化但不发 fullscreen-change，须在 visible=false 分支同步复位
const maximized = ref(false);

// 返回七元组：[Form, formApi, Grid, gridApi, onlyRequired, layout, formWidth]
// - onlyRequired：「只看必填项」开关，v-model 到底部 checkbox
// - layout：'vertical'（上下，默认）| 'horizontal'（左右），绑定到布局切换按钮
// - formWidth：左右布局 Form 面板宽度，v-model:width 绑 a-resize-box
const [Form, formApi, Grid, gridApi, onlyRequired, layout, formWidth] = useFormTable({
  formSchema: formTableFormSchema,
  tableColumns: formTableColumns,
  tableToolbarButtons: formTableToolbarButtons,
  tableEditRules: { cName: [{ required: true, message: '名称不能为空' }] },
  tableHeight: 'auto',   // 'auto'=填满父容器（弹窗内接通 flex 链即可占剩余高度）；也可传固定高度如 400
  formWidth: 450,        // 左右布局 Form 初始宽度 ≈ 弹窗 900 的一半（ResizeBox 可拖）
  objectToValueFields: [], // 表单含业务搜索字段时填入
  gridEvents: {
    async toolbarButtonClick(params: any) {
      if (params.button.code === 'addRow') {
        gridApi.addEvent({}, -1); // 末尾插入空行（自动进入编辑态）
      } else if (params.button.code === 'deleteRow') {
        const checked = await gridApi.getCheckboxRecords(); // 类型化方法，注意是 async
        if (checked.length === 0) return Message.warning('请至少选择一条记录');
        await gridApi.deleteSelection(); // 删除勾选行（removeCheckboxRow 的类型化封装）
      }
    },
  },
});

// 打开时重置；编辑模式加载
watch(
  () => props.visible,
  async (visible) => {
    if (!visible) {
      maximized.value = false; // Modal 关闭时内部复位最大化但不发 fullscreen-change，同步复位
      return;
    }
    formApi.resetForm();
    gridApi.reloadData([]);
    onlyRequired.value = false; // 复位「只看必填项」（hook 内部自动恢复表单上下文与全量列）
    if (props.editData?.id) await loadData();
  },
  { immediate: true },
);

async function loadData() {
  loading.value = true;
  try {
    const { result } = await fetchFormTableDetail(props.editData!.id);
    formApi.setValues({
      ...result.header,
      // 附件字段（SunnyUpload）：后端 "name:url,..." → 组件 JSON 字符串
      cAttachment: fromStorageString(result.header.cAttachment),
    });
    gridApi.reloadData(result.details); // 回填表格
  } catch (error) {
    console.error('加载失败:', error);
  } finally {
    loading.value = false;
  }
}

// 提交：校验表单 → 取表单值 + 表格值
async function handleBeforeOk() {
  const { valid } = await formApi.validate(); // 1. 校验表单
  if (!valid) return false;
  // 需要时再校验表格：const errMap = await gridApi.validate(); if (errMap) return false;
  const formValues = await formApi.getValues();        // 2. 取表单值
  const tableData = await gridApi.getFullData();       // 3. 取表格值（类型化方法，async）
  if (tableData.length === 0) {
    Message.warning('请至少添加一条明细');
    return false;
  }
  // 附件字段两侧都要转后端 "name:url,..." 格式（未点「上传附件」的表单附件此时会被丢弃）
  await saveFormTableData({
    header: { ...formValues, cAttachment: toStorageString(formValues.cAttachment) },
    details: tableData.map((row: any) => ({ ...row, cFile: toStorageString(row.cFile) })) as DemoItemVO[],
  });
  Message.success('保存成功');
  emit('success');
  return true; // 返回 true 关闭弹窗
}
</script>

<template>
  <Modal
    :model-value="visible"
    :title="editData ? '编辑' : '新增'"
    :width="900"
    :on-before-ok="handleBeforeOk"
    @update:model-value="emit('update:visible', $event)"
    @fullscreen-change="maximized = $event"
  >
    <!-- 高度方案（勿简化回纯 h-full）：SunnyModal 弹窗常态由内容撑开（仅 max-height 封顶），body 非定高，
         Grid 的 height:'auto'（填满父容器）在不定高父链里与内容高度互相反馈 → 表格逐轮缩小或无限增高。
         常态：根容器固定高度（值 ≈ 表单高 + 期望表格高）；最大化：弹窗定高，切回 h-full 真正填满，
         状态由 @fullscreen-change 同步（⚠️ 关闭时 Modal 内部复位最大化但不发该事件，须自行复位） -->
    <div class="flex flex-col" :class="maximized ? 'h-full' : 'h-[520px]'">
      <Form />
      <a-spin :loading="loading" class="w-full flex-1 min-h-0">
        <!-- Form 和 Grid 分别渲染，没有「自动含表格」的合并组件 -->
        <Grid class="h-full" />
      </a-spin>
    </div>

    <!-- 底部最左：「只看必填项」开关（默认必备）；flex-1 把取消/确认推回右侧 -->
    <template #insertFooter>
      <a-checkbox v-model="onlyRequired" class="mr-3">只看必填项</a-checkbox>
      <div class="flex-1" />
    </template>
  </Modal>
</template>
```

## 4. 关键约定

- **配置一律写 `config.ts`，禁止内联在 `.vue` 里**：`formTableFormSchema` / `formTableColumns` / `formTableToolbarButtons` 全部导出自模块 `config.ts`（见 §2 文件结构、§3.2），弹窗 `.vue` 只 `import { ... } from './config'` + 写状态与事件分发。Schema 内联进 `.vue` 是生成错误，必须重构成 config.ts 导出。
- **Grid 占「弹窗剩余高度」＝常态固定高度 + 最大化切 `h-full`**（§3.3 模板已含，勿简化成纯 `h-full`）。⚠️ 前提纠偏（曾据此踩坑）：SunnyModal 弹窗**常态没有确定高度**——整体由内容撑开、仅 `max-height: calc(100vh - 40px)` 封顶，body 的 `flex:1 + min-height:0` 只在弹窗定高（**最大化**或内容超限出滚动）时才给出确定高度。vxe `height:'auto'` 取 **Grid 父元素的 computedStyle.height**（自动减去工具栏/分页高度），父链不定高时与内容高度互相反馈成循环（症状：**表格逐轮缩小**或无限增高）。因此：常态根容器固定高度（`h-[520px]`，值 ≈ 表单高 + 期望表格高）；最大化时根容器切 `h-full`（弹窗定高，链真正生效），状态用 Modal 的 `@fullscreen-change` 同步，并注意**确认/取消关闭时 Modal 内部复位最大化但不发该事件**，必须在 `visible=false` 分支复位本地 ref，否则重开弹窗带着 `h-full` 进常态、循环复发。不需要「跟随弹窗高度」语义时直接传 `tableHeight: 400` 固定高度最简单。真实参照：`packages/@effects/src/views/setting/dataDictionary/DataDictionaryAdd.vue`。
- **`a-spin` 放进链里的规则**：它不断链（arco-vue 的 spin 子内容直接渲染，无包装层），但必须给它自己挂高度类——loading 盖 Form+Grid 时当第一层（`class="w-full h-full"` 包住整个 flex 链），只盖表格时当中间层（`class="w-full flex-1 min-h-0"` 替代 Grid 外层 div）。裸 `class="w-full"`（无高度）即断链。
- **弹窗受控用 `:model-value` + `@update:model-value`**：`SunnyModal` 没有 `visible` prop，传 `:visible` 会出现「能打开、关不掉」（详见 [SunnyModal.md](../components/SunnyModal.md) FAQ）。
- **返回五元组 `[Form, formApi, Grid, gridApi, onlyRequired]`**：`Form`（表单组件）和 `Grid`（表格组件）要**分别渲染**——没有「自动含表格的合并组件」；`onlyRequired` 是「只看必填项」开关 ref（见下条）。
- **「只看必填项」默认必备**（用户体验标准项，§3.3 模板已含）：footer `#insertFooter` 放 `<a-checkbox v-model="onlyRequired">` + `flex-1` 占位。机制：开关写 `__onlyRequired` 保留上下文字段 → config.ts 里非必填字段的 `dependencies.show` 响应隐藏；表格侧按 `tableEditRules` 的 key 过滤非必填数据列（checkbox/seq 保留）整体换列恢复。**仅过滤视图，隐藏字段值仍参与提交**；打开弹窗时复位 `onlyRequired.value = false`。业务 schema 勿占用 `__onlyRequired` 字段名。真实参照：`packages/@effects/src/views/setting/dataDictionary/DataDictionaryAdd.vue`。
- **表单 + 表格字典都自动加载**：`useFormTable` 内部对 formSchema 和 tableColumns 的 `selectOptions.dictCode` 都做了声明式加载，无需手动。
- **三模式（add / edit / view）**：打开前 `gridApi.setEditable(mode !== 'view')` + `setToolbarButtons(view ? [] : buttons)`；固定只读的弹窗直接传 `tableEditable: false`（见 §5 变体）。
- **行内操作列**（每行删除/编辑按钮）：列配 `slots: { default: 'actionSlot' }` + `<Grid>` 里 `#actionSlot` 插槽直接绑函数，删行 `gridApi.$grid?.remove(row)`——见 [useSunnyEditGrid.md §3.4](../components/useSunnyEditGrid.md)。
- **区域选择 / 复制粘贴为编辑表格内置能力**（弹窗内 Grid 自动获得，列配置零新增）：单击=编辑+自动聚焦，拖动=区域选择，Ctrl+C/V、拖填充柄均可复制；不可编辑列自动跳过。详见 [useSunnyEditGrid.md §3.5](../components/useSunnyEditGrid.md)。
- **工具栏事件走 `gridEvents`**：在 options 里传 `gridEvents.toolbarButtonClick`，按 `code` 分发（addRow/deleteRow，可做删除前空勾选拦截）。
- **提交用 `:on-before-ok`**：先 `formApi.validate()` 校验表单，再 `formApi.getValues()` + `await gridApi.getFullData()`，校验失败 `return false` 不关闭。
- **编辑回填分两步**：`formApi.setValues(header)` + `gridApi.reloadData(details)`；打开时先 `resetForm()` + `reloadData([])` 清空。
- **取数统一用 `await gridApi.getFullData()`**：表格列配了 `params.fieldNames` 时自动对象数组→字符串；普通列直接返回全量行（`getTableData().fullData` 无类型，严格模式编译不过，别用）。
- **附件两端用法不同**：表单字段用 `SunnyUpload`（两段式，选完需点「上传附件」，未上传的文件提交时被 `toStorageString` 丢弃）；表格列用 `EditRender.UploadRender`（渲染 `SunnySimpleUpload`，即选即传）。两者字段值都是 JSON 字符串，与后端 `"name:url,..."` 的互转**只发生在边界**（回填前 `fromStorageString` / 提交前 `toStorageString`）。详见 [SunnyUpload.md](../components/SunnyUpload.md)。
- **错误不重复提示**：`requestClient` 已拦截，业务 `catch` 别再 `Message.error()`。

## 5. 变体：三模式弹窗（add / edit / view）

同一弹窗组件复用新增 / 编辑 / 查看：打开前按模式调 `gridApi.setEditable` + `gridApi.setToolbarButtons`，view 模式底部只留「关闭」：

```typescript
type ModalMode = 'add' | 'edit' | 'view';
const mode = ref<ModalMode>('add');

/** 打开弹窗（子组件 defineExpose 暴露给父组件） */
function open(target: ModalMode, editData?: { id: number }) {
  mode.value = target;
  formApi.resetForm();
  gridApi.reloadData([]);
  // view 模式：表格只读 + 隐藏增删行按钮；add/edit 恢复可编辑
  gridApi.setEditable(target !== 'view');
  gridApi.setToolbarButtons(target === 'view' ? [] : formTableToolbarButtons);
  if (target !== 'add' && editData?.id) void loadData(editData.id);
  visible.value = true;
}
```

```vue
<Modal
  :model-value="visible"
  :title="{ add: '新增', edit: '编辑', view: '查看' }[mode]"
  :width="900"
  :ok-text="mode === 'view' ? '关闭' : undefined"
  :hide-cancel="mode === 'view'"
  :on-before-ok="mode === 'view' ? undefined : handleBeforeOk"
  @update:model-value="visible = $event"
>
  <!-- 布局同 §3.3：三层 flex 链，Grid 占弹窗剩余高度 -->
  <div class="h-full flex flex-col">
    <Form />
    <div class="flex-1 min-h-0">
      <Grid class="h-full" />
    </div>
  </div>
</Modal>
```

> 只读是 `editConfig.beforeEditMethod` 层面的否决——即使列配了 `EditRender`，view 模式单元格也点不进编辑；固定只读的独立弹窗直接传 `tableEditable: false` 更简单。表单字段的只读可在 schema 里用函数式 `componentProps: () => ({ disabled: mode.value === 'view' })`。

### 5.1 仅新增（无编辑 / 查看）

场景只需新增（如「新增字典 + 额外属性行」）时：**去掉 `mode` / `editData` 与三模式逻辑**（`setEditable` / `setToolbarButtons` 都不需要），props 换成业务上下文参数（如 `parentId` / `parentName`），提交只调 insert，模板布局与 §3.3 完全一致。真实参照：`packages/@effects/src/views/setting/dataDictionary/DataDictionaryAdd.vue`。

## 6. useFormTable API

**Options**

| 属性 | 类型 | 说明 |
|------|------|------|
| `formSchema` | `FormSchema[]` | 表单配置 |
| `tableColumns` | `VxeGridProps['columns']` | 表格列（`EditRender.*` 或原生 `editRender`） |
| `tableEditRules` | `any` | 表格校验规则 |
| `tableToolbarButtons` | `{ code; name }[]` | 表格工具栏按钮 |
| `objectToValueFields` | `string[]` | 表单业务搜索字段（对象数组取值） |
| `gridEvents` | `Record<string, Function>` | 表格事件（`toolbarButtonClick` 等，可做删除行前空勾选拦截） |
| `aggregateConfig` | `{ groupFields?; ... }` | 聚合 / 行分组 |
| `tableEditable` | `boolean` | 表格是否可编辑，默认 `true`；view/详情弹窗传 `false`（运行期切换用 `setEditable`） |
| `tableEditTrigger` | `'click' \| 'dblclick'` | 编辑触发方式，默认 `'click'` |
| `tableEditMode` | `'cell' \| 'row'` | 编辑模式，默认 `'cell'` |
| `gridId` | `string` | 表格 ID（列自定义持久化 key），默认 `'meta-grid'`；同页多表格必传 |
| `tableHeight` | `string \| number` | 表格高度，默认 `'auto'`（填满父容器，父元素须有确定高度——弹窗内父链常态不定高，高度方案见 §3.3/§4）；不需要跟随弹窗高度语义时传固定高度（如 `400`） |
| `formWidth` | `number` | 左右布局时 Form 面板初始宽度（px），默认 `350`；**建议传弹窗宽度的一半**（如弹窗 700 传 350、960 传 480），ResizeBox 可拖拽调整 |

**返回 `[Form, formApi, Grid, gridApi, onlyRequired, layout, formWidth]`**

| 返回 | 方法/说明 |
|------|-----------|
| `Form` | 表单组件，`<Form />` 渲染 |
| `formApi` | `validate` / `getValues` / `setValues` / `setFieldValue` / `resetForm`（详见 [SunnyForm.md](../components/SunnyForm.md)） |
| `Grid` | 表格组件，`<Grid />` 渲染 |
| `gridApi` | `reloadData` / `getFullData` / `getCheckboxRecords` / `addEvent` / `deleteSelection` / `validate` / `setEditable` / `setToolbarButtons` / `setColumns` / `$grid`（除 `reloadData`/`addEvent` 外取数、删行均为 **async**；详见 [useSunnyEditGrid.md](../components/useSunnyEditGrid.md)） |
| `onlyRequired` | `Ref<boolean>`「只看必填项」开关，`v-model` 到 footer checkbox；机制见 §4 关键约定 |
| `layout` | `Ref<'vertical' \| 'horizontal'>` 布局切换：上下（默认）↔ 左右；绑定到 footer 切换按钮 |
| `formWidth` | `Ref<number>` 左右布局 Form 面板宽度，`v-model:width` 绑到 `a-resize-box`；初始值来自 Options.formWidth |

## 7. 关联资源

- **组成组件**：[SunnyForm.md](../components/SunnyForm.md)（formApi）、[useSunnyEditGrid.md](../components/useSunnyEditGrid.md)（gridApi）、[SunnyModal.md](../components/SunnyModal.md)、[SunnyUpload.md](../components/SunnyUpload.md)（表单附件字段 + 明细附件列）
- **同类模板**：[form-modal](./form-modal.md)（纯表单）、[table-modal](./table-modal.md)（纯表格）
- **页面集成**：[查询列表页标准模板](../page-patterns/query-list.md)
