<!--
  per-component 文档模板
  --------------------------------------------------
  用法：
  - 新建组件文档时复制本文件，改名为 <ComponentName>.md
  - 替换所有 {{...}} 占位符
  - 必填节：1. 何时使用 / 2. 导入 / 3. 代码演示 / 4.1 Props
  - 其余节（4.2~4.5、5、6、7）按需，无内容就整节删除，不要留空标题
  - API 权威来源（按序）：
      ① 所在工程源码（src/components/**，工程内全局组件以它为准）
      ② kunkka 组件库本地源码仓库 E:\kunkka组件库\kunkka 的 packages/components/llms-full.txt / llms.txt / llms-semantic.md（只读）
      ③ 所在工程 node_modules/sunnygroup-components（行为以它为准）
  - 代码示例优先取自官方模板与 demo（src/template/、src/views/demo/），精简成最小可运行片段
  - 框架 Vue 2.7 + Options API：示例不写 <script setup>；交互用 ref 实例方法 + .sync
-->

# {{ComponentName}} {{中文名}}

> {{一句话定位}}。来源库：{{sunnygroup-components（kunkka 组件库，main.js 全局注册） / 工程内全局组件（src/plugins/sunnyoptical.js 注册） / 工程内按需引入}} ｜ API 提取自 {{权威来源文件（标注日期）}}

## 1. 何时使用

- {{适用场景 1}}
- {{适用场景 2}}
- 不适用：{{何时改用别的组件，交叉引用如「轻量确认用 MessageBox.confirm」}}

## 2. 导入

```
{{全局注册的组件（kunkka-* / Sunnyoptical 系列）无需 import，模板直接写标签；}}
{{按需引入的写 import XxXx from '@/components/XxXx' 或 'sunnygroup-components/lib/kunkka-xx'}}
```

## 3. 代码演示

> 每个示例 = 三级标题 + 一句描述 + 代码块；挑 2–4 个覆盖核心用法，代码自包含、可复制。

### 3.1 基础用法

{{一句描述：最常用的最小形态}}

```vue
<script>
export default {
  // {{data / mixin / ref}}
}
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

<!-- 无则整节删除；指通过 this.$refs 调用的方法（框架无 hooks，这是主要交互方式） -->

| Method | Signature | Description |
|--------|-----------|-------------|
| `{{method}}` | `{{signature}}` | {{说明}} |

### 4.4 Slots

<!-- 无则整节删除 -->

| Slot | Description |
|------|-------------|
| `{{slot}}` | {{说明，含作用域参数}} |

## 5. 类型定义 / 数据结构

<!-- 无则整节删除；框架 JS 为主，放关键数据结构（如 optionlist 的 {cKeyname, cKeynumb, cSlot}） -->

## 6. 注意事项 / FAQ

- {{项目约定，如「request.js 已全局报错，catch 别重复提示」}}
- {{踩坑 / 高频问题}}

## 7. 关联资源

- **相关组件**：{{交叉链接 references/XxxYyy.md}}
- **标准模板**：{{被 page-patterns / modules 哪个模板使用，链接该模板；无则删除本行}}
- **真实代码**：{{本仓库内实际使用处；无则删除本行}}
