# OpsPilot - 产品智能运维工具

基于Python和LLM的智能运维助手，提供Linux命令生成、系统监控、JVM分析、Web接口分析等功能。

## 功能特性

1. **Linux命令生成**
   - 自然语言转Linux命令
   - 静态规则检查（危险命令识别）
   - 动态行为分析
   - 风险命令二次确认机制

2. **操作系统指标分析**
   - CPU使用率分析
   - 内存使用情况
   - 磁盘I/O监控
   - 网络流量统计

3. **JVM情况分析**
   - GC情况统计
   - JVM内存使用分析
   - 垃圾回收器识别
   - 老年代大对象检测

4. **Web接口性能分析**
   - 自动扫描Spring Controller
   - 响应时间分析
   - 请求量统计
   - QPS参数分析

5. **SpringBoot异常日志分析**
   - Error日志解析
   - 异常堆栈分析
   - 问题根因定位
   - 解决方案推荐
   - **链路ID追踪分析**（根据traceId/requestId分析完整链路）
   - **目录扫描模式**（自动扫描目录下所有日志文件，跨文件追踪链路）

## 安装

```bash
pip install -r requirements.txt
```

## 配置

首次运行时会引导您配置LLM模型：
- **本地模式**: 使用Ollama运行本地模型（需要先安装Ollama）
- **远程模式**: 使用OpenAI兼容的API（需要API Key）

配置信息保存在 `config.yaml` 文件中。

## 使用

```bash
python main.py
```

运行后，通过交互式菜单选择需要的功能。

## 依赖

- Python 3.8+
- psutil: 系统监控
- rich: 终端美化
- prompt-toolkit: 交互式命令行
- openai: LLM调用（支持OpenAI兼容API）
- javalang: Java代码解析

## 注意事项

- Linux命令执行需要相应的系统权限
- JVM分析需要Java进程运行
- 本地Ollama模式需要预先安装并启动Ollama服务

# OpsPilot 使用指南

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置LLM模型

首次运行会自动引导配置，您也可以手动创建 `config.yaml` 文件：

#### 选项A：使用Ollama本地模型

```yaml
llm:
  mode: "ollama"
  ollama:
    base_url: "http://localhost:11434"
    model: "llama2"
```

**前置条件：**
- 安装Ollama: https://ollama.ai/
- 拉取模型: `ollama pull llama2`
- 启动服务: `ollama serve`

#### 选项B：使用远程API

```yaml
llm:
  mode: "api"
  api:
    base_url: "https://api.openai.com/v1"
    api_key: "your-api-key"
    model: "gpt-3.5-turbo"
```

支持任何OpenAI兼容的API，包括：
- OpenAI官方API
- Azure OpenAI
- 国内大模型API（如通义千问、文心一言等）

### 3. 运行程序

```bash
python main.py
```

## 功能详解

### 1. Linux命令生成

**功能说明：**
- 输入自然语言描述，AI自动生成对应的Linux命令
- 自动进行风险检查（静态规则 + 动态分析）
- 高危命令会要求二次确认
- 支持直接执行命令并查看结果

**使用示例：**
```
请描述你想执行的操作：查找当前目录下所有大于100MB的文件
生成的命令：find . -type f -size +100M
```

**风险等级：**
- 🟢 低危：普通查询命令，自动放行
- 🟡 中危：涉及系统文件或需要权限的命令，提示注意
- 🔴 高危：删除、格式化等危险操作，强制二次确认

### 2. 操作系统指标分析

**功能说明：**
- 实时收集系统性能指标
- 显示CPU、内存、磁盘、网络等详细信息
- AI智能分析系统健康状况
- 给出优化建议

**分析维度：**
- CPU使用率（总体和各核心）
- 内存使用情况（包含Swap）
- 磁盘空间和I/O
- 网络流量和错误率
- 系统运行时间

### 3. JVM情况分析

**功能说明：**
- 自动检测运行中的Java进程
- 收集GC统计信息
- 分析内存使用情况
- 识别垃圾回收器类型
- 检测老年代大对象

**前置条件：**
- 系统中有运行的Java进程
- 已安装JDK（需要jps、jstat、jmap等工具）

**分析内容：**
- GC次数和耗时（Young GC / Full GC）
- 各内存区域使用率（Eden、Survivor、老年代、Metaspace）
- 当前使用的垃圾回收器
- 大对象列表（默认阈值10MB，可配置）

**配置大对象阈值：**
```yaml
jvm:
  large_object_threshold: 10  # 单位：MB
```

### 4. Web接口性能分析

**功能说明：**
- 扫描SpringBoot项目中的Controller
- 统计API接口数量和类型
- AI分析RESTful设计规范性
- 识别潜在性能瓶颈
- 提供优化建议

**支持的注解：**
- @RestController / @Controller
- @RequestMapping
- @GetMapping / @PostMapping
- @PutMapping / @DeleteMapping / @PatchMapping

**使用流程：**
1. 输入SpringBoot工程代码路径
2. 自动扫描所有Controller类
3. 提取接口信息（HTTP方法、路径、方法名）
4. 生成统计报告
5. AI分析并给出建议

### 5. SpringBoot异常日志分析

**功能说明：**
- 解析SpringBoot错误日志
- 统计异常类型和出现频率
- 提取堆栈跟踪信息
- AI分析根本原因
- 推荐解决方案
- **新增：链路ID追踪分析**

**分析模式：**

#### 模式1：全量日志分析
扫描整个日志文件，分析所有错误和异常。

**使用流程：**
1. 选择"全量日志分析"模式
2. 输入日志文件路径
3. 自动解析错误和异常
4. 显示统计信息和错误详情
5. AI深度分析并给出解决方案

#### 模式2：根据链路ID分析（推荐用于分布式系统）
根据链路ID（traceId/requestId）追踪完整请求链路，分析整个调用过程。

**适用场景：**
- 分布式系统问题追踪
- 微服务调用链路分析
- 特定请求的完整日志追踪
- 上下游服务关联分析

**使用流程：**
1. 选择"根据链路ID分析"模式
2. 输入链路ID（如：abc123-def456-ghi789）
3. 输入日志文件路径或目录路径
   - **单文件模式**：输入单个日志文件路径
   - **目录扫描模式**：输入目录路径，自动扫描所有日志文件（.log, .txt, .out）
4. 系统自动提取该链路的所有相关日志
5. 多文件时按时间戳自动排序，还原完整调用顺序
6. 显示链路统计（ERROR/WARN/INFO数量、涉及文件数）
7. 按时间顺序展示链路日志（标注来源文件）
8. AI分析完整链路调用流程和问题根因

**支持的链路ID格式：**
- `traceId=xxx` 或 `traceId: xxx`
- `trace_id=xxx` 或 `trace_id: xxx`
- `requestId=xxx` 或 `requestId: xxx`
- `[traceId]` 格式
- 直接匹配链路ID字符串

**目录扫描功能：**
- 自动扫描目录下所有 .log、.txt、.out 文件
- 支持递归扫描子目录
- 实时显示扫描进度
- 自动合并多个文件的日志
- 按时间戳排序，还原完整调用链路
- 标注每条日志的来源文件
- 统计涉及的文件数量

**AI分析内容：**
1. 请求的完整链路流程
2. 每个环节的执行情况
3. 异常发生的具体位置和原因
4. 上下游服务调用关系
5. 根本原因分析
6. 问题解决方案
7. 防止类似问题的建议

**支持的日志格式：**
- 标准SpringBoot日志格式
- 包含ERROR关键字的日志
- Java异常堆栈信息
- 分布式链路追踪日志

## 配置管理

### 修改配置

在主菜单中选择"LLM配置管理"，可以重新配置：
- LLM模式（Ollama/API）
- 模型地址和参数
- API Key

配置会立即生效，无需重启程序。

### 配置文件位置

配置保存在项目根目录的 `config.yaml` 文件中。

## 常见问题

### Q1: Ollama连接失败

**解决方案：**
1. 确认Ollama服务已启动：`ollama serve`
2. 检查服务地址是否正确（默认：http://localhost:11434）
3. 确认模型已下载：`ollama list`

### Q2: API调用失败

**解决方案：**
1. 检查API Key是否正确
2. 确认API地址是否正确
3. 检查网络连接
4. 确认账户余额是否充足

### Q3: JVM分析功能无法使用

**解决方案：**
1. 确认系统中有运行的Java进程
2. 检查JDK是否已安装
3. 确认jps、jstat、jmap等工具可用
4. 可能需要相应的权限（与Java进程同用户或root）

### Q4: 命令执行超时

**解决方案：**
- 默认超时时间为30秒
- 长时间运行的命令可能会超时
- 考虑手动执行或后台运行

### Q5: Web接口扫描不到Controller

**解决方案：**
1. 确认路径是否正确
2. 检查是否是标准的SpringBoot项目
3. 确认使用了@RestController或@Controller注解
4. 检查文件编码（应为UTF-8）

## 高级用法

### 自定义危险命令规则

编辑 `config.yaml`：

```yaml
command_check:
  dangerous_commands:
    - "rm -rf"
    - "mkfs"
    - "dd if="
    - "> /dev/"
    - "chmod -R 777"
    # 添加自定义规则
    - "your-dangerous-pattern"
```

### 批量分析日志

```python
# 可以扩展log_analyzer.py支持批量处理
for log_file in log_files:
    analyzer.analyze_file(log_file)
```

### 集成到CI/CD

```bash
# 可以将分析功能集成到持续集成流程
python -c "from system_analyzer import SystemAnalyzer; ..."
```

## 最佳实践

1. **定期运行系统指标分析**，及时发现性能问题
2. **在生产环境谨慎使用命令执行功能**，建议先在测试环境验证
3. **定期分析JVM情况**，优化内存配置和GC参数
4. **在开发阶段使用Web接口分析**，确保API设计规范
5. **建立日志分析定时任务**，快速发现和解决线上问题

## 技术支持

如遇到问题，请检查：
1. Python版本（推荐3.8+）
2. 依赖包是否正确安装
3. 配置文件是否正确
4. 相关工具是否可用（Java工具、系统命令等）

# 更新日志

## [v1.2.0] - 2025-10-07

### 重要改进
- 🚀 **目录扫描功能** - 链路ID分析支持扫描整个目录
  - 自动扫描目录下所有日志文件（.log, .txt, .out）
  - 支持递归扫描子目录
  - 实时显示扫描进度条
  - 自动合并多个文件的日志
  - 按时间戳智能排序，还原完整调用链路
  - 标注每条日志的来源文件
  - 统计涉及的文件数量

### 功能增强
- 📊 改进链路日志显示，增加来源文件标识
- ⚡ 优化多文件日志合并性能
- 🔄 支持多种时间戳格式的自动识别和排序
- 📈 增加扫描进度可视化

### 技术优化
- 使用 Rich Progress 组件显示扫描进度
- 智能时间戳解析和排序算法
- 优化内存使用，支持大量日志文件扫描

### 文件变更
- 修改：`log_analyzer.py` - 新增目录扫描和多文件合并功能
- 更新：`USAGE.md` - 增加目录扫描使用说明
- 更新：`TRACE_ANALYSIS_EXAMPLE.md` - 更新使用示例
- 更新：`CHANGELOG.md` - 记录版本更新

### 适用场景
- ✅ 分布式系统日志分散在多个文件
- ✅ 微服务架构每个服务独立日志文件
- ✅ 日志按日期/大小切割成多个文件
- ✅ 需要追踪跨多个服务的完整链路

---

## [v1.1.0] - 2025-10-07

### 新增功能
- ✨ **链路ID追踪分析功能**
  - 支持根据traceId/requestId分析完整请求链路
  - 自动识别多种链路ID格式（traceId、trace_id、requestId、request_id等）
  - 按日志级别统计（ERROR/WARN/INFO）
  - 时间顺序展示链路日志
  - AI智能分析完整调用链路和问题根因
  - 支持上下游服务调用关系分析

### 改进
- 📝 SpringBoot日志分析增加模式选择（全量分析 / 链路ID分析）
- 📚 更新文档，增加链路分析详细说明
- 📖 新增 TRACE_ANALYSIS_EXAMPLE.md 使用示例文档

### 文件变更
- 修改：`log_analyzer.py` - 新增链路分析相关方法
- 更新：`README.md` - 增加链路分析功能说明
- 更新：`USAGE.md` - 详细的链路分析使用指南
- 更新：`PROJECT_SUMMARY.md` - 更新功能列表
- 新增：`TRACE_ANALYSIS_EXAMPLE.md` - 链路分析示例文档
- 新增：`CHANGELOG.md` - 更新日志

### 技术细节
- 支持正则表达式匹配多种链路ID格式
- 保留错误日志的完整堆栈跟踪
- 限制显示数量避免信息过载（默认显示前20条）
- AI分析提供7个维度的深度分析

---

## [v1.0.0] - 2025-10-07

### 初始版本发布

#### 核心功能
1. **Linux命令生成**
   - 自然语言转Linux命令
   - 三级风险检查（低/中/高）
   - 危险命令二次确认
   - 命令执行和结果显示

2. **操作系统指标分析**
   - CPU、内存、磁盘、网络监控
   - 实时性能数据采集
   - AI智能分析和优化建议

3. **JVM情况分析**
   - 自动检测Java进程
   - GC统计和内存分析
   - 垃圾回收器识别
   - 大对象检测

4. **Web接口性能分析**
   - 自动扫描SpringBoot Controller
   - RESTful API分析
   - 性能瓶颈识别

5. **SpringBoot异常日志分析**
   - 错误日志解析
   - 异常类型统计
   - AI根因分析

#### 技术特性
- 支持Ollama本地模型
- 支持OpenAI兼容的远程API
- Rich终端美化界面
- 交互式配置向导
- 完整的错误处理
- 模块化架构设计

#### 文档
- README.md - 项目介绍
- USAGE.md - 详细使用指南
- PROJECT_SUMMARY.md - 技术架构文档
- config.yaml.example - 配置示例

#### 部署
- requirements.txt - Python依赖
- start.sh - 快速启动脚本
- .gitignore - Git忽略配置


## License

MIT
