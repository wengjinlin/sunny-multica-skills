# 分布式锁

> 读者：PM（design 识别并发场景与锁粒度）· Developer（实现前）· Reviewer（审查对照）
> 本篇受 [index.md](index.md)「通用约定」与「受保护/慎用清单」约束——示例即按封装层规范写。

## 概述

`sunny-base-lock`：基于 Redis 的分布式锁，防止多节点重复执行同一任务（定时任务、并发抢占、防重复提交等）。

## 依赖

```xml
<dependency>
    <groupId>com.sunny</groupId>
    <artifactId>sunny-base-lock</artifactId>
</dependency>
```

版本由 base-platform 父 POM 统一管理，禁止子模块私改。

## API 说明

| 方法 | 说明 |
|------|------|
| `AssLockUtils.newSimpleLock(name, expireSeconds)` | 创建锁：成功返回解锁密钥，失败返回 `null`（他人持有） |
| `AssLockUtils.removeSimpleLock(name, unlockContent)` | 解锁：传入创建时返回的密钥 |

## 使用方式

Service 方法内加锁执行（**必须 try-finally**）：

```java
@Slf4j
@Service
public class SyncJobService {

    /**
     * 定时任务加锁执行：多节点部署时同一时刻只有一个节点真正跑业务
     */
    public void syncOnLock() {
        String unlockKey = AssLockUtils.newSimpleLock("ecqCustomerSync", 300);
        if (unlockKey == null) {
            log.info("sync_lock_held skip");   // 其他节点正在执行
            return;
        }
        try {
            doSync();                           // 业务逻辑（锁 TTL 内必须能完成）
            log.info("sync_ok");
        } finally {
            AssLockUtils.removeSimpleLock("ecqCustomerSync", unlockKey);  // 异常也必须解锁
        }
    }
}
```

## 注意事项

- **必须 try-finally**：异常路径不解锁 = 死锁到 TTL 过期
- **TTL 与业务时长匹配**：估算业务最大耗时后留余量；TTL 过短业务未完锁已释放，等于没锁（见 index.md 慎用清单）
- **锁内禁止远程调用**：锁应只罩住短临界区，远程调用（PO/SAP/OA）放锁外
- 锁名带业务含义（如 `ecqCustomerSync`），避免不同业务同名互踩
- 加锁失败是正常分支（他人持有），走跳过/稍后重试，不要当异常抛
