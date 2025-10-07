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

## License

MIT
