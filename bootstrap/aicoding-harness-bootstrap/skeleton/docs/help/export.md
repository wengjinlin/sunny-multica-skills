# Excel 导出

> 读者：PM（design 定导出方案与列清单）· Developer（实现前）· Reviewer（审查对照）
> 本篇受 [index.md](index.md)「通用约定」与「受保护/慎用清单」约束。

## 概述

`sunny-base-export`（导出能力）：三种导出方案。

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **流式导出** | 节省内存，支持大数据量 | 无法对结果集做个性化处理 | 单 SQL 能查出的结果（最常用） |
| **一次性批量导出** | 可对结果集做个性化处理 | 全量加载占用内存 | 流式导出无法满足时 |
| **自定义格式导出** | 导出格式可个性化定制 | 全量加载占用内存 | 单 SQL 无法满足或格式有特殊需求 |

## 依赖

```xml
<dependency>
    <groupId>com.sunny</groupId>
    <artifactId>sunny-base-export</artifactId>
</dependency>
```

版本由 base-platform 父 POM 统一管理，禁止子模块私改。

## 配置

### 全局配置

```yaml
export-config:
  max-export-number: 50000    # 最大导出行数
  sheet-row-number: 800000    # 单个 sheet 行限制（超过自动分页签）
```

### 前端按钮配置（资源管理）

| 配置项 | 说明 |
|--------|------|
| 导出文件名 | 默认生成的导出文件名 |
| 导出处理类前缀 | 后端处理类前缀（如 `Test` → `TestExportHandler`，首字母小写） |
| 导出类型 | 流式 / 一次性批量 / 自定义格式 |

### 前端组件

```html
<!-- 本服务导出 -->
<exportDialog />

<!-- 基础模块导出（需指定微服务名） -->
<exportDialog export-url="main-data-sync" />
```

## 使用方式

### 通用规则

- 处理类放 `com.sunny.modules.export.handler` 包下（主服务与独立导出服务共用）
- 类名格式：`前缀 + ExportHandler`（如 `TestExportHandler`）
- 实现 `IExportHandler` 接口，加 `@Service` 注解

### 流式导出（重写 `exportQuery`）

```java
@Override
public void exportQuery(ExportResultHandler<?> handler, RowBounds rowBounds, Map<String, Object> map) {
    testMapper.exportQuery(handler, rowBounds, map);
}
```

对应 Mapper（方法必须无返回值，handler 参数必须保留）：

```java
void exportQuery(ExportResultHandler<?> handler, RowBounds rowBounds, @Param("param") Map<String, Object> map);
```

```xml
<!-- MySQL 需用 CaseInsensitiveMap 忽略大小写 -->
<select id="exportQuery" resultType="cn.hutool.core.map.CaseInsensitiveMap">
    <include refid="selectForPages"/>
</select>
```

### 一次性批量导出（重写 `exportAllQuery`）

```java
@Override
public List<Map<String, Object>> exportAllQuery(Map<String, Object> map) {
    List<Map<String, Object>> mapList = testMapper.exportAllQuery(map);
    // 对 mapList 做个性化处理
    return mapList;
}
```

### 自定义格式导出（重写 `customTableHead` + `exportCustom`）

```java
// 定义导出列
@Override
public List<Export> customTableHead() {
    List<Export> list = new ArrayList<>();
    // 参数：属性编号, 属性名称, 是否导出, 属性类型, 字段宽度
    list.add(new Export("cName", "名称", 1, ExportColDataType.VARCHAR, 15));
    // 数据字典列
    list.add(new Export("nDict", "数字类数据字典", 1, ExportColDataType.NUMBER, 20,
                        FieldSelType.DICT.getName(), "SFQY", null));
    // 下拉选项列
    List<SelOption> optList = CollUtil.newArrayList(
        new SelOption("启用", "10001"),
        new SelOption("禁用", "10002")
    );
    list.add(new Export("cName2", "下拉值", 1, ExportColDataType.VARCHAR, 20,
                        FieldSelType.SELOPTION.getName(), "sjzdSignOpts", optList));
    list.add(new Export("dCredate", "创建日期", 1, ExportColDataType.DATE, 20));
    return list;
}
```

### 仅修改部分列（实现 `customTableHeadPart`）

```java
@Override
public List<Export> customTableHeadPart(List<Export> exportList) {
    for (Export export : exportList) {
        if ("cUsernumb".equals(export.getColProp())) {
            export.setColDataType(ExportColDataType.VARCHAR.getName());
        }
    }
    return exportList;
}
```

### 数据国际化处理

- **流式导出**：数据字典类型的字段默认已自动转换
- **一次性批量 / 自定义格式**：需手动调用 `ExportUtilService.findChildDictData`

```java
// 传入字典大类编号集合，返回翻译后的 Map
Map<String, Map<String, String>> mapDict = ExportUtilService.findChildDictData(CollUtil.newHashSet("SFQY"));
```

## 注意事项

- 用户填写的单页签最大行数与导出行数不能超过全局配置（`export-config`）
- 大数据量导出注意内存占用，优先选流式
- 处理类路径固定 `com.sunny.modules.export.handler`，勿放业务模块包内（主服务与导出服务共用依赖此路径）
