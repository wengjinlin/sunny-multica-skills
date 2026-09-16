# 表格弹窗标准模板（table-modal）

> 弹窗内展示 / 编辑表格明细数据，本质是 **`SunnyModal` + `useTable`**（封装 `useSunnyEditGrid` + 字典自动加载）的组合。支持三种变体：只读查看、行内编辑、勾选返回。本模板自包含。

## 1. 何时使用

- 弹窗内查看明细数据（只读）
- 弹窗内行内编辑明细、新增/删除行（可编辑）
- 弹窗内勾选数据行后返回给父组件（可选择）

不适用：

- 整页查询列表 → 用页面模式（`useList`）
- 纯表单录入 → 用 [form-modal](./form-modal.md)
- 独立按钮弹窗选业务实体 → 用 `useBusinessSearchModal`

## 2. 文件结构

通常追加到已有模块：

```
src/api/{module}/index.ts                  # 追加 fetchDetailData / saveDetailData
src/views/{module}/{Name}TableModal.vue    # 表格弹窗组件（新增文件）
src/views/{module}/config.ts               # 追加 tableModalColumns + tableModalToolbarButtons
src/views/{module}/types.ts                # 追加明细行 VO（如 DemoItemVO）
```

## 3. 标准实现（可编辑模式，最常用）

### 3.1 API 追加

```typescript
/** 查询明细（按父行 ID） */
export function fetchDetailData(id: number) {
  return requestClient.post<ResponseResult<DemoItemVO[]>>('/{module}/detail', { id });
}

/** 保存明细 */
export function saveDetailData(data: DemoItemVO[]) {
  return requestClient.post<ResponseResult<void>>('/{module}/saveDetail', { detailList: data });
}
```

### 3.2 配置追加 — `config.ts`

可编辑列用 `EditRender.*` 声明编辑控件；字典列配 `selectOptions.dictCode`（useTable 自动加载）：

```typescript
import type { VxeGridProps } from '@sunny-base-web/ui';
import { EditRender } from '@sunny-base-web/ui';

/** 组合筛选默认项（FilterCombination 完整条件结构；工厂函数——每列独立 data，避免共享引用被 vxe 原地修改） */
const combinationFilter = () =>
  [{ data: { checks: [], sVal: '', sMenu: '', fType1: '', fVal1: '', fMode: 'and', fType2: '', fVal2: '' } }];

export const tableModalColumns: VxeGridProps['columns'] = [
  { type: 'checkbox', width: 50 },
  { type: 'seq', title: '序号', width: 60 },
  // 数据列默认统一配 FilterCombination 组合筛选（见 useSunnyEditGrid.md §3.6）
  { field: 'cName', title: '名称', minWidth: 150, ...EditRender.InputRender,
    filters: combinationFilter(), filterRender: { name: 'FilterCombination' } },
  { field: 'nStatus', title: '状态', width: 120, ...EditRender.SelectRender, selectOptions: { dictCode: 'STATUS' },
    filters: combinationFilter(), filterRender: { name: 'FilterCombination' } },
  { field: 'nQty', title: '数量', width: 100, ...EditRender.InputNumberRender, params: { min: 0 },
    filters: combinationFilter(), filterRender: { name: 'FilterCombination' } },
  // 业务搜索列：params.fieldNames 会触发对象数组↔字符串自动互转
  { field: 'cWlbm', title: '物料', minWidth: 160, ...EditRender.BusinessSearchRender,
    params: { cNum: 'COMMON_WL', multiple: false, displayField: 'cWlmc', fieldNames: { label: 'cWlmc', value: 'cWlbm' } } },
  // 附件列：编辑态渲染 SunnySimpleUpload（即选即传）；params 即组件 props。
  // 展示插槽默认是 JSON 原文，要显示文件名需覆盖 slots.default（见 components/SunnyUpload.md §3.3）
  { field: 'cFile', title: '附件', minWidth: 200, ...EditRender.UploadRender, params: { accept: '.pdf,.doc,.docx', limit: 3 } },
];

export const tableModalToolbarButtons = [
  { code: 'addRow', name: '新增行', status: 'primary' },
  { code: 'deleteRow', name: '删除行' },
];
```

### 3.3 弹窗组件 — `{Name}TableModal.vue`

```vue
<script setup lang="ts">
import { ref, watch } from 'vue';
import { Message } from '@arco-design/web-vue';
import { Modal, toStorageString } from '@sunny-base-web/ui';
import { useTable } from '@sunny-base-web/effects';
import { tableModalColumns, tableModalToolbarButtons } from './config';
import { fetchDetailData, saveDetailData } from '#/api/{module}';

defineOptions({ name: 'DemoTableModal' });

const props = defineProps<{ visible: boolean; editData?: { id: number } }>();
const emit = defineEmits<{ (e: 'update:visible', v: boolean): void; (e: 'success'): void }>();

const loading = ref(false);

const [Grid, gridApi] = useTable({
  columns: tableModalColumns,
  data: [],
  editable: true,
  editTrigger: 'click',
  editMode: 'cell',
  editRules: { cName: [{ required: true, message: '名称不能为空' }] },
  height: 400,
  gridId: 'demo-table-modal',
  toolbarButtons: tableModalToolbarButtons,
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

// 打开时按父行 ID 加载明细
watch(() => props.visible, async (visible) => {
  if (visible) await loadData();
}, { immediate: true });

async function loadData() {
  if (!props.editData?.id) return;
  loading.value = true;
  try {
    const { result } = await fetchDetailData(props.editData.id);
    gridApi.reloadData(result);
  } catch (error) {
    console.error('加载失败:', error);
  } finally {
    loading.value = false;
  }
}

async function handleOk() {
  const tableData = await gridApi.getFullData(); // 取全量数据（类型化方法，async；业务搜索列自动转字符串）
  if (tableData.length === 0) return Message.warning('请至少添加一条记录');
  // 附件列（UploadRender）行值是 JSON 字符串，提交前转成后端 "name:url,..." 格式
  const payload = tableData.map((row: any) => ({ ...row, cFile: toStorageString(row.cFile) }));
  await saveDetailData(payload);
  Message.success('保存成功');
  emit('success');
}
</script>

<template>
  <Modal :model-value="visible" title="明细编辑" :width="900" @ok="handleOk"
    @update:model-value="emit('update:visible', $event)">
    <a-spin :loading="loading" class="w-full">
      <Grid />
    </a-spin>
  </Modal>
</template>
```

## 4. 变体

### 4.1 只读模式（查看明细）

去掉编辑相关配置，列不加 `EditRender`：

```typescript
const [Grid] = useTable({
  columns: tableModalReadonlyColumns, // 列无 EditRender，纯展示
  data: [],
  editable: false,
  height: 400,
  gridId: 'demo-table-readonly',
});
```

> 也可以保留 `EditRender` 列 + `editable: false`（内部经 `beforeEditMethod` 否决，点不进编辑）；同一弹窗运行期在 view ↔ edit 之间切换时用 `gridApi.setEditable(value)`。

### 4.2 可选择模式（勾选返回）

第一列为 checkbox，确认时把勾选行 emit 给父组件：

```typescript
async function handleOk() {
  const selected = await gridApi.getCheckboxRecords(); // async
  emit('confirm', selected); // 父组件接收
}
```

```typescript
// 父组件
<DemoSelectModal v-model:visible="selectVisible" @confirm="(rows) => handleSelected(rows)" />
```

## 5. 关键约定

- **列配置一律写 `config.ts`，禁止内联在 `.vue` 里**：`tableModalColumns` / `tableModalToolbarButtons` 导出自模块 `config.ts`（见 §2、§3.2），弹窗 `.vue` 只 import。内联进 `.vue` 是生成错误。
- **弹窗受控用 `:model-value` + `@update:model-value`**：`SunnyModal` 没有 `visible` prop，传 `:visible` 会出现「能打开、关不掉」（详见 [SunnyModal.md](../components/SunnyModal.md) FAQ）。
- **可编辑列用 `EditRender.*`**：`InputRender` / `InputNumberRender` / `SelectRender` / `DatePickerRender` / `TextareaRender` / `SwitchRender` / `BusinessSearchRender` / `UploadRender`，spread 进列配置。
- **区域选择 / 复制粘贴为编辑表格内置能力**（弹窗内 Grid 自动获得）：单击=编辑+自动聚焦，拖动=区域选择，Ctrl+C/V=复制粘贴，拖填充柄=拖动复制；不可编辑列自动跳过。列配置无需任何新增项，详见 [useSunnyEditGrid.md §3.5](../components/useSunnyEditGrid.md)。
- **字典列**：配 `selectOptions.dictCode`，`useTable` 自动加载选项注入到列。
- **校验**：`editRules` + 提交前 `gridApi.validate()`（返回非 null 即有错）。详见 [useSunnyEditGrid.md](../components/useSunnyEditGrid.md)。
- **取数用 `await gridApi.getFullData()`**（类型化方法，async）：普通列直接返回全量行；业务搜索列（配了 `params.fieldNames`）自动把对象数组转字符串 + 回填 `displayField`。`getTableData().fullData` 运行期经 Proxy 可用但**无类型**，严格模式编译不过，别写在代码里。
- **附件列用 `EditRender.UploadRender`**：编辑态渲染 `SunnySimpleUpload`（即选即传，无「上传附件」按钮，不存在两段式丢文件问题）；行字段值是 **JSON 字符串**，展示插槽默认 `JSON.stringify` 原文（要显示文件名需覆盖 `slots.default`），提交前逐行 `toStorageString` 转换。详见 [SunnyUpload.md](../components/SunnyUpload.md)。
- **增删行**：`gridApi.addEvent(record, -1)`（末尾插入并自动进入编辑态）/ `await gridApi.deleteSelection()`（删勾选，`removeCheckboxRow` 的类型化封装）；不要自己调 vxe 原生 `insert`（见 [useSunnyEditGrid.md](../components/useSunnyEditGrid.md)）。
- **行内操作列**（每行一个删除/编辑按钮）：列配 `slots: { default: 'actionSlot' }` + `<Grid>` 里 `#actionSlot` 插槽，删行用 `gridApi.remove(row)`——见 [useSunnyEditGrid.md §3.4](../components/useSunnyEditGrid.md)。
- **工具栏按钮**：声明在 `toolbarButtons`（或资源驱动），点击在 `gridEvents.toolbarButtonClick` 按 `code` 分发；**禁止自己拼 div+按钮**。
- **弹窗内 loading**：异步加载明细用 `<a-spin :loading="loading">` 包裹 `<Grid />`。
- **错误不重复提示**：`requestClient` 已拦截，业务 `catch` 别再 `Message.error()`。

## 6. useTable 常用 api

| 方法 | 说明 |
|------|------|
| `reloadData(data)` | 加载数据（同时清状态） |
| `await getFullData()` | 取全量行（业务搜索列自动转字符串） |
| `await getCheckboxRecords()` | 取勾选行 |
| `addEvent(record, index)` | 插入行并进入编辑态（`-1` 末尾、`null` 第一行） |
| `await deleteSelection()` | 删除勾选行 |
| `await validate(full?)` | 校验，返回 null 表示通过 |
| `setColumns(cols)` / `setToolbarButtons(btns)` | 动态换列 / 换按钮 |
| `setEditable(value)` | 运行期切换只读 / 可编辑（view 详情模式；只读时配了 `EditRender` 的列也点不进编辑） |
| `$grid` | 原始 vxe-table 实例 |

> `useTable` 在 `useSunnyEditGrid` 基础上增强（`addEvent` 即来自它），未定义方法运行期经 Proxy 委托给 vxe 实例——**但委托方法没有类型**（如 `getTableData` / `removeCheckboxRow` 写了代码严格模式编译不过），请用上表的类型化方法。

## 7. 关联资源

- **组成组件**：[SunnyModal.md](../components/SunnyModal.md)、[useSunnyEditGrid.md](../components/useSunnyEditGrid.md)（`useTable` 是其上层封装）、[SunnyUpload.md](../components/SunnyUpload.md)（附件列）
- **页面集成**：[查询列表页标准模板](../page-patterns/query-list.md)（工具栏按钮打开弹窗）
