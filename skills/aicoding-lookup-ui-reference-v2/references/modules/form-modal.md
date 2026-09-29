# 表单弹窗标准模板（form-modal）

> 新增 / 编辑 / 查看详情的业务数据弹窗，本质是 **`KunkkaModal` + `kunkka-form`** 的组合，字段与按钮由弹窗模块自己的资源（`modnumb`）下发。本模板自包含，照着改 `name` / `modnumb` / api 即可生成。

> 模板源文件：[src/template/formDialogTemplate.vue](../../../../../src/template/formDialogTemplate.vue) ｜ demo：[src/views/demo/querylist/demoAdd.vue](../../../../../src/views/demo/querylist/demoAdd.vue)（本文即模板精编，自包含）

## 1. 何时使用

- 新增（`<name>Add.vue`）/ 编辑（`<name>Update.vue`）/ 详情（`<name>Detail.vue`）三兄弟弹窗
- 字段联动（动态显隐 / 动态必填 / 动态禁用，由资源 `cDynamicShow` / `cDynamicRules` / `cDynamicDisabled` 表达式驱动）
- 含放大镜字段（InputSearch）、自定义下拉（CustomizeSelect）的表单

不适用：

- 弹窗内还有明细表格一次提交 → [table-modal](./table-modal.md)
- 轻量确认 → `MessageBox.confirm()`，不要为此开全量弹窗
- 整页表单 → 框架惯例仍是弹窗（宽 `width="960px"`）

## 2. 文件结构

通常**追加到已有的 query-list 模块目录**（弹窗由工具栏按钮打开）：

```
src/api/<模块>/<name>.js              # 追加 insert / update_init / update
src/store/modules/<模块>/<name>.js    # 追加 addSave / updateSave（保存后 dispatch queryList）
src/views/.../<name>Add.vue           # 新增弹窗（新增文件）
src/views/.../<name>Update.vue        # 编辑弹窗（新增文件）
src/views/.../<name>Detail.vue        # 详情弹窗（新增文件，只读回显）
```

> 后端「资源管理」需为弹窗配独立模块（拿到 `modnumb`），字段 `cArea='form'`、按钮 `cArea='form'`（`cSubArea` 决定落位：`insertFooter` / `centerFooter` / `appendFooter` / `footer`）。

## 3. 标准实现

### 3.1 弹窗组件 — `<name>Add.vue`

照 [formDialogTemplate.vue](../../../../../src/template/formDialogTemplate.vue)：

```vue
<template>
  <kunkka-modal
    ref="registerModal"
    :visible.sync="visible"
    :title="title"
    width="960px"
    :close-on-click-modal="false"
    :show-close="false"
    @ok="handleOk"
    @cancel="handleCancel"
  >
    <kunkka-form
      ref="kunkka-form"
      label-position="left"
      label-width="auto"
      :show-message="false"
      v-bind="formData"
      :events="events"
      @inputSearchClick="inputSearchClick"
    />
    <!-- 弹窗底栏扩展位（按钮由资源 cSubArea 决定，见 §3.4） -->
    <kunkka-search-dialog
      ref="kunkka-search-dialog"
      @submitAction="submitAction"
      @cleanAction="cleanAction"
    />
  </kunkka-modal>
</template>
<script>
import { mapGetters } from 'vuex'
import formModal from '@/mixins/formModal'
import { insert } from '@/api/manHourManagement/programItem'

export default {
  mixins: [formModal],   // 提供 currentUserResourcesGroupBycArea 等方法
  data() {
    return {
      visible: false,
      title: this.$t('新增'),
      formData: {
        gutter: 20,
        showMessage: false,
        size: 'mini',
        form: [],       // 资源下发后填充
        button: [],
        model: {}       // 表单值（kunkka-form 双向同步）
      },
      events: {}        // 字段事件 { cSsgs: { change: fn } }
    }
  },
  computed: {
    ...mapGetters(['programItem'])
  },
  methods: {
    // 父页面打开入口：this.$refs.programItemAdd.onDataReceive({ row })
    onDataReceive(data) {
      this.currentUserResourcesGroupBycArea({ modnumb: '<弹窗资源modnumb>' }).then((result) => {
        const { resFieldList, resButtonList } = result
        this.formData.form = resFieldList['form']
        this.formData.button = resButtonList['form']
        this.formData.model = {}
        this.visible = true
        // 编辑/详情：调查询接口回显（Update/Detail 弹窗）
        // update_init({ programItem: { id: row.id } }).then((res) => {
        //   this.formData.model = res.result
        // })
        this.$nextTick(() => {
          this.$refs['kunkka-form'].$refs['kunkkaForm'].clearValidate()
        })
      })
    },

    // 放大镜字段点击：打开公共查询弹窗
    inputSearchClick(data) {
      this.$refs['kunkka-search-dialog'].openInit({
        cNum: 'XXX_XXXX',
        selection: false,
        defaultModel: {}
      })
    },

    // 查询弹窗选中回填（单选 data=行对象，字段 C_XXX 大写；多选=数组）
    submitAction(data, fData) {
      // this.formData.model.cCode = data.C_CODE
      // this.formData.model.cName = data.C_NAME
    },
    cleanAction(data, fData) {},

    // 确定：校验 → loading → 保存 → 关窗
    handleOk() {
      this.$refs['kunkka-form'].$refs['kunkkaForm'].validate((valid) => {
        if (!valid) {
          this.$message.error('必填项未填写完整')
          return false
        }
        this.$refs.registerModal.changeOkLoading(true)
        insert({ programItem: { ...this.formData.model } }).then(() => {
          this.$store.dispatch('programItem/queryList')   // 刷新列表
          this.visible = false
        }).finally(() => {
          this.$refs.registerModal.changeOkLoading(false)  // 成败都复位
        })
      })
    },

    handleCancel() {
      this.visible = false
    }
  }
}
</script>
```

### 3.2 store 追加 — addSave / updateSave

```javascript
// store/modules/<模块>/<name>.js actions 追加（或直接在页面调 api，两种写法都常见；
// 走 action 的好处是保存成功后统一 dispatch('queryList')）
addSave({ dispatch }, data) {
  return insert(data).then(res => {
    dispatch('queryList')
    return res
  })
}
```

### 3.3 编辑 / 详情变体

- **Update 弹窗**：`onDataReceive({ row })` 里 `update_init({ programItem: { id: row.id } })` 回显 `formData.model`，提交走 `update`。
- **Detail 弹窗**：同样回显，但隐藏确定按钮（`KunkkaModal` 传 `:show-ok-btn="false"`），表单禁用（资源字段配只读 / 或 `kunkka-form` 透传 `disabled`）。

### 3.4 弹窗底栏扩展按钮位

`KunkkaModal` 的四个插槽对应资源按钮 `cSubArea`（模板源文件里有完整注释示例）：

| 插槽 | 位置 | 资源 cSubArea |
|------|------|---------------|
| `#insertFooter` | 取消按钮**前面** | `insertFooter` |
| `#centerFooter` | 取消与确定**中间** | `centerFooter` |
| `#appendFooter` | 确定按钮**后面** | `appendFooter` |
| `#footer` | 整个底部**全重写**（覆盖取消/确定） | `footer` |

```vue
<template #centerFooter>
  <el-button
    v-for="btn in formData.button.filter((it) => it.cSubArea === 'centerFooter')"
    :key="btn.nButtonid"
    :loading="btn.loading"
    plain
    @click="toolbarClick(btn)"
  >
    {{ btn.label }}
  </el-button>
</template>
```

## 4. 关键约定（踩坑高频点）

- **打开弹窗走 `onDataReceive`，不走 props**：父组件 `this.$refs.xxxAdd.onDataReceive({ row })`；子组件自持 `visible`，保存成功后自己置 `false`。不要给弹窗传 `visible` prop 再 `v-model`。
- **`:visible.sync` 必须带 .sync**：`KunkkaModal` 靠 `update:visible` 关窗，漏 `.sync` 就是「能打开关不掉」。
- **校验是双层 ref**：`this.$refs['kunkka-form'].$refs['kunkkaForm'].validate(cb)`（kunkka-form 内部包着 el-form）；打开弹窗后 `clearValidate()` 清上一次的校验残留。
- **确定按钮必做 loading**：`this.$refs.registerModal.changeOkLoading(true)` + `.finally()` 复位，防连点重复提交。
- **必填规则来自资源 `cRequired`**，动态显隐 / 必填 / 禁用来自资源表达式（`cDynamicShow` / `cDynamicRules` / `cDynamicDisabled`，[utils.js](../../../../../src/mixins/configurationFile/utils.js) 求值），**不要在 `.vue` 里手写字段数组**。
- **字段事件写 `events`**：`events = { cSsgs: { change: (val) => {...} } }`；级联改下游字段 `attrParam`（见 [KunkkaCustomizeSelect.md](../components/KunkkaCustomizeSelect.md)）。
- **放大镜字段选中回填注意大小写**：`submitAction` 返回行是后端 SQL 别名（`C_CODE` 大写下划线），回填 `formData.model` 时手动映射到 camelCase 字段。
- **多选回填用 MulSearchDialog**：代码 / 名称逗号拼接的场景（用法见 [MulSearchDialog.md](../components/MulSearchDialog.md) §3.1）。
- **错误不重复提示**：`request.js` 已全局拦截报错，业务 `catch` 里别再 `$message.error()`；成功提示用 `Message.success(res.message)`。

## 5. 变体

| 变体 | 做法 |
|------|------|
| 仅新增 | 只写 `<name>Add.vue`（本文标准实现） |
| 新增 + 编辑分文件 | 项目惯例是 Add / Update 分开两个文件（各引各的 api），不共用 |
| 详情只读 | `<name>Detail.vue`：回显 + `:show-ok-btn="false"` + 禁用 |
| 底部加自定义按钮 | 资源按钮配 `cSubArea` + 对应插槽（§3.4） |

## 6. 关联资源

- **组成组件**：[KunkkaModal.md](../components/KunkkaModal.md)、[KunkkaForm.md](../components/KunkkaForm.md)、[KunkkaSearchDialog.md](../components/KunkkaSearchDialog.md) / [MulSearchDialog.md](../components/MulSearchDialog.md)、[KunkkaCustomizeSelect.md](../components/KunkkaCustomizeSelect.md)
- **页面集成**：[query-list](../page-patterns/query-list.md)（工具栏按钮 `onDataReceive` 打开）
- **真实代码**：[src/template/formDialogTemplate.vue](../../../../../src/template/formDialogTemplate.vue)（官方模板）、[demoAdd.vue](../../../../../src/views/demo/querylist/demoAdd.vue)（官方 demo）
