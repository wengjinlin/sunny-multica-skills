# 表单弹窗标准模板（form-modal）

> 新增 / 编辑业务数据的弹窗，本质是 **`SunnyModal` + `SunnyForm`（`useForm`）的组合**。本模板自包含，照着改字段即可生成。

## 1. 何时使用

- 新增 / 编辑业务数据（弹窗内表单录入）
- 字段联动（显隐 / 必填 / 禁用 / 联动赋值）
- 含字典 / 权限下拉、业务搜索字段的表单

不适用：

- 表格明细编辑 → 用表格弹窗（`SunnyModal` + `useTable`）
- 整页表单录入 → 用页面模式
- 简单确认提示 → 用 `Modal.confirm()`

## 2. 文件结构

通常**追加到已有的 query-list 模块**（弹窗由工具栏按钮打开）：

```
src/api/{module}/index.ts           # 追加 add / getById / update
src/views/{module}/{Name}Add.vue    # 弹窗组件（新增文件）
src/views/{module}/config.ts        # 追加 addFormSchema
src/views/{module}/types.ts         # 复用 VO，一般无需新增
```

## 3. 标准实现

### 3.1 API 追加 — `src/api/{module}/index.ts`

```typescript
/** 新增 */
export function add(data: Record<string, any>) {
  return requestClient.post<ResponseResult<void>>('/{module}/add', { demoEntity: data });
}

/** 按 ID 查详情（编辑回填用） */
export function getById(id: number) {
  return requestClient.post<ResponseResult<DemoVO>>('/{module}/getById', { id });
}

/** 更新 */
export function update(data: Record<string, any>) {
  return requestClient.post<ResponseResult<void>>('/{module}/update', { demoEntity: data });
}
```

### 3.2 配置追加 — `src/views/{module}/config.ts`

```typescript
import { markRaw } from 'vue';
import type { FormSchema } from '@sunny-base-web/ui';
import { SunnyBusinessSearch } from '@sunny-base-web/ui';

const BusinessSearch = markRaw(SunnyBusinessSearch); // 组件用 markRaw

export const addFormSchema: FormSchema[] = [
  // 文本输入（必填）
  { fieldName: 'cName', label: '名称', component: 'Input', rules: 'required', componentProps: { placeholder: '请输入名称', allowClear: true } },

  // 字典下拉：dictCode 对应后端字典（非必填字段默认挂「只看必填项」开关）
  { fieldName: 'nZt', label: '状态', component: 'Select', selectOptions: { dictCode: 'SFQY' },
    dependencies: { show: (v: any) => !v.__onlyRequired },
    componentProps: { placeholder: '请选择状态', allowClear: true } },

  // 权限下拉：code 对应后端权限（公司/部门等）
  { fieldName: 'cOrg', label: '组织机构', component: 'Select', permissionOptions: { code: 'COMPANY' },
    dependencies: { show: (v: any) => !v.__onlyRequired } },

  // 业务搜索（返回对象数组 → useForm 必须配 objectToValueFields）
  {
    fieldName: 'roleValue', label: '角色', component: BusinessSearch,
    componentProps: (_, formApi) => ({
      cNum: 'XTGL_USER_ROLE',
      modalProps: { multiple: false, fieldNames: { label: 'C_ROLENAME', value: 'ID' } },
      onChange: (values: any[]) => formApi.setFieldValue('cRemark', values[0]?.C_ROLENUMB ?? ''), // 联动赋值
    }),
  },

  // 联动：状态 = 启用时才显示（字典值是字符串，严禁与数字比较）；
  // 已有联动条件的非必填字段：只看必填项开关与原条件 AND 组合
  { fieldName: 'cRemark', label: '备注', component: 'Input',
    dependencies: { show: (v: any) => !v.__onlyRequired && v.nZt === '10001' } },

  // 附件上传：action/downAction 全局已配，这里只给过滤条件；面板较宽用大 span。
  // 两段式：选完必须点「上传附件」才真正上传（详见 components/SunnyUpload.md）
  { fieldName: 'cAttachment', label: '附件', component: 'SunnyUpload',
    dependencies: { show: (v: any) => !v.__onlyRequired },
    componentProps: { accept: '.pdf,.doc,.docx,.xls,.xlsx', limit: 5, maxSize: 10 },
    colProps: { span: 16 } },
];
```

### 3.3 弹窗组件 — `src/views/{module}/{Name}Add.vue`

```vue
<script setup lang="ts">
import { nextTick, watch } from 'vue';
import { Message } from '@arco-design/web-vue';
import { useForm } from '@sunny-base-web/effects';
import { Modal, toStorageString, fromStorageString } from '@sunny-base-web/ui';
import { addFormSchema } from './config';
import { add, update } from '#/api/{module}';

defineOptions({ name: 'DemoAdd' });

const props = defineProps<{ visible: boolean; editData?: { id: number } }>();
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void;
  (e: 'success'): void;
}>();

// 返回三元组：[FormComponent, formApi, onlyRequired] —— 第 3 个是「只看必填项」开关 ref，
// 直接 v-model 到弹窗底部 checkbox（见模板 #insertFooter）
const [FormComponent, formApi, onlyRequired] = useForm({
  schema: addFormSchema,
  objectToValueFields: ['roleValue'], // 业务搜索对象数组必须配，否则回显异常
});

// 打开时重置；编辑模式回填
watch(
  () => props.visible,
  async (visible) => {
    if (!visible) return;
    formApi.resetForm();
    onlyRequired.value = false; // 复位「只看必填项」开关
    if (props.editData) {
      await nextTick();
      // 附件字段（SunnyUpload）：后端 "name:url,..." → 组件 JSON 字符串；schema 无附件字段可去掉这行
      const data = props.editData as Record<string, any>;
      formApi.setValues({ ...data, cAttachment: fromStorageString(data.cAttachment) });
    }
  },
  { immediate: true },
);

// 提交（@ok 模式：提交后弹窗自动关闭）
async function handleOk() {
  const { valid } = await formApi.validate();
  if (!valid) return;
  const values = await formApi.getValues();
  // 附件字段：组件 JSON → 后端 "name:url,..."（未点「上传附件」的文件此时会被丢弃，必要时先校验提示）
  values.cAttachment = toStorageString(values.cAttachment);
  await (props.editData ? update(values) : add(values));
  Message.success('操作成功');
  emit('success');
}
</script>

<template>
  <Modal
    :model-value="visible"
    title="新增"
    :width="600"
    @ok="handleOk"
    @update:model-value="emit('update:visible', $event)"
  >
    <FormComponent />

    <!-- 底部最左：「只看必填项」开关（默认必备）；flex-1 把取消/确认推回右侧 -->
    <template #insertFooter>
      <a-checkbox v-model="onlyRequired" class="mr-3">只看必填项</a-checkbox>
      <div class="flex-1" />
    </template>
  </Modal>
</template>
```

### 3.4 在 query-list 页面集成

```vue
<!-- XxxQuery.vue 模板里 -->
<DemoAdd v-model:visible="addVisible" :edit-data="editData" @success="refresh" />
```

```typescript
// gridEvents.toolbarButtonClick 里
const addVisible = ref(false);
const editData = ref<any>(null);
// case 'add':  editData.value = null;  addVisible.value = true;
// case 'edit': if (selected.length !== 1) return; editData.value = selected[0]; addVisible.value = true;
```

## 4. 关键约定

- **Schema 一律写 `config.ts`，禁止内联在 `.vue` 里**：`addFormSchema` 导出自模块 `config.ts`（见 §2、§3.2），弹窗 `.vue` 只 `import { addFormSchema } from './config'`。内联进 `.vue` 是生成错误。
- **「只看必填项」默认必备**（用户体验标准项，§3.3 模板已含）：`useForm` 第 3 个返回值 `onlyRequired` 直接 v-model 到 footer `#insertFooter` 的 checkbox。机制：开关写 `__onlyRequired` 保留上下文字段 → config.ts 非必填字段的 `dependencies.show` 响应隐藏（已有联动条件的字段 AND 组合两个条件）。**仅过滤视图，隐藏字段值仍参与提交**；打开弹窗时复位。真实参照：`packages/@effects/src/views/setting/user/UserAdd.vue`。
- **弹窗受控用 `:model-value` + `@update:model-value`**：`SunnyModal` 没有 `visible` prop，传 `:visible` 会出现「能打开、关不掉」（详见 [SunnyModal.md](../components/SunnyModal.md) FAQ）。
- **字典值是字符串**：字典下拉字段的联动比较必须 `=== '10001'`，不能 `=== 1`（后端字典 value 恒为字符串）。
- **字段联动用 `dependencies`**：`show` / `if` / `required` / `disabled` / `componentProps`，声明式，别手写 `watch`。
- **业务搜索字段必须配 `objectToValueFields`**：返回对象数组，不配会被序列化成字符串、回显异常。
- **附件字段（`SunnyUpload`）**：`modelValue` 是 JSON 字符串，与后端 `"name:url,..."` 格式的互转**只发生在边界**——回填前 `fromStorageString`、提交前 `toStorageString`；组件是两段式（选完必须点「上传附件」），未上传的文件不进表单值，提交时被静默丢弃。详见 [SunnyUpload.md](../components/SunnyUpload.md)。
- **联动赋值用 `componentProps` 函数形式**：`(_, formApi) => ({ onChange: ... })`，在 `onChange` 里 `formApi.setFieldValue`。
- **两种提交模式**：`@ok`（提交即自动关闭）vs `:on-before-ok`（返回 `false` 阻止关闭，适合校验失败保留弹窗）。
- **编辑回填**：`watch(visible)` → `resetForm()` → `setValues(editData)`；`resetForm` 会清空所有数据，编辑前必须重置再回填。
- **`setValues` 写上下文字段**：`setValues(data, false)` 可写入 schema 外字段供 `dependencies` 读取（用 `__` 前缀避免冲突）。
- **错误不重复提示**：`requestClient` 已内置全局错误拦截，业务 `catch` 里别再 `Message.error()`。

## 5. 变体

| 变体 | 做法 |
|------|------|
| 仅新增 | 去掉 `editData` prop + `getById`/`update` 逻辑 |
| 仅编辑 | 去掉 `add`，`editData` 改必传 |
| 新增 + 编辑共用 | 用 `editData` 是否存在区分（本文标准实现即此模式） |
| 校验失败不关闭 | `@ok` → `:on-before-ok`，校验失败 `return false` |

## 6. 关联资源

- **组成组件**：[SunnyModal.md](../components/SunnyModal.md)、[SunnyForm.md](../components/SunnyForm.md)（`useForm`）、[SunnyUpload.md](../components/SunnyUpload.md)（附件字段）
- **页面集成**：[查询列表页标准模板](../page-patterns/query-list.md)（工具栏按钮打开弹窗）
- **真实代码**：`packages/@effects/src/views/setting/role/RoleAdd.vue`（RoleAdd 式：子组件自持 visible + defineExpose）
