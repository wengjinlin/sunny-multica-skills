# 接口中转 PO

> 读者：PM（design 写上下游影响与超时策略）· Developer（实现前）· Reviewer（审查对照）
> 本篇受 [index.md](index.md)「通用约定」与「受保护/慎用清单」约束——示例即按封装层规范写。

## 概述

`sunny-base-po`：A 系统调用 B 系统接口时，通过 PO（Process Orchestration）中转。支持 HTTP（RESTful）与 WebService（SOAP）两种方式。涉及任何跨系统接口集成的需求先用本篇。

## 依赖

```xml
<dependency>
    <groupId>com.sunny</groupId>
    <artifactId>sunny-base-po</artifactId>
</dependency>
```

版本由 base-platform 父 POM 统一管理，禁止子模块私改。

## 配置

```yaml
po:
  http:
    urlPrefix: 192.xxx.xx.xxx:xxxx   # PO HTTP 地址
  username: xxx
  passwd: xxx

# SOAP 调用还需额外配置：
po:
  soap:
    urlPrefix: xxx
    senderService: xxx
```

> PO 有测试/生产两套环境：`application-dev` / `application-test` 调测试环境，`application-pro` 调生产。

## 使用方式

### API 速查

| 方法 | 用途 |
|------|------|
| `PoUtil.sendHttpPostRequestFromJson(url, JSONObject)` | HTTP + JSON 参数 |
| `PoUtil.sendHttpPostRequestFromJsonStr(url, String)` | HTTP + JSON 字符串 |
| `PoUtil.sendHttpPostRequestFromMap(url, Map)` | HTTP + Map 参数 |
| `PoUtil.sendHttpPostRequestFromXmlStr(url, String)` | HTTP + XML（Content-Type 自动 application/xml） |
| `PoUtil.sendSoapRequest(接口名, 接口命名空间, 方法名, 方法命名空间, params)` | SOAP 调用 |

### 封装层（模块专属子目录，禁止 Controller 直调）

```java
// customerlib/po/PoClient.java —— 模块专属封装层（通用约定 1/3 条）
@Slf4j
@Service
public class PoClient {

    /** HTTP + JSON 调用：失败转业务异常（业务异常类以项目 common 封装为准） */
    public String postJson(String interfacePath, Object paramMap) {
        try {
            log.info("po_http_call path={}", interfacePath);
            String result = PoUtil.sendHttpPostRequestFromJsonStr(interfacePath, JSONUtil.toJsonStr(paramMap));
            log.info("po_http_ok path={}", interfacePath);
            return result;
        } catch (Exception e) {
            log.error("po_http_failed path={}", interfacePath, e);
            throw new BusinessException("PO 接口调用失败：" + interfacePath);
        }
    }

    /** SOAP 调用 */
    public String callSoap(String interfaceName, String interfaceNamespace,
                           String methodName, String methodNamespace, Map<String, Object> params) {
        try {
            log.info("po_soap_call iface={}", interfaceName);
            return PoUtil.sendSoapRequest(interfaceName, interfaceNamespace, methodName, methodNamespace, params);
        } catch (Exception e) {
            log.error("po_soap_failed iface={}", interfaceName, e);
            throw new BusinessException("PO SOAP 调用失败：" + interfaceName);
        }
    }
}
```

### 业务层使用（Service 内，Controller 只编排）

```java
// 业务 Service 只依赖 PoClient，不直接碰 PoUtil
@Service
public class StaffInfoService {

    @Autowired
    private PoClient poClient;

    public List<StaffInfo> getStaffFromHr(String workCode) {
        Dict mapAll = new Dict();
        mapAll.put("HEADER", Dict.of("PERNR", workCode, "DOCN1", ""));
        mapAll.put("MESSAGE_HEADER", Dict.of("INTERFACE_ID", "HCM_001", "SENDER", "SSO", "RECEIVER", "HR"));
        String result = poClient.postJson("/RESTAdapter/OA/getCommonStaffInfoFromHR", mapAll);
        // 解析 result 并返回
        return parseStaffList(result);
    }
}
```

```java
// Controller 只做参数校验与编排（此处无任何平台调用）
@PostMapping(value = "/getStaffFromHr")
public Result<List<StaffInfo>> getStaffFromHr(@RequestBody StaffQuery query) {
    return Result.ok(staffInfoService.getStaffFromHr(query.getWorkCode()));
}
```

## 注意事项

- PO 调用涉及跨系统交互，design.md 必须说明上下游影响与超时处理（通用约定 4 条）
- 发送 OA 审批流程优先用 `sunny-base-sendoa` 封装（见 [sendoa.md](sendoa.md)）
- 不同系统的 RESTAdapter URL 不同，需联系 PO 开发确认；URL/凭据走配置，禁止硬编码
