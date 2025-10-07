"""
SpringBoot日志分析模块
"""
import os
import re
from typing import List, Dict, Any
from datetime import datetime
from collections import Counter
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm


class LogAnalyzer:
    """SpringBoot日志分析器"""
    
    def __init__(self, llm_client):
        """
        初始化日志分析器
        
        Args:
            llm_client: LLM客户端实例
        """
        self.llm = llm_client
        self.console = Console()
    
    def run(self) -> None:
        """运行日志分析功能"""
        self.console.print("\n[bold cyan]SpringBoot异常日志分析[/bold cyan]\n")
        
        # 选择分析模式
        self.console.print("[yellow]请选择分析模式:[/yellow]")
        self.console.print("1. 全量日志分析")
        self.console.print("2. 根据链路ID分析")
        
        mode = Prompt.ask("请选择", choices=["1", "2"], default="1")
        
        if mode == "2":
            self.run_trace_analysis()
            return
        
        # 选择日志文件
        log_file = Prompt.ask("\n请输入日志文件路径")
        
        if not os.path.exists(log_file):
            self.console.print("[red]日志文件不存在[/red]")
            input("\n按回车键返回主菜单...")
            return
        
        # 读取并解析日志
        self.console.print("\n[yellow]正在解析日志文件...[/yellow]\n")
        log_data = self._parse_log_file(log_file)
        
        if not log_data['errors']:
            self.console.print("[green]未发现错误日志[/green]")
            input("\n按回车键返回主菜单...")
            return
        
        # 显示统计信息
        self._display_statistics(log_data)
        
        # 显示错误详情
        self._display_errors(log_data['errors'])
        
        # AI分析
        if Confirm.ask("\n是否需要AI智能分析？", default=True):
            self.console.print("\n[yellow]正在进行AI分析...[/yellow]\n")
            
            # 选择要分析的错误
            if len(log_data['errors']) > 5:
                self.console.print("[yellow]错误数量较多，将分析最严重的5个错误[/yellow]\n")
                errors_to_analyze = log_data['errors'][:5]
            else:
                errors_to_analyze = log_data['errors']
            
            # 格式化日志内容
            log_content = self._format_errors_for_analysis(errors_to_analyze)
            analysis = self.llm.analyze_error_log(log_content)
            
            if analysis:
                self.console.print(Panel(
                    analysis,
                    title="[bold green]AI分析报告[/bold green]",
                    border_style="green"
                ))
            else:
                self.console.print("[red]AI分析失败[/red]")
        
        input("\n按回车键返回主菜单...")
    
    def run_trace_analysis(self) -> None:
        """运行链路ID日志分析功能"""
        self.console.print("\n[bold cyan]链路ID日志分析[/bold cyan]\n")
        
        # 输入链路ID
        trace_id = Prompt.ask("请输入链路ID（如traceId/requestId）")
        
        if not trace_id.strip():
            self.console.print("[red]链路ID不能为空[/red]")
            input("\n按回车键返回主菜单...")
            return
        
        # 选择日志路径（文件或目录）
        log_path = Prompt.ask("请输入日志文件路径或目录路径")
        
        if not os.path.exists(log_path):
            self.console.print("[red]路径不存在[/red]")
            input("\n按回车键返回主菜单...")
            return
        
        # 判断是文件还是目录
        if os.path.isfile(log_path):
            # 单文件分析
            self.console.print(f"\n[yellow]正在查找链路ID: {trace_id}...[/yellow]\n")
            trace_logs = self._parse_trace_logs(log_path, trace_id)
        else:
            # 目录扫描分析
            self.console.print(f"\n[yellow]正在扫描目录: {log_path}...[/yellow]")
            log_files = self._scan_log_files(log_path)
            
            if not log_files:
                self.console.print("[yellow]目录中未找到日志文件[/yellow]")
                input("\n按回车键返回主菜单...")
                return
            
            self.console.print(f"[green]找到 {len(log_files)} 个日志文件[/green]")
            self.console.print(f"[yellow]正在查找链路ID: {trace_id}...[/yellow]\n")
            
            # 解析所有文件
            trace_logs = self._parse_trace_logs_from_directory(log_files, trace_id)
        
        if not trace_logs['logs']:
            self.console.print(f"[yellow]未找到链路ID '{trace_id}' 的相关日志[/yellow]")
            input("\n按回车键返回主菜单...")
            return
        
        # 显示链路日志统计
        self._display_trace_statistics(trace_logs)
        
        # 显示链路日志详情
        self._display_trace_logs(trace_logs)
        
        # AI分析
        if Confirm.ask("\n是否需要AI智能分析？", default=True):
            self.console.print("\n[yellow]正在进行AI链路分析...[/yellow]\n")
            
            # 格式化链路日志
            log_content = self._format_trace_for_analysis(trace_logs, trace_id)
            analysis = self.llm.analyze_error_log(log_content)
            
            if analysis:
                self.console.print(Panel(
                    analysis,
                    title="[bold green]AI链路分析报告[/bold green]",
                    border_style="green"
                ))
            else:
                self.console.print("[red]AI分析失败[/red]")
        
        input("\n按回车键返回主菜单...")
    
    def _parse_log_file(self, log_file: str) -> Dict[str, Any]:
        """
        解析日志文件
        
        Args:
            log_file: 日志文件路径
            
        Returns:
            日志数据字典
        """
        errors = []
        error_types = []
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # 检测错误行（包含ERROR关键字或异常类名）
                if self._is_error_line(line):
                    error_entry = {
                        'timestamp': self._extract_timestamp(line),
                        'level': 'ERROR',
                        'message': line.strip(),
                        'stack_trace': [],
                        'exception_type': None
                    }
                    
                    # 提取异常类型
                    exception_match = re.search(r'(\w+Exception|\w+Error)', line)
                    if exception_match:
                        error_entry['exception_type'] = exception_match.group(1)
                        error_types.append(exception_match.group(1))
                    
                    # 收集堆栈跟踪
                    i += 1
                    while i < len(lines) and (lines[i].startswith('\t') or lines[i].startswith('    ') or lines[i].startswith('at ')):
                        error_entry['stack_trace'].append(lines[i].strip())
                        i += 1
                    
                    errors.append(error_entry)
                    continue
                
                i += 1
            
            # 统计错误类型
            error_type_counter = Counter(error_types)
            
            return {
                'file': log_file,
                'total_lines': len(lines),
                'error_count': len(errors),
                'errors': errors,
                'error_types': error_type_counter.most_common(10)
            }
        except Exception as e:
            self.console.print(f"[red]日志文件解析失败: {e}[/red]")
            return {
                'file': log_file,
                'total_lines': 0,
                'error_count': 0,
                'errors': [],
                'error_types': []
            }
    
    def _is_error_line(self, line: str) -> bool:
        """
        判断是否是错误行
        
        Args:
            line: 日志行
            
        Returns:
            是否是错误行
        """
        error_keywords = ['ERROR', 'Exception', 'Error:', 'Caused by:', 'at ']
        return any(keyword in line for keyword in error_keywords) and not line.startswith(('\t', '    ', 'at '))
    
    def _extract_timestamp(self, line: str) -> str:
        """
        提取时间戳
        
        Args:
            line: 日志行
            
        Returns:
            时间戳字符串
        """
        # 常见的时间戳格式
        patterns = [
            r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(0)
        
        return 'Unknown'
    
    def _display_statistics(self, log_data: Dict[str, Any]) -> None:
        """
        显示统计信息
        
        Args:
            log_data: 日志数据
        """
        self.console.print(f"[bold]日志文件:[/bold] {log_data['file']}")
        self.console.print(f"[bold]总行数:[/bold] {log_data['total_lines']}")
        self.console.print(f"[bold red]错误数量:[/bold red] {log_data['error_count']}\n")
        
        # 错误类型统计
        if log_data['error_types']:
            table = Table(title="错误类型统计 (Top 10)")
            table.add_column("异常类型", style="cyan")
            table.add_column("出现次数", style="red")
            
            for error_type, count in log_data['error_types']:
                table.add_row(error_type, str(count))
            
            self.console.print(table)
            self.console.print()
    
    def _display_errors(self, errors: List[Dict[str, Any]]) -> None:
        """
        显示错误详情
        
        Args:
            errors: 错误列表
        """
        display_count = min(5, len(errors))
        self.console.print(f"[bold]最近 {display_count} 个错误:[/bold]\n")
        
        for i, error in enumerate(errors[:display_count], 1):
            # 错误标题
            title = f"错误 #{i}"
            if error['exception_type']:
                title += f" - {error['exception_type']}"
            if error['timestamp'] != 'Unknown':
                title += f" ({error['timestamp']})"
            
            # 错误内容
            content_lines = [error['message']]
            if error['stack_trace']:
                content_lines.append("\n堆栈跟踪:")
                # 只显示前10行堆栈
                for line in error['stack_trace'][:10]:
                    content_lines.append(line)
                if len(error['stack_trace']) > 10:
                    content_lines.append(f"... 还有 {len(error['stack_trace']) - 10} 行")
            
            self.console.print(Panel(
                '\n'.join(content_lines),
                title=f"[bold red]{title}[/bold red]",
                border_style="red"
            ))
            self.console.print()
    
    def _format_errors_for_analysis(self, errors: List[Dict[str, Any]]) -> str:
        """
        格式化错误用于AI分析
        
        Args:
            errors: 错误列表
            
        Returns:
            格式化的文本
        """
        lines = []
        
        for i, error in enumerate(errors, 1):
            lines.append(f"\n{'='*60}")
            lines.append(f"错误 #{i}")
            lines.append(f"{'='*60}")
            
            if error['timestamp'] != 'Unknown':
                lines.append(f"时间: {error['timestamp']}")
            
            if error['exception_type']:
                lines.append(f"异常类型: {error['exception_type']}")
            
            lines.append(f"\n错误信息:")
            lines.append(error['message'])
            
            if error['stack_trace']:
                lines.append(f"\n堆栈跟踪:")
                for line in error['stack_trace'][:20]:  # 最多20行
                    lines.append(line)
        
        return '\n'.join(lines)
    
    def _parse_trace_logs(self, log_file: str, trace_id: str) -> Dict[str, Any]:
        """
        解析指定链路ID的日志
        
        Args:
            log_file: 日志文件路径
            trace_id: 链路ID
            
        Returns:
            链路日志数据字典
        """
        logs = []
        error_count = 0
        warn_count = 0
        info_count = 0
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # 支持多种链路ID格式
            trace_patterns = [
                rf'traceId[=:]\s*{re.escape(trace_id)}',
                rf'trace_id[=:]\s*{re.escape(trace_id)}',
                rf'\[{re.escape(trace_id)}\]',
                rf'requestId[=:]\s*{re.escape(trace_id)}',
                rf'request_id[=:]\s*{re.escape(trace_id)}',
                re.escape(trace_id)  # 直接匹配
            ]
            
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # 检查是否包含链路ID
                if any(re.search(pattern, line, re.IGNORECASE) for pattern in trace_patterns):
                    log_entry = {
                        'line_number': i + 1,
                        'timestamp': self._extract_timestamp(line),
                        'level': self._extract_log_level(line),
                        'content': line.strip(),
                        'stack_trace': []
                    }
                    
                    # 统计日志级别
                    level = log_entry['level']
                    if level == 'ERROR':
                        error_count += 1
                    elif level == 'WARN':
                        warn_count += 1
                    elif level == 'INFO':
                        info_count += 1
                    
                    # 如果是错误日志，收集堆栈跟踪
                    if level == 'ERROR':
                        i += 1
                        while i < len(lines) and (lines[i].startswith('\t') or 
                                                   lines[i].startswith('    ') or 
                                                   lines[i].startswith('at ')):
                            log_entry['stack_trace'].append(lines[i].strip())
                            i += 1
                        i -= 1
                    
                    logs.append(log_entry)
                
                i += 1
            
            return {
                'trace_id': trace_id,
                'file': log_file,
                'total_logs': len(logs),
                'error_count': error_count,
                'warn_count': warn_count,
                'info_count': info_count,
                'logs': logs
            }
        except Exception as e:
            self.console.print(f"[red]链路日志解析失败: {e}[/red]")
            return {
                'trace_id': trace_id,
                'file': log_file,
                'total_logs': 0,
                'error_count': 0,
                'warn_count': 0,
                'info_count': 0,
                'logs': []
            }
    
    def _extract_log_level(self, line: str) -> str:
        """
        提取日志级别
        
        Args:
            line: 日志行
            
        Returns:
            日志级别
        """
        if 'ERROR' in line:
            return 'ERROR'
        elif 'WARN' in line:
            return 'WARN'
        elif 'INFO' in line:
            return 'INFO'
        elif 'DEBUG' in line:
            return 'DEBUG'
        else:
            return 'UNKNOWN'
    
    def _display_trace_statistics(self, trace_logs: Dict[str, Any]) -> None:
        """
        显示链路日志统计信息
        
        Args:
            trace_logs: 链路日志数据
        """
        self.console.print(f"[bold]链路ID:[/bold] {trace_logs['trace_id']}")
        self.console.print(f"[bold]日志文件:[/bold] {trace_logs['file']}")
        self.console.print(f"[bold]相关日志数:[/bold] {trace_logs['total_logs']}\n")
        
        # 日志级别统计
        table = Table(title="日志级别统计")
        table.add_column("级别", style="cyan")
        table.add_column("数量", style="white")
        
        if trace_logs['error_count'] > 0:
            table.add_row("ERROR", str(trace_logs['error_count']), style="red")
        if trace_logs['warn_count'] > 0:
            table.add_row("WARN", str(trace_logs['warn_count']), style="yellow")
        if trace_logs['info_count'] > 0:
            table.add_row("INFO", str(trace_logs['info_count']), style="green")
        
        self.console.print(table)
        self.console.print()
    
    def _display_trace_logs(self, trace_logs: Dict[str, Any]) -> None:
        """
        显示链路日志详情
        
        Args:
            trace_logs: 链路日志数据
        """
        logs = trace_logs['logs']
        
        # 限制显示数量
        display_count = min(20, len(logs))
        self.console.print(f"[bold]显示前 {display_count} 条日志:[/bold]\n")
        
        for i, log in enumerate(logs[:display_count], 1):
            # 根据日志级别设置颜色
            if log['level'] == 'ERROR':
                level_color = "red"
                border_style = "red"
            elif log['level'] == 'WARN':
                level_color = "yellow"
                border_style = "yellow"
            else:
                level_color = "green"
                border_style = "cyan"
            
            # 日志标题
            title = f"日志 #{i} - {log['level']}"
            if log['timestamp'] != 'Unknown':
                title += f" ({log['timestamp']})"
            if 'source_file' in log:
                title += f" - {log['source_file']}"
            
            # 日志内容
            content_lines = [log['content']]
            if log['stack_trace']:
                content_lines.append("\n堆栈跟踪:")
                for line in log['stack_trace'][:15]:
                    content_lines.append(line)
                if len(log['stack_trace']) > 15:
                    content_lines.append(f"... 还有 {len(log['stack_trace']) - 15} 行")
            
            self.console.print(Panel(
                '\n'.join(content_lines),
                title=f"[bold {level_color}]{title}[/bold {level_color}]",
                border_style=border_style
            ))
            self.console.print()
        
        if len(logs) > display_count:
            self.console.print(f"[yellow]... 还有 {len(logs) - display_count} 条日志未显示[/yellow]\n")
    
    def _format_trace_for_analysis(self, trace_logs: Dict[str, Any], trace_id: str) -> str:
        """
        格式化链路日志用于AI分析
        
        Args:
            trace_logs: 链路日志数据
            trace_id: 链路ID
            
        Returns:
            格式化的文本
        """
        lines = []
        lines.append(f"链路ID: {trace_id}")
        lines.append(f"相关日志总数: {trace_logs['total_logs']}")
        lines.append(f"ERROR数量: {trace_logs['error_count']}")
        lines.append(f"WARN数量: {trace_logs['warn_count']}")
        lines.append(f"INFO数量: {trace_logs['info_count']}")
        
        # 如果是多文件，显示来源文件
        if 'source_files' in trace_logs and trace_logs['source_files']:
            lines.append(f"涉及文件数: {len(trace_logs['source_files'])}")
            lines.append(f"文件列表: {', '.join([os.path.basename(f) for f in trace_logs['source_files']])}")
        
        lines.append("\n" + "="*80)
        lines.append("完整链路日志:")
        lines.append("="*80)
        
        for i, log in enumerate(trace_logs['logs'], 1):
            lines.append(f"\n[日志 #{i}] {log['level']}")
            if log['timestamp'] != 'Unknown':
                lines.append(f"时间: {log['timestamp']}")
            if 'source_file' in log:
                lines.append(f"来源: {log['source_file']}")
            lines.append(f"内容: {log['content']}")
            
            if log['stack_trace']:
                lines.append("堆栈跟踪:")
                for line in log['stack_trace']:
                    lines.append(f"  {line}")
        
        lines.append("\n" + "="*80)
        lines.append("分析要求:")
        lines.append("="*80)
        lines.append("请分析此链路的完整调用过程，包括：")
        lines.append("1. 请求的完整链路流程")
        lines.append("2. 每个环节的执行情况")
        lines.append("3. 异常发生的具体位置和原因")
        lines.append("4. 上下游服务调用关系")
        lines.append("5. 根本原因分析")
        lines.append("6. 问题解决方案")
        lines.append("7. 防止类似问题的建议")
        
        return '\n'.join(lines)
    
    def _scan_log_files(self, directory: str) -> List[str]:
        """
        扫描目录下的所有日志文件
        
        Args:
            directory: 目录路径
            
        Returns:
            日志文件路径列表
        """
        log_files = []
        log_extensions = ['.log', '.txt', '.out']
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    # 检查文件扩展名
                    if any(file.endswith(ext) for ext in log_extensions):
                        file_path = os.path.join(root, file)
                        log_files.append(file_path)
            
            # 按文件名排序
            log_files.sort()
            return log_files
        except Exception as e:
            self.console.print(f"[red]扫描目录失败: {e}[/red]")
            return []
    
    def _parse_trace_logs_from_directory(self, log_files: List[str], trace_id: str) -> Dict[str, Any]:
        """
        从多个日志文件中解析指定链路ID的日志
        
        Args:
            log_files: 日志文件路径列表
            trace_id: 链路ID
            
        Returns:
            合并后的链路日志数据字典
        """
        all_logs = []
        error_count = 0
        warn_count = 0
        info_count = 0
        source_files = []
        
        from rich.progress import Progress, SpinnerColumn, TextColumn
        
        # 使用进度条显示扫描进度
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=self.console
        ) as progress:
            task = progress.add_task(f"扫描文件中...", total=len(log_files))
            
            for log_file in log_files:
                progress.update(task, description=f"扫描: {os.path.basename(log_file)}")
                
                # 解析单个文件
                file_logs = self._parse_trace_logs(log_file, trace_id)
                
                if file_logs['logs']:
                    source_files.append(log_file)
                    
                    # 为每条日志添加来源文件信息
                    for log in file_logs['logs']:
                        log['source_file'] = os.path.basename(log_file)
                    
                    all_logs.extend(file_logs['logs'])
                    error_count += file_logs['error_count']
                    warn_count += file_logs['warn_count']
                    info_count += file_logs['info_count']
                
                progress.advance(task)
        
        # 按时间戳排序所有日志
        all_logs = self._sort_logs_by_timestamp(all_logs)
        
        self.console.print(f"[green]✓ 在 {len(source_files)} 个文件中找到相关日志[/green]")
        if source_files:
            self.console.print(f"[cyan]涉及文件: {', '.join([os.path.basename(f) for f in source_files])}[/cyan]\n")
        
        return {
            'trace_id': trace_id,
            'file': f"目录扫描 ({len(log_files)} 个文件)",
            'source_files': source_files,
            'total_logs': len(all_logs),
            'error_count': error_count,
            'warn_count': warn_count,
            'info_count': info_count,
            'logs': all_logs
        }
    
    def _sort_logs_by_timestamp(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        按时间戳排序日志
        
        Args:
            logs: 日志列表
            
        Returns:
            排序后的日志列表
        """
        from datetime import datetime
        
        def parse_timestamp(log: Dict[str, Any]) -> datetime:
            """解析时间戳为datetime对象"""
            timestamp = log.get('timestamp', 'Unknown')
            if timestamp == 'Unknown':
                return datetime.min
            
            # 尝试多种时间格式
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%d/%m/%Y %H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    # 处理可能的毫秒部分
                    ts = timestamp.split('.')[0] if '.' in timestamp and 'T' not in timestamp else timestamp
                    return datetime.strptime(ts, fmt)
                except ValueError:
                    continue
            
            return datetime.min
        
        # 排序
        try:
            sorted_logs = sorted(logs, key=parse_timestamp)
            return sorted_logs
        except Exception as e:
            self.console.print(f"[yellow]日志排序失败，使用原始顺序: {e}[/yellow]")
            return logs
