# Kafka 消息

> 读者：PM（design 定主题/消费组命名与可靠性等级）· Developer（实现前）· Reviewer（审查对照）
> 本篇受 [index.md](index.md)「通用约定」与「受保护/慎用清单」约束——示例即按封装层规范写。

## 概述

`sunny-base-kafka`：对 Kafka 配置与使用的简化封装，改配置项即可收发消息。需求含「发消息 / 消费消息 / 异步通知 / 解耦上下游」时用本篇。

## 依赖

```xml
<dependency>
    <groupId>com.sunny</groupId>
    <artifactId>sunny-base-kafka</artifactId>
</dependency>
```

版本由 base-platform 父 POM 统一管理，禁止子模块私改。

## 配置

```yaml
kafka-config:
  enable: true                    # 是否启用 Kafka（开关）
  default-brokers: host1:9192,host2:9193,host3:9194  # broker 节点
  request-timeout-ms-config: 30000
  producer:
    default-topics: slmTest1      # 发送消息的默认主题
    acks: 0
    retries: 3
    batch-size: 100
    buffer-memory: 33554432
    liner-ms: 100
    key-serializer: org.apache.kafka.common.serialization.StringSerializer
    value-serializer: org.apache.kafka.common.serialization.StringSerializer
  consumer:
    default-listen: true           # 是否启动默认监听
    default-group-id: dev-base-consumer    # 消费组名称
    default-topics: slmTest,slmTest1       # 监听主题（逗号分隔）
    data-execute-handler: TestKafkaDataExecuteHandler  # 数据处理器类名
    batch-concurrency: 3           # 并发消费者数量（≤ topic 分区数，多实例时需加倍）
    auto-offset-reset: latest
    poll-timeout: 1500
    max-poll-records: 500
    enable-auto-commit: false      # 建议显式 ack
    session-timeout-ms-config: 30000
    key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
    value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
```

### 关键配置说明

| 配置项 | 说明 |
|--------|------|
| `enable` | 不使用 Kafka 时设 `false`，加快启动 |
| `producer.default-topics` | 发送消息的默认主题，按需更改 |
| `consumer.default-group-id` | 消费组名称，按环境区分（dev/test/pro） |
| `consumer.default-topics` | 监听主题，多个逗号分隔 |
| `consumer.data-execute-handler` | 数据处理器类名（实现 `IKafkaDataExecuteHandler`） |
| `consumer.batch-concurrency` | 总线程数 = 实例数 × 此值，须 ≤ topic 分区数（默认 12） |

## 使用方式

### 发送（Service 内，失败转业务异常）

```java
@Slf4j
@Service
public class NoticeSyncService {

    /**
     * 业务完成后发送通知消息。
     * 失败是否阻断主流程按业务定：阻断则抛业务异常；不阻断则记 error 日志由消费侧对账。
     */
    public void sendNotice(Notice notice) {
        try {
            KafkaUtilService.sendMessage(JSONUtil.toJsonStr(notice));
            log.info("kafka_send_ok noticeId={}", notice.getId());
        } catch (Exception e) {
            log.error("kafka_send_failed noticeId={}", notice.getId(), e);
            throw new BusinessException("通知消息发送失败");
        }
    }
}
```

### 消费（Handler，@Service）

在 `com.sunny.kafka` 包下创建处理器，实现 `IKafkaDataExecuteHandler`：

```java
@Slf4j
@Service
public class TestKafkaDataExecuteHandler implements IKafkaDataExecuteHandler {

    @Autowired
    private TestMapper testMapper;

    @Override
    public void batchExecute(List<ConsumerRecord<String, String>> consumerRecordList) {
        List<Test> testList = new ArrayList<>();
        for (ConsumerRecord<String, String> record : consumerRecordList) {
            log.info("kafka_consume topic={} partition={} key={}", record.topic(), record.partition(), record.key());
            Test test = new Test();
            test.setcName(record.value());
            testList.add(test);
        }
        testMapper.insertBatch(testList);
    }
}
```

## 注意事项

- **offset 覆盖丢数据**（见 index.md 慎用清单）：`batchExecute` 内不 try-catch 时，第一条失败未 ack、第二条成功 ack 会覆盖 offset，第一条**业务数据丢失**——按业务决定方法内异常边界（逐条 try-catch 或整批失败停消费）
- 开发期不调试 Kafka：`kafka-config.enable: false` 加快启动
- dev / test / pro 三环境设置不同主题与消费组名，减少干扰
- 指定分区等高级发送需求需联系框架组
