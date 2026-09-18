# 平台能力使用指南

> 本目录收录本项目使用的平台能力（自研/二方平台包 + 通用中间件）的使用指南。任何涉及平台集成的需求，需先查阅对应章节。
> 新增能力文档的格式规范见 [_template.md](_template.md)。

## 能力清单

| 能力 | 包 / 组件 | 简介 | 文档 |
|------|----------|------|------|
| 鉴权/权限资源 | sunny-auth-client | 登录态 + AUTH_EXRES 权限资源表体系（菜单/按钮/C_VIEWPATH） | （待建：auth.md） |
| 接口中转 PO | sunny-base-po | 跨系统接口调用中转（HTTP REST / SOAP，Process Orchestration） | [po.md](po.md) |
| 对象存储 S3 | sunny-base-s3 | 文件上传/下载（新项目统一 Vestack S3） | [s3.md](s3.md) |
| OA 对接 | sunny-base-sendoa | OA 审批流程单创建（sunny-base-po 上层封装） | [sendoa.md](sendoa.md) |
| 分布式锁 | sunny-base-lock | 业务幂等/并发控制（Redis） | [lock.md](lock.md) |
| 流程引擎 BPM | sunny-base-process（Flowable） | 流程定义/绑定（BPM_PROCESS_BINDING）/节点提交与网关退回 | （待建：process.md） |
| Excel 导入 | sunny-base-export | 模板导入 + 回调 Service 处理 | [import.md](import.md) |
| Excel 导出 | sunny-base-export | 流式 / 一次性批量 / 自定义格式三方案 | [export.md](export.md) |
| 消息队列 Kafka | sunny-base-kafka | Kafka 收发封装（配置驱动 + Handler 消费） | [kafka.md](kafka.md) |
| 日志 | sunny-base-log | 平台日志切面 | （内置于框架，暂无专文档） |
| i18n | sunny-client-i18n | 错误消息/文案国际化 | （待建：i18n.md） |
| 分页 | sunny-client-pagehelper | pageNo/pageSize 分页（DTO 内字段驱动） | （见 standards/api.md 分页节） |
| 动态 Redis | sunny-dynamic-redis | 缓存 | （待建：redis.md） |
| SAP 同步 | customerlib/sap/（模块内封装） | 客户主档 SAP 同步 | （待建：sap.md） |

<!-- 分析指引：本清单为 sunny 体系预置。实例化时按项目实际引入的二方包依赖**删减未用行**、补项目特有能力；「待建」文档在首次深度使用时按 _template.md 骨架补齐并回填本表；自研包 vs 社区组件的选型对照可增设「选型决策记录」节 -->

## 共享底座

- 父 POM：`com.sunny:base-platform`（版本与依赖统一管理，**禁止**子模块私改版本；各能力文档依赖示例一律不写 version）
- sunny-base-module（模块框架）+ sunny-common-util（通用工具）+ sunny-client-i18n + sunny-client-pagehelper
- 前端底座：@sunny-base-web/{ui,stores,utils,effects,locales,constants,shadcn-ui}（vben5 系）+ Arco Design Vue

<!-- 分析指引：按项目实际基础包核对增删；无 sunny 前端的项目删前端底座行 -->

## 通用约定

适用于**所有**平台能力调用（能力文档示例均按此写，正文不重复展开）：

1. **封装位置**：平台调用的封装**必须**放在模块专属子目录（如 `customerlib/sap/`、`customerlib/po/`）或 common 模块；新模块中调用**必须**通过封装层，**禁止**直接 new 客户端
2. **异常处理**：平台调用的异常**必须**在 Service 层捕获并转换为业务异常，**禁止**向上抛裸异常
3. **调用位置**：平台调用**禁止**写在 Controller / 展示层
4. **超时 / 重试 / 降级**：策略**必须**在 OpenSpec `design.md` 中显式说明（读超时 / 连接超时 / 重试次数 / 降级返回）
5. **配置**：连接信息走 Nacos/配置文件，**禁止**硬编码；敏感配置不入文档不入库
6. **日志**：调用入口 / 出口 / 失败**必须**有日志，含操作者 + method + 耗时
7. **幂等**：写操作的平台调用**必须**有业务幂等键，**禁止**靠重试兜底

## 受保护 / 慎用清单

| 区域 | 风险 | 注意 |
|------|------|------|
| application*.yml 平台配置段 | 凭据泄露/改错全服务不可用 | hook 拦截；变更走 design 声明 + 人审 |
| sunny-base-lock | 锁 TTL 与业务时长不匹配 | 必须设超时 + finally 释放；禁止锁内远程调用 |
| sunny-base-process 网关退回 | 退回连线错导致流程卡死 | 用 returnNode 网关版语义，禁止自造退回 |
| SAP 同步 | 外部系统不可用拖垮主流程 | 异步 + 降级；事务内禁止 SAP 调用 |
| sunny-base-kafka 消费 | Handler 未捕获异常时后续 ack 覆盖 offset，**丢数据** | batchExecute 内按业务决定异常边界；关键数据先落库再 ack |
| 动态 Redis | 缓存与库不一致 | 写库后失效策略显式设计 |

<!-- 分析指引：按项目实际中间件增删行；本表与「通用约定」视同宪法红线，违反会被 Reviewer 打回 -->
