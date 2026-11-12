# 查询列表页标准模板

> 最常见的业务页面类型：顶部搜索栏 + 数据表格 + 分页，可选查询方案、批量操作、导出。本模板自包含，照着改字段即可生成一个标准查询页。
>
> 核心 Hook：`useList`（`@sunny-base-web/effects`）

## ⚠️ 工具栏按钮规则（最高频踩坑，先看这条）

**页面级按钮（新增/删除/导出）一律走 useList 的 `toolbarConfig.buttons`，绝不自己写 `<div>` + 按钮拼工具栏。** 自写工具栏会脱离 useList 的布局、权限、事件分发体系，是查询页第一类错误。

- **正常业务（有后端）**：按钮由后端资源系统按 `resourceConfig` 注入，前端**不声明按钮**，只在 `gridEvents.toolbarButtonClick` 里按 `params.button.code` 分发。
- **原型 / 无后端**：前端本地写死 `toolbarConfig.buttons`，结构最小为 `[{ code: 'add', name: '新增' }]`；事件分发同样走 `gridEvents.toolbarButtonClick`。**仍然不许自写 `<div>` 工具栏** —— 哪怕原型，也走 toolbarConfig。
- **⚠️ 按钮 code 两条铁律**（资源表 `C_STOREMETHOD` 字段 → `params.button.code`）：
  1. **不能为空**——vxe 工具栏点击守卫 `if (code)` 会静默 return，按钮看得见、点了没任何反应（`DefaultButtonResource` 种子里 add/edit/del 的 `cStoremethod` 默认为空，建资源时必须回填）；
  2. **不能撞 vxe 保留字** `import` / `export` / `print` / `open_import` / `open_export` / `open_print` / `custom` / `zoom` / `refresh`——vxe 会静默拦截自己处理，`toolbarButtonClick` 永远不触发。
  框架标准 code：`add` / `update` / `del` / `disable` / `enable` / 导入 **`daoru/show`** / 导出 **`daochu/show`**（见 `packages/@effects/src/utils/DefaultButtonResource.ts`）。
- **⚠️ 调后端接口的按钮必须加 loading（强制）**：`toolbarButtonClick`（含其 `Modal.confirm` 的 `onBeforeOk`）里凡 `await` 后端接口（删除/启用/禁用/重置/保存等），请求期间必须把当前按钮切到 loading——防重复提交 + 用户可感知。`params.button` 就是渲染中的按钮配置对象（useList 的 gridOptions 为 reactive，运行期可变；vxe 工具栏按钮原生支持 `loading`：转圈图标 + 自动禁用）。用 `try/finally` 保证成败都复位：

  ```typescript
  case 'userManagement/disable':
    // ...勾选校验后，Modal.confirm 的 onBeforeOk 里：
    params.button.loading = true
    try {
      const res = await requestClient.post('/core/authUser/updateSign', { id, cSign: '1' })
      if (res.code === 200) {
        Message.success(res.message)
        params.$grid.commitProxy('query', {})
        return true
      }
      Message.error(res.message)
      return false
    } finally {
      params.button.loading = false   // 成败都复位
    }
  ```

  补充：静态按钮配置同理直接支持 `{ code, name, loading, disabled }`（ButtonConfig 继承 VxeButtonProps）；Vue 3 响应式对新增属性同样追踪，**无需**预先声明 `loading: false`。纯打开弹窗类按钮（新增/修改/详情，无接口调用）不需要 loading。**导出按钮也算调接口**（打开弹窗会拉方案列表/详情）：`await openExport({...})` + `finally` 复位——弹窗本身「先开后载」（0.9.38 起 `openExport` 返回 Promise，数据加载完成才 resolve；旧版本 fire-and-forget，勿用 setTimeout 硬撑，升级即可）。

```typescript
// 原型 / 无后端：本地写死按钮，不依赖 resourceConfig 接口
const toolbarConfig = {
  buttons: [{ code: 'add', name: '新增' }],
};

const { QueryForm, Grid } = useList<DemoVO>({
  searchFormSchema,
  tableColumns,
  resourceConfig,      // 可传，nResourceid: 0 跳过资源接口
  queryFunction,
  toolbarConfig,       // ← 本地按钮塞这里
  gridEvents: {
    toolbarButtonClick(params: any) {
      if (params.button.code === 'add') {
        addVisible.value = true;   // 打开新增弹窗
      }
    },
  },
});
```

> 业务上线时把本地 `toolbarConfig` 删掉，按钮改回后端注入即可，事件分发代码不用动。

## 1. 何时使用

- 需要展示数据列表（带分页、多条件查询）
- 需要批量操作（启用/禁用/删除）、导出
- 需要保存/管理常用查询（查询方案）

不适用：

- 纯录入 → 用 [form-modal](../modules/form-modal.md)
- 明细编辑 → 用可编辑表格弹窗
- 主从联动 → 用 `useSunnyQueryGrid` 自行组合

## 2. 文件结构（四件套）

```
src/api/{module}/index.ts          # API 函数
src/views/{module}/{Name}Query.vue # 页面组件
src/views/{module}/config.ts       # searchFormSchema + tableColumns + resourceConfig
src/views/{module}/types.ts        # QueryParams + VO
```

> 命名：组件 PascalCase（`{Name}Query.vue`），类型 `{Module}QueryParams` / `{Module}VO`，实体字段 `{module}Entity`（camelCase）。

## 3. 标准实现

### 3.1 API 层 — `src/api/{module}/index.ts`

```typescript
import { requestClient } from '@sunny-base-web/effects';
import type { ResponseResult } from '@sunny-base-web/effects';
import type { DemoQueryParams, DemoVO } from '#/views/{module}/types';

/** 分页查询 */
export function selectForPage(params: DemoQueryParams) {
  return requestClient.post<ResponseResult<{ records: DemoVO[]; total: number }>>(
    '/{module}/selectForPage',
    params,
  );
}

/** 批量删除（按需） */
export function batchDelete(ids: number[]) {
  return requestClient.post<ResponseResult<void>>('/{module}/batchDelete', { ids });
}
```

### 3.2 类型 — `src/views/{module}/types.ts`

```typescript
/** 查询参数 */
export interface DemoQueryParams {
  /** 页码 */
  pageNo: number;
  /** 每页大小 */
  pageSize: number;
  /** 排序字段 */
  sortField?: string;
  /** 排序方向 */
  sortOrder?: '' | 'asc' | 'desc';
  /** 查询实体 */
  demoEntity: {
    cName?: string;
    nStatus?: number | null;
    dCredate?: string[];
  };
}

/** 数据 VO */
export interface DemoVO {
  /** ID */
  id: number;
  /** 名称 */
  cName: string;
  /** 状态 */
  nStatus: number | null;
  /** 创建日期 */
  dCredate: string | null;
}
```

### 3.3 配置 — `src/views/{module}/config.ts`

```typescript
import type { VxeGridProps } from '@sunny-base-web/ui';
import type { FormSchema } from '@sunny-base-web/ui';

/** 查询表单（无需配 colProps，useList 已全局响应式布局） */
export const searchFormSchema: FormSchema[] = [
  { fieldName: 'cName', label: '名称', component: 'Input', componentProps: { placeholder: '请输入名称', allowClear: true } },
  // 字典下拉：字段以 n 开头 + number → 配 dictCode
  { fieldName: 'nStatus', label: '状态', component: 'Select', selectOptions: { dictCode: 'STATUS' }, componentProps: { placeholder: '请选择状态', allowClear: true } },
  // 日期范围
  { fieldName: 'dCredate', label: '创建日期', component: 'RangePicker', componentProps: { allowClear: true } },
];

/** 表格列（sortable 启用服务端排序；filters 启用列筛选） */
export const tableColumns: VxeGridProps['columns'] = [
  { type: 'checkbox', width: 50, fixed: 'left' },
  { type: 'seq', title: '序号', width: 60 },
  { field: 'cName', title: '名称', minWidth: 120, sortable: true, filters: [{ data: '' }], filterRender: { name: 'MyFilterComplex' } },
  { field: 'nStatus', title: '状态', width: 100, sortable: true },
  { field: 'dCredate', title: '创建日期', width: 150, sortable: true },
];

/** 资源配置（工具栏按钮 / 查询方案 依赖它，由后端资源系统加载） */
export const resourceConfig = {
  resourceId: 'demoQuery',
  nResourceid: 0,
  cModnumb: '',
};
```

### 3.4 页面组件 — `src/views/{module}/{Name}Query.vue`

```vue
<script lang="tsx" setup>
import { useList, useSchemaOptionsLoader } from '@sunny-base-web/effects';
import { Message, Modal } from '@arco-design/web-vue';
import { selectForPage, batchDelete } from '#/api/{module}';
import { searchFormSchema, tableColumns, resourceConfig } from './config';
import type { DemoVO, DemoQueryParams } from './types';

defineOptions({ name: 'DemoQuery' });

// 字典自动加载（selectOptions.dictCode 的选项由它注入）
const { enhancedSchema } = useSchemaOptionsLoader(searchFormSchema);

// 查询函数：合并「查询表单 + 表格列筛选 + 排序」
interface QueryFunctionParams {
  page: { currentPage: number; pageSize: number };
  formValues: Record<string, any>;
  filterValues?: Record<string, any[]>;
  sorts?: Array<{ field: string; order: 'asc' | 'desc' }>;
}

const queryFunction = async ({ page, formValues, filterValues, sorts }: QueryFunctionParams) => {
  // 合并筛选：表格列筛选优先级高于查询表单
  const mergedFilters = {
    ...(formValues.cName && { cName: [formValues.cName] }),
    ...(formValues.nStatus != null && { nStatus: [formValues.nStatus] }),
    ...(formValues.dCredate?.length && { dCredate: formValues.dCredate }),
    ...filterValues, // 表格列筛选覆盖
  };

  const queryParams: DemoQueryParams = {
    pageNo: page.currentPage,
    pageSize: page.pageSize,
    sortField: sorts?.[0]?.field || '',
    sortOrder: sorts?.[0]?.order || '',
    demoEntity: {
      cName: mergedFilters.cName?.join(',') || '',
      nStatus: mergedFilters.nStatus?.[0] ?? null,
      dCredate: mergedFilters.dCredate || [],
    },
  };
  return await selectForPage(queryParams);
};

// 工具栏按钮事件（按钮本身由后端资源系统按 resourceConfig 注入）
const gridEvents = {
  toolbarButtonClick(params: any) {
    const selected = [
      ...params.$grid.getCheckboxReserveRecords(),
      ...params.$grid.getCheckboxRecords(),
    ];
    if (params.button.code === 'delete') {
      if (selected.length === 0) return Message.warning('请至少选择一条记录');
      Modal.confirm({
        title: '提示',
        content: `确定删除选中的 ${selected.length} 条记录吗？`,
        onBeforeOk: async () => {
          await batchDelete(selected.map((r: any) => r.id));
          params.$grid.commitProxy('query'); // 刷新
          return true;
        },
      });
    }
  },
};

const { QueryForm, Grid, handleGlobalEnter } = useList<DemoVO>({
  searchFormSchema: enhancedSchema.value,
  tableColumns: tableColumns || [],
  resourceConfig,
  queryFunction,
  gridEvents,
});
</script>

<template>
<div
    class="h-full flex flex-col bg-[var(--color-fill-2)] focus:outline-none"
    tabindex="-1"
    @keydown.enter="handleGlobalEnter"
  >
    <!-- Main Container -->
    <div
      class="flex-1 bg-[var(--color-bg-2)] flex flex-col shadow-sm border border-[var(--color-border)] overflow-hidden rounded"
    >
      <!-- Search Form Area -->
      <div class="px-4 border-b py-2 pb-3 border-[var(--color-border)]">
        <QueryForm />
      </div>

      <!-- Data Grid Area -->
      <div ref="gridAreaRef" class="flex-1 px-2 pt-1 overflow-hidden flex flex-col">
        <Grid class="flex-1" :row-class-name="rowClassName" :checkbox-config="checkboxConfig" />
      </div>
    </div>
  </div>
</template>
```

## 4. 关键约定（踩坑高频点）

- **四件套配置集中在 `config.ts`，禁止内联在 `.vue` 里**：`searchFormSchema` / `tableColumns` / `resourceConfig` 全部在模块 `config.ts` 导出（见 §2 文件结构），页面 `.vue` 只 import + 写查询函数与事件分发。Schema 内联进 `.vue` 是生成错误。
- **工具栏按钮一律走 `toolbarConfig.buttons`**：详见开头「⚠️ 工具栏按钮规则」。有后端 → 资源注入；无后端 → 本地塞 `[{code, name}]`。**无论哪种都不许自写 `<div>` + 按钮拼工具栏。**
- **异步按钮必须 loading**：`toolbarButtonClick`（或其 `Modal.confirm` `onBeforeOk`）里 `await` 后端接口期间，`params.button.loading = true`、`finally` 复位——写法见开头「⚠️ 工具栏按钮规则」第三条。
- **`queryFunction` 必须合并三路值**：`formValues`（搜索栏）+ `filterValues`（表格列筛选，优先级更高）+ `sorts`（排序）。表格筛选会覆盖查询表单同名条件。
- **别手动 `join` / 取对象 value**：用 useList 的 `arrayToStringFields`（数组→逗号串）和 `objectToValueFields`（对象数组→value，配 SunnyBusinessSearch 必用），转换在 queryFunction 调用前自动完成。
- **查询表单不要配 `colProps`**：useList 已全局配响应式布局（<992px 单列、lg 四列、xl 六列），手动配会破坏布局。
- **服务端排序**：列加 `sortable: true` → useList 自动捕获列头点击，通过 `sorts` 传给 queryFunction，取 `sorts[0]` 即可（通常单列排序）。
- **跨页选中**取选中行要合并 `getCheckboxReserveRecords()` + `getCheckboxRecords()`；刷新表格用 `params.$grid.commitProxy('query')`。
- **字典下拉**：字段以 `n` 开头 + number 类型通常是字典字段，配 `selectOptions.dictCode`；`useSchemaOptionsLoader` 自动加载选项。
- **错误处理**：`requestClient` 已内置全局错误拦截，业务 `catch` 里别再 `Message.error()`。

## 5. 变体

| 变体 | 做法 |
|------|------|
| 原型 / 无后端 | `toolbarConfig.buttons` 本地塞 `[{code:'add',name:'新增'}]`，queryFunction 用前端 mock；详见开头规则 |
| 无查询方案 | 不传 `resourceConfig` / 关闭 searchPlanConfig（useList 默认行为） |
| 无批量操作 | 去掉 checkbox 列 + 不写 batch* API + 精简 gridEvents |
| 简单查询（无字典） | 去掉 `useSchemaOptionsLoader`，直接用 `searchFormSchema` |
| 带导出 | 配 `useExport`，工具栏按 `daochu/show` 触发（见 [export.md](../modules/export.md)） |
| 业务搜索字段 | 用 `SunnyBusinessSearch` + `objectToValueFields`（见 [SunnyBusinessSearch.md](../components/SunnyBusinessSearch.md)） |

## 6. 关联资源

- **核心 Hook**：`useList` / `useSchemaOptionsLoader`（`@sunny-base-web/effects`）
- **相关文档**：[export.md](../modules/export.md)（导出）、[SunnyBusinessSearch.md](../components/SunnyBusinessSearch.md)、[SunnyForm.md](../components/SunnyForm.md)
- **弹窗集成**：[form-modal](../modules/form-modal.md) / [table-modal](../modules/table-modal.md) / [form-table-modal](../modules/form-table-modal.md)（工具栏按钮打开）
