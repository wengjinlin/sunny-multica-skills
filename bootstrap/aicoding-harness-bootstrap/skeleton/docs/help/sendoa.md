# 发送 OA 审批流程

> 读者：PM（design 写上下游影响与流程单字段映射）· Developer（实现前）· Reviewer（审查对照）
> 本篇受 [index.md](index.md)「通用约定」与「受保护/慎用清单」约束——示例即按封装层规范写。

## 概述

`sunny-base-sendoa`：通过 PO 调用创建 OA 审批流程单，是对 `sunny-base-po` 的上层封装，简化 SOAP 参数构造。需求含「发 OA / 走审批流程单」时用本篇。

## 依赖

```xml
<!-- 发送 OA 流程包（底层依赖 sunny-base-po，需同时引入） -->
<dependency>
    <groupId>com.sunny</groupId>
    <artifactId>sunny-base-sendoa</artifactId>
</dependency>
```

版本由 base-platform 父 POM 统一管理，禁止子模块私改。

## 配置

使用前需在**系统管理**中完成 OA 调用配置：

- **菜单路径**：系统管理 → 功能组件管理 → 发送 OA 配置
- **模块编号**：根据 OA 流程路径命名（如 `问题闭环-公共功能-重工单`）
- **公司**：可选，相同模块编号可按公司配不同流程单
- **URL 地址**：调用 OA 的 URL
- **OA 流程 ID**：OA 中要创建的流程单 ID

## 使用方式

完整闭环示例（取人 → 构造 → 发送 → 流程单 ID 落库，全部在 Service 内完成）：

```java
// customerlib/oa/OaFlowService.java —— 模块专属封装层（通用约定 1/3 条）
@Slf4j
@Service
public class OaFlowService {

    @Autowired
    private OrderMapper orderMapper;

    /**
     * 为业务单据创建 OA 审批流程单，成功后把 workFlowId 回写业务表
     * （远程调用不进事务——发送成功与落库之间靠 workFlowId 对账补偿）
     */
    public void sendOaFlow(Order order, String creatorWorkCode) {
        // 1. 获取 OA 人员信息（部门编号不传则取主职部门；可传多人）
        OaPersonResult personResult = CustomWorkFlowManageUtil.getOaPersonId(
            CollUtil.newArrayList(new OaPerson(creatorWorkCode, null)),
            "/RESTAdapter/QMSBasic/getPersonListFromOA");

        // 2. 构造主项参数
        Map<String, String> mainMap = new HashMap<>();
        mainMap.put("gs", personResult.getData().get(0).getCompanyId());    // 公司 ID
        mainMap.put("bm", personResult.getData().get(0).getDeptId());       // 部门 ID
        mainMap.put("ngr", personResult.getData().get(0).getUserId());      // 拟稿人 ID
        mainMap.put("ngrgh", personResult.getData().get(0).getWorkCode());  // 拟稿人工号
        mainMap.put("ngrq", DateUtil.today());                              // 拟稿日期

        // 3. 发送流程单（子项参数 key 为数字：0=第 1 个表格，无子项传 null）
        Result res = CustomWorkFlowManageUtil.sendOA(
            "流程标题",
            new AssSendoaMsg("模块编号", null),   // 模块编号 + 公司编号（查 ASS_SENDOA 配置）
            mainMap,
            null,
            personResult.getData().get(0).getUserId()  // OA 拟稿人 ID
        );

        // 4. 结果处理：失败转业务异常，成功落 workFlowId
        if (res.getCode() != 200) {
            log.error("sendOA_failed orderId={}", order.getId());
            throw new BusinessException("OA 流程发送失败：" + res.getMessage());
        }
        Integer workFlowId = Integer.valueOf(res.getMessage());
        orderMapper.updateWorkFlowId(order.getId(), workFlowId);  // 记录到业务表，供后续流程追踪
        log.info("sendOA_ok orderId={} workFlowId={}", order.getId(), workFlowId);
    }
}
```

## 注意事项

- OA 调用涉及跨系统交互，design.md 必须说明上下游影响与超时处理（通用约定 4 条）
- `workFlowId` 必须记录到业务表，用于后续流程追踪/撤单
- 子项参数 `LinkedHashMap<Integer, List<Map>>` 的 key 为数字格式（0=第 1 个表格，1=第 2 个表格...），无子项传 `null`
- 不同系统的取人 URL 不同，联系 PO 开发确认；URL 走配置
- 发送 OA 属写操作，重试必须带幂等键（通用约定 7 条）——重复发送会产生重复流程单
