"""
JVM分析模块
"""
import subprocess
import re
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm


class JVMAnalyzer:
    """JVM分析器"""
    
    def __init__(self, llm_client, config_manager):
        """
        初始化JVM分析器
        
        Args:
            llm_client: LLM客户端实例
            config_manager: 配置管理器实例
        """
        self.llm = llm_client
        self.config = config_manager
        self.console = Console()
        self.large_object_threshold = config_manager.get('jvm.large_object_threshold', 10)
    
    def run(self) -> None:
        """运行JVM分析功能"""
        self.console.print("\n[bold cyan]JVM情况分析[/bold cyan]\n")
        
        # 获取Java进程列表
        java_processes = self._get_java_processes()
        
        if not java_processes:
            self.console.print("[yellow]未检测到运行中的Java进程[/yellow]")
            input("\n按回车键返回主菜单...")
            return
        
        # 显示Java进程列表
        self.console.print("[bold]检测到以下Java进程:[/bold]\n")
        for i, (pid, name) in enumerate(java_processes, 1):
            self.console.print(f"{i}. PID: {pid} - {name}")
        
        # 选择进程
        choice = Prompt.ask(
            "\n请选择要分析的进程编号（输入0返回主菜单）",
            choices=[str(i) for i in range(len(java_processes) + 1)],
            default="1"
        )
        
        if choice == "0":
            return
        
        pid = java_processes[int(choice) - 1][0]
        
        # 收集JVM信息
        self.console.print("\n[yellow]正在收集JVM信息...[/yellow]\n")
        jvm_data = self._collect_jvm_data(pid)
        
        if not jvm_data:
            self.console.print("[red]JVM信息收集失败[/red]")
            input("\n按回车键返回主菜单...")
            return
        
        # 显示JVM信息
        self._display_jvm_data(jvm_data)
        
        # AI分析
        if Confirm.ask("\n是否需要AI智能分析？", default=True):
            self.console.print("\n[yellow]正在进行AI分析...[/yellow]\n")
            
            # 格式化数据用于分析
            analysis_text = self._format_for_analysis(jvm_data)
            analysis = self.llm.analyze_jvm(analysis_text)
            
            if analysis:
                self.console.print(Panel(
                    analysis,
                    title="[bold green]AI分析结果[/bold green]",
                    border_style="green"
                ))
            else:
                self.console.print("[red]AI分析失败[/red]")
        
        input("\n按回车键返回主菜单...")
    
    def _get_java_processes(self) -> List[tuple]:
        """
        获取Java进程列表
        
        Returns:
            [(pid, name), ...] 列表
        """
        try:
            result = subprocess.run(
                ['jps', '-l'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            processes = []
            for line in result.stdout.strip().split('\n'):
                if line and 'Jps' not in line:
                    parts = line.split(None, 1)
                    if len(parts) >= 1:
                        pid = parts[0]
                        name = parts[1] if len(parts) > 1 else 'Unknown'
                        processes.append((pid, name))
            
            return processes
        except Exception as e:
            self.console.print(f"[red]获取Java进程失败: {e}[/red]")
            return []
    
    def _collect_jvm_data(self, pid: str) -> Optional[Dict[str, Any]]:
        """
        收集JVM数据
        
        Args:
            pid: Java进程ID
            
        Returns:
            JVM数据字典
        """
        data = {
            'pid': pid,
            'gc_info': self._get_gc_info(pid),
            'memory_info': self._get_memory_info(pid),
            'gc_collector': self._get_gc_collector(pid),
            'heap_histogram': self._get_heap_histogram(pid)
        }
        
        return data if any(data.values()) else None
    
    def _get_gc_info(self, pid: str) -> Optional[Dict[str, Any]]:
        """
        获取GC信息
        
        Args:
            pid: Java进程ID
            
        Returns:
            GC信息字典
        """
        try:
            result = subprocess.run(
                ['jstat', '-gcutil', pid, '1000', '1'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return None
            
            headers = lines[0].split()
            values = lines[1].split()
            
            gc_info = {}
            for i, header in enumerate(headers):
                if i < len(values):
                    try:
                        gc_info[header] = float(values[i])
                    except ValueError:
                        gc_info[header] = values[i]
            
            return gc_info
        except Exception as e:
            self.console.print(f"[yellow]获取GC信息失败: {e}[/yellow]")
            return None
    
    def _get_memory_info(self, pid: str) -> Optional[Dict[str, Any]]:
        """
        获取内存信息
        
        Args:
            pid: Java进程ID
            
        Returns:
            内存信息字典
        """
        try:
            result = subprocess.run(
                ['jstat', '-gc', pid],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return None
            
            headers = lines[0].split()
            values = lines[1].split()
            
            memory_info = {}
            for i, header in enumerate(headers):
                if i < len(values):
                    try:
                        memory_info[header] = float(values[i])
                    except ValueError:
                        memory_info[header] = values[i]
            
            return memory_info
        except Exception as e:
            self.console.print(f"[yellow]获取内存信息失败: {e}[/yellow]")
            return None
    
    def _get_gc_collector(self, pid: str) -> Optional[str]:
        """
        获取垃圾回收器类型
        
        Args:
            pid: Java进程ID
            
        Returns:
            垃圾回收器名称
        """
        try:
            result = subprocess.run(
                ['jinfo', '-flag', 'UseG1GC', pid],
                capture_output=True,
                text=True,
                timeout=10
            )
            if 'UseG1GC' in result.stdout and '+' in result.stdout:
                return "G1GC"
            
            result = subprocess.run(
                ['jinfo', '-flag', 'UseParallelGC', pid],
                capture_output=True,
                text=True,
                timeout=10
            )
            if 'UseParallelGC' in result.stdout and '+' in result.stdout:
                return "ParallelGC"
            
            result = subprocess.run(
                ['jinfo', '-flag', 'UseConcMarkSweepGC', pid],
                capture_output=True,
                text=True,
                timeout=10
            )
            if 'UseConcMarkSweepGC' in result.stdout and '+' in result.stdout:
                return "CMS"
            
            result = subprocess.run(
                ['jinfo', '-flag', 'UseZGC', pid],
                capture_output=True,
                text=True,
                timeout=10
            )
            if 'UseZGC' in result.stdout and '+' in result.stdout:
                return "ZGC"
            
            return "Unknown/Default"
        except Exception as e:
            self.console.print(f"[yellow]获取GC收集器信息失败: {e}[/yellow]")
            return None
    
    def _get_heap_histogram(self, pid: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取堆对象统计（大对象）
        
        Args:
            pid: Java进程ID
            
        Returns:
            大对象列表
        """
        try:
            result = subprocess.run(
                ['jmap', '-histo:live', pid],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            lines = result.stdout.strip().split('\n')
            large_objects = []
            
            # 解析堆对象统计
            for line in lines[3:]:  # 跳过前3行标题
                if line.strip() and not line.startswith('Total'):
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            size_bytes = int(parts[2])
                            size_mb = size_bytes / (1024 * 1024)
                            
                            # 只保留超过阈值的对象
                            if size_mb >= self.large_object_threshold:
                                large_objects.append({
                                    'num': parts[0],
                                    'instances': parts[1],
                                    'bytes': size_bytes,
                                    'size_mb': round(size_mb, 2),
                                    'class_name': parts[3]
                                })
                        except (ValueError, IndexError):
                            continue
            
            # 按大小排序
            large_objects.sort(key=lambda x: x['size_mb'], reverse=True)
            
            return large_objects[:20]  # 只返回前20个
        except Exception as e:
            self.console.print(f"[yellow]获取堆对象统计失败: {e}[/yellow]")
            return None
    
    def _display_jvm_data(self, data: Dict[str, Any]) -> None:
        """
        显示JVM数据
        
        Args:
            data: JVM数据字典
        """
        # GC信息
        if data.get('gc_info'):
            table = Table(title=f"GC情况 (PID: {data['pid']})")
            table.add_column("指标", style="cyan")
            table.add_column("值", style="white")
            
            gc_info = data['gc_info']
            descriptions = {
                'S0': 'Survivor 0区使用率(%)',
                'S1': 'Survivor 1区使用率(%)',
                'E': 'Eden区使用率(%)',
                'O': '老年代使用率(%)',
                'M': 'Metaspace使用率(%)',
                'CCS': '压缩类空间使用率(%)',
                'YGC': 'Young GC次数',
                'YGCT': 'Young GC总时间(s)',
                'FGC': 'Full GC次数',
                'FGCT': 'Full GC总时间(s)',
                'GCT': 'GC总时间(s)'
            }
            
            for key, value in gc_info.items():
                desc = descriptions.get(key, key)
                table.add_row(desc, str(value))
            
            self.console.print(table)
            self.console.print()
        
        # 垃圾回收器
        if data.get('gc_collector'):
            self.console.print(f"[bold]当前垃圾回收器:[/bold] [green]{data['gc_collector']}[/green]\n")
        
        # 内存信息
        if data.get('memory_info'):
            table = Table(title="内存详情")
            table.add_column("区域", style="cyan")
            table.add_column("容量(KB)", style="white")
            table.add_column("使用(KB)", style="white")
            
            mem = data['memory_info']
            if 'S0C' in mem and 'S0U' in mem:
                table.add_row("Survivor 0", f"{mem.get('S0C', 0):.2f}", f"{mem.get('S0U', 0):.2f}")
            if 'S1C' in mem and 'S1U' in mem:
                table.add_row("Survivor 1", f"{mem.get('S1C', 0):.2f}", f"{mem.get('S1U', 0):.2f}")
            if 'EC' in mem and 'EU' in mem:
                table.add_row("Eden", f"{mem.get('EC', 0):.2f}", f"{mem.get('EU', 0):.2f}")
            if 'OC' in mem and 'OU' in mem:
                table.add_row("老年代", f"{mem.get('OC', 0):.2f}", f"{mem.get('OU', 0):.2f}")
            if 'MC' in mem and 'MU' in mem:
                table.add_row("Metaspace", f"{mem.get('MC', 0):.2f}", f"{mem.get('MU', 0):.2f}")
            
            self.console.print(table)
            self.console.print()
        
        # 大对象
        if data.get('heap_histogram'):
            table = Table(title=f"老年代大对象 (>= {self.large_object_threshold}MB)")
            table.add_column("排名", style="cyan")
            table.add_column("实例数", style="white")
            table.add_column("大小(MB)", style="yellow")
            table.add_column("类名", style="white")
            
            for i, obj in enumerate(data['heap_histogram'][:10], 1):
                table.add_row(
                    str(i),
                    obj['instances'],
                    f"{obj['size_mb']:.2f}",
                    obj['class_name']
                )
            
            self.console.print(table)
    
    def _format_for_analysis(self, data: Dict[str, Any]) -> str:
        """
        格式化数据用于AI分析
        
        Args:
            data: JVM数据
            
        Returns:
            格式化的文本
        """
        lines = [f"JVM进程 PID: {data['pid']}\n"]
        
        if data.get('gc_collector'):
            lines.append(f"垃圾回收器: {data['gc_collector']}\n")
        
        if data.get('gc_info'):
            lines.append("\nGC统计:")
            for key, value in data['gc_info'].items():
                lines.append(f"  {key}: {value}")
        
        if data.get('memory_info'):
            lines.append("\n内存使用:")
            for key, value in data['memory_info'].items():
                lines.append(f"  {key}: {value}")
        
        if data.get('heap_histogram'):
            lines.append(f"\n大对象 (>= {self.large_object_threshold}MB):")
            for obj in data['heap_histogram'][:10]:
                lines.append(f"  {obj['class_name']}: {obj['size_mb']}MB ({obj['instances']} 实例)")
        
        return '\n'.join(lines)
