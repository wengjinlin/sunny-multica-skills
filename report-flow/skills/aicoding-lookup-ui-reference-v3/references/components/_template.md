<!--
  per-component 文档模板（AntD 风格）
  --------------------------------------------------
  用法：
  - 新建组件文档时复制本文件，改名为 <ComponentName>.md
  - 替换所有 {{...}} 占位符
  - 必填节：1. 何时使用 / 2. 导入 / 3. 代码演示 / 4.1 Props
  - 其余节（4.2~4.5、5、6、7）按需，无内容就整节删除，不要留空标题
  - API（Props/Events/Methods/Slots/Hooks）以 docs/src/public/llms-full.txt 为权威来源，标注版本日期
  - 代码示例优先取自本仓库真实用法（packages/@effects/src/views/ 等），精简成最小可运行片段
  - 不写「样式变量 / Design Token」一节（项目主要用 Tailwind）
-->

# {{ComponentName}} {{中文名}}

> {{一句话定位}}。来源库：`@sunny-base-web/ui` ｜ 分类：{{Data Entry / Feedback / Composite / ...}} ｜ API 提取自 `docs/src/public/llms-full.txt`（{{版本日期}}）

## 1. 何时使用

- {{适用场景 1}}
- {{适用场景 2}}
- 不适用：{{何时改用别的组件，交叉引用如「简单展示用 Tag」}}

## 2. 导入

```typescript
import { {{ComponentName}}, {{相关 Hook / Type}} } from '@sunny-base-web/ui';
```

## 3. 代码演示

> 每个示例 = 三级标题 + 一句描述 + 代码块；挑 2–4 个覆盖核心用法，代码自包含、可复制。

### 3.1 基础用法

{{一句描述：最常用的最小形态}}

```vue
<script setup lang="ts">
// {{关键响应式数据 / hook 调用}}
</script>

<template>
  <!-- {{最小模板}} -->
</template>
```

### 3.2 {{关键变体，如「字段联动 / 校验 / 多选 / 异步加载」}}

{{一句描述}}

```vue
<!-- {{代码}} -->
```

## 4. API

### 4.1 Props

| Prop | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `{{prop}}` | `{{type}}` | `{{default}}` | {{Yes / No}} | {{说明}} |

### 4.2 Events
<!-- 无则整节删除 -->

| Event | Parameters | Description |
|-------|------------|-------------|
| `{{event}}` | `{{params}}` | {{说明}} |

### 4.3 Methods / Expose
<!-- 无则整节删除；指通过 ref 调用的方法，如 FormApi.validate -->

| Method | Signature | Description |
|--------|-----------|-------------|
| `{{method}}` | `{{signature}}` | {{说明}} |

### 4.4 Slots
<!-- 无则整节删除 -->

| Slot | Description |
|------|-------------|
| `{{slot}}` | {{说明}} |

### 4.5 Hooks
<!-- 无则整节删除；指组件自带的 useXxx -->

#### `{{useXxx}}`

{{一句话说明}}

```typescript
{{useXxx}}({{options}}): {{return}}
```

## 5. 类型定义
<!-- 无则整节删除；放复杂共享类型，如 FormSchema / FormApi / XxxOptions -->

```typescript
// {{类型定义}}
```

## 6. 注意事项 / FAQ

- {{项目约定，如「不直接依赖 requestClient」「catch 不重复 Message.error」「字典字段配 dictCode」}}
- {{踩坑 / 高频问题}}

## 7. 关联资源

- **相关组件**：{{同库联动件，交叉链接 references/XxxYyy.md}}
- **标准模块**：{{如被 modules / page-patterns 某模板使用，链接该模板；无则删除本行}}
- **真实代码**：{{本仓库内实际使用处，如 packages/@effects/src/views/...；无则删除本行}}
