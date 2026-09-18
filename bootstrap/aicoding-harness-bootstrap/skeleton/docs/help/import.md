# Excel 导入

> 读者：PM（design 定模板列与回调 Service）· Developer（实现前）· Reviewer（审查对照）
> 本篇受 [index.md](index.md)「通用约定」与「受保护/慎用清单」约束。

## 概述

`sunny-base-export`（导入能力）：通用导入方法，把前端上传的 Excel 解析为 `List<Map<String, Object>>`，回调业务 Service 方法处理。需求含「批量导入 / Excel 数据入库」时用本篇。

## 依赖

```xml
<dependency>
    <groupId>com.sunny</groupId>
    <artifactId>sunny-base-export</artifactId>
</dependency>
```

版本由 base-platform 父 POM 统一管理，禁止子模块私改。

## 配置

### 前端按钮配置（资源管理）

- **vuex 方法**：固定填 `daoru/show`
- **导入/导出配置**格式：`模板名@模板显示名称,回调Service名,回调方法名`
- 示例：`i18nDataTemplate@数据国际化导入模板,assI18nDataServiceImpl.importExcel`

| 部分 | 说明 |
|------|------|
| `i18nDataTemplate` | 模板文件名（存放于 `resources/excelTemplate/`，**必须英文名**） |
| `数据国际化导入模板` | 模板显示名称 |
| `assI18nDataServiceImpl` | 回调 Service 实例名（首字母小写） |
| `importExcel` | 回调方法名 |

### 前端组件

```html
<!-- 基本用法 -->
<importDialog />

<!-- 带参数传递 -->
<importDialog :param-map="{'a': 1}" />
```

## 使用方式

### 无参导入（回调方法即 Service 方法，天然在 Service 层）

```java
public Result<?> importExcel(List<Map<String, Object>> dataMap, LogCommonDTO logCommonDTO) {
    List<AssI18nDataEntity> list = new ArrayList<>();
    for (Map<String, Object> map : dataMap) {
        AssI18nDataEntity entity = new AssI18nDataEntity();
        entity.setcBname(getStr(map.get("业务表名")));
        entity.setcFname(getStr(map.get("业务字段名")));
        list.add(entity);
    }
    if (!list.isEmpty()) {
        saveI18nDataCommon(list);
        this.saveOperatorLogSimple(logCommonDTO);  // 操作日志
    }
    return Result.ok("导入成功！");
}
```

### 带参导入

前端传 `param-map` 时，回调方法增加 `Dict` 入参（`cn.hutool.core.lang.Dict`，本质是 Map）：

```java
public Result<?> importExcel(Dict dict, List<Map<String, Object>> dataMap, LogCommonDTO logCommonDTO) {
    // dict 为前端传入的参数
}
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `dataMap` | 解析 Excel 行列生成的数据 |
| `logCommonDTO` | 记录导入日志，固定参数 |
| `dict` | 前端传入的自定义参数（可选） |

## 注意事项

- 模板文件必须放 `resources/excelTemplate/`，文件名必须英文（容器下中文路径可能找不到文件）
- 导入是批量写入：注意事务边界与批量上限（超量导入分批提交，见 standards/database.md 批量操作红线）
- 回调方法内的数据校验失败要有明确报错行号提示，便于用户修 Excel 重传
