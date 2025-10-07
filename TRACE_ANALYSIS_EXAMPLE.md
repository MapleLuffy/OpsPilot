# 链路ID分析功能使用示例

## 功能概述

链路ID分析功能帮助您在分布式系统中追踪特定请求的完整调用链路，快速定位问题。

## 使用场景

### 场景1：微服务调用链路追踪
当用户报告某个请求出现问题时，通过链路ID可以看到请求在各个服务中的完整调用过程。

### 场景2：性能问题定位
追踪慢请求的完整链路，分析各环节耗时，找出性能瓶颈。

### 场景3：异常根因分析
当某个请求失败时，通过链路ID可以看到从入口到异常发生的完整过程。

## 操作步骤

### 1. 启动OpsPilot

```bash
python main.py
```

### 2. 选择日志分析功能

在主菜单中选择：`5. SpringBoot异常日志分析`

### 3. 选择链路分析模式

```
请选择分析模式:
1. 全量日志分析
2. 根据链路ID分析

请选择: 2
```

### 4. 输入链路ID

```
请输入链路ID（如traceId/requestId）: abc123-def456-ghi789
```

**链路ID从哪里获取？**
- 应用日志中的traceId/requestId
- 监控系统的链路追踪ID
- 用户反馈的请求ID
- API网关日志中的请求标识

### 5. 输入日志文件路径或目录路径

**选项A：单文件分析**
```
请输入日志文件路径或目录路径: /var/log/app/application.log
```

**选项B：目录扫描（推荐）**
```
请输入日志文件路径或目录路径: /var/log/app/
```

系统会自动：
- 扫描目录下所有 .log、.txt、.out 文件
- 在所有文件中查找链路ID
- 按时间顺序合并日志
- 标注每条日志的来源文件

### 6. 查看分析结果

系统会展示：
- 扫描进度（目录模式）
- 涉及的文件列表（目录模式）
- 链路日志统计（总数、ERROR/WARN/INFO数量、涉及文件数）
- 按时间顺序的完整链路日志（标注来源文件）
- AI智能分析报告

## 日志格式示例

OpsPilot支持多种链路ID格式：

### 格式1：键值对格式
```
2025-10-07 10:30:15 INFO [traceId=abc123] OrderService - 开始处理订单
2025-10-07 10:30:16 INFO [traceId=abc123] PaymentService - 调用支付接口
2025-10-07 10:30:17 ERROR [traceId=abc123] PaymentService - 支付失败
```

### 格式2：JSON格式
```json
{"time": "2025-10-07 10:30:15", "level": "INFO", "trace_id": "abc123", "msg": "开始处理订单"}
{"time": "2025-10-07 10:30:16", "level": "INFO", "trace_id": "abc123", "msg": "调用支付接口"}
{"time": "2025-10-07 10:30:17", "level": "ERROR", "trace_id": "abc123", "msg": "支付失败"}
```

### 格式3：Logback/Log4j标准格式
```
2025-10-07 10:30:15.123 [http-nio-8080-exec-1] INFO  c.e.OrderController [requestId: abc123] - 接收订单请求
2025-10-07 10:30:16.234 [http-nio-8080-exec-1] INFO  c.e.OrderService [requestId: abc123] - 创建订单
2025-10-07 10:30:17.345 [http-nio-8080-exec-1] ERROR c.e.PaymentService [requestId: abc123] - 支付异常
```

## AI分析报告示例

AI会从以下维度进行分析：

### 1. 请求的完整链路流程
```
OrderController -> OrderService -> PaymentService -> 第三方支付API
```

### 2. 每个环节的执行情况
```
✓ OrderController: 接收请求成功
✓ OrderService: 订单创建成功
✗ PaymentService: 支付调用失败（超时）
```

### 3. 异常发生的具体位置和原因
```
位置: PaymentService.pay() 方法
原因: 第三方支付API响应超时（30秒无响应）
异常类型: SocketTimeoutException
```

### 4. 上下游服务调用关系
```
OrderController (入口)
  └─ OrderService
      ├─ InventoryService (库存检查) ✓
      └─ PaymentService (支付处理) ✗
          └─ ThirdPartyPaymentAPI (第三方) ✗
```

### 5. 根本原因分析
```
1. 第三方支付API不稳定，频繁超时
2. 未设置合理的超时和重试机制
3. 缺少熔断降级策略
```

### 6. 问题解决方案
```
短期方案：
1. 联系第三方支付服务商排查问题
2. 临时增加超时时间到60秒

长期方案：
1. 实现重试机制（最多3次）
2. 增加熔断器（Hystrix/Resilience4j）
3. 实现降级策略（使用备用支付通道）
4. 增加异步补偿机制
```

### 7. 防止类似问题的建议
```
1. 为所有外部API调用设置合理的超时时间
2. 实现完整的熔断降级机制
3. 增加调用链路监控告警
4. 定期进行压力测试和演练
5. 建立多活容灾方案
```

## 实际案例

### 案例1：微服务架构 - 订单支付失败（目录扫描模式）

**场景描述：**
电商系统采用微服务架构，订单服务、支付服务、库存服务各自独立部署，日志分散在不同文件中。

**日志文件结构：**
```
/var/log/ecommerce/
├── order-service.log       # 订单服务日志
├── payment-service.log     # 支付服务日志
├── inventory-service.log   # 库存服务日志
├── gateway.log            # 网关日志
└── notification-service.log # 通知服务日志
```

**操作步骤：**
1. 从用户反馈获取订单号，查询对应的traceId: `trace-2025-abc123`
2. 使用OpsPilot链路分析功能
3. 选择模式：`2. 根据链路ID分析`
4. 输入链路ID: `trace-2025-abc123`
5. 输入目录路径: `/var/log/ecommerce/`
6. 系统自动扫描5个日志文件

**扫描结果：**
```
正在扫描目录: /var/log/ecommerce/...
找到 5 个日志文件
正在查找链路ID: trace-2025-abc123...

扫描文件: gateway.log ✓
扫描文件: order-service.log ✓
扫描文件: inventory-service.log ✓
扫描文件: payment-service.log ✓
扫描文件: notification-service.log ✓

✓ 在 4 个文件中找到相关日志
涉及文件: gateway.log, order-service.log, inventory-service.log, payment-service.log
```

**发现的完整链路：**
```
[10:30:15.123] gateway.log - INFO - 接收订单请求
[10:30:15.234] order-service.log - INFO - 创建订单
[10:30:15.456] inventory-service.log - INFO - 检查库存
[10:30:15.567] inventory-service.log - INFO - 扣减库存成功
[10:30:15.678] order-service.log - INFO - 调用支付服务
[10:30:16.789] payment-service.log - ERROR - 第三方支付API超时
[10:30:16.890] order-service.log - ERROR - 支付失败，订单状态异常
```

**AI分析结果：**
- 完整链路流程：Gateway → OrderService → InventoryService → PaymentService → 第三方API
- 问题定位：PaymentService调用第三方API时超时
- 连锁影响：库存已扣减但支付失败，订单状态不一致
- 根本原因：缺少分布式事务管理和补偿机制

**解决效果：**
- 10分钟内定位跨4个服务的完整链路
- 发现分布式事务一致性问题
- 实施Seata分布式事务解决方案

---

### 案例2：单文件分析 - 电商订单支付失败问题

**问题描述：**
用户下单后支付失败，投诉订单状态异常。

**操作步骤：**
1. 从用户反馈获取订单号，查询对应的traceId
2. 使用OpsPilot链路分析功能，输入traceId
3. 查看完整链路日志

**发现问题：**
- 订单创建成功
- 库存扣减成功
- 支付服务调用第三方API时超时
- 但订单状态未正确回滚

**AI分析建议：**
1. 增加分布式事务管理（Seata）
2. 实现补偿事务机制
3. 增加订单状态一致性检查
4. 优化支付超时后的重试逻辑

**解决效果：**
- 问题定位时间：从2小时缩短到5分钟
- 快速实施解决方案
- 建立了防止类似问题的机制

## 最佳实践

### 1. 统一链路ID规范

建议在整个系统中统一使用相同的链路ID字段名：
```java
// 推荐使用
MDC.put("traceId", generateTraceId());

// 在日志配置中添加
<pattern>%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level [traceId=%X{traceId}] %logger{36} - %msg%n</pattern>
```

### 2. 链路ID生成策略

```java
// 使用UUID
String traceId = UUID.randomUUID().toString();

// 使用时间戳+随机数
String traceId = System.currentTimeMillis() + "-" + RandomStringUtils.randomAlphanumeric(8);

// 使用雪花算法
String traceId = String.valueOf(snowflakeIdGenerator.nextId());
```

### 3. 链路ID传递

确保在跨服务调用时传递链路ID：
```java
// HTTP Header
headers.put("X-Trace-Id", traceId);

// Dubbo Attachment
RpcContext.getContext().setAttachment("traceId", traceId);

// Kafka Message Header
record.headers().add("traceId", traceId.getBytes());
```

### 4. 日志记录规范

在关键节点记录日志：
```java
log.info("[traceId={}] 开始处理订单, orderId={}", traceId, orderId);
log.info("[traceId={}] 调用支付服务, amount={}", traceId, amount);
log.error("[traceId={}] 支付失败, error={}", traceId, e.getMessage(), e);
```

## 常见问题

### Q1: 为什么找不到某个链路ID的日志？

**可能原因：**
1. 链路ID输入错误（注意大小写）
2. 日志文件不是该请求经过的服务
3. 日志已被轮转或清理
4. 链路ID格式不在支持列表中

**解决方法：**
1. 确认链路ID的准确性
2. 检查多个相关服务的日志文件
3. 查看备份日志或日志归档
4. 联系开发确认日志格式

### Q2: 日志量很大时分析很慢怎么办？

**优化建议：**
1. 使用日期时间范围缩小搜索范围
2. 先用grep等工具预过滤日志
3. 将大文件拆分为小文件
4. 考虑使用ELK等专业日志系统

### Q3: 链路不完整怎么办？

**可能原因：**
1. 某些服务未记录该链路ID
2. 异步调用中链路ID未传递
3. 日志级别过滤掉了部分日志

**改进方法：**
1. 检查各服务的链路ID传递逻辑
2. 为异步调用增加链路ID传递机制
3. 调整日志级别配置

## 技术支持

如遇到问题或有改进建议，欢迎反馈：
- 查看 USAGE.md 了解更多功能
- 查看 README.md 了解系统配置
- 提交 Issue 或 Pull Request
