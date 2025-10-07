"""
系统指标分析模块
"""
import psutil
import platform
from datetime import datetime
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


class SystemAnalyzer:
    """系统指标分析器"""
    
    def __init__(self, llm_client):
        """
        初始化系统分析器
        
        Args:
            llm_client: LLM客户端实例
        """
        self.llm = llm_client
        self.console = Console()
    
    def run(self) -> None:
        """运行系统分析功能"""
        self.console.print("\n[bold cyan]操作系统指标分析[/bold cyan]\n")
        
        # 收集系统指标
        self.console.print("[yellow]正在收集系统指标...[/yellow]\n")
        metrics = self._collect_metrics()
        
        # 显示指标
        self._display_metrics(metrics)
        
        # AI分析
        from rich.prompt import Confirm
        if Confirm.ask("\n是否需要AI智能分析？", default=True):
            self.console.print("\n[yellow]正在进行AI分析...[/yellow]\n")
            analysis = self.llm.analyze_system_metrics(metrics)
            
            if analysis:
                self.console.print(Panel(
                    analysis,
                    title="[bold green]AI分析结果[/bold green]",
                    border_style="green"
                ))
            else:
                self.console.print("[red]AI分析失败[/red]")
        
        input("\n按回车键返回主菜单...")
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """
        收集系统指标
        
        Returns:
            系统指标字典
        """
        # CPU信息
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # 内存信息
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # 网络信息
        net_io = psutil.net_io_counters()
        
        # 系统信息
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        metrics = {
            'system': {
                'platform': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
                'uptime': str(uptime).split('.')[0]
            },
            'cpu': {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': cpu_count,
                'current_freq': f"{cpu_freq.current:.2f} MHz" if cpu_freq else "N/A",
                'max_freq': f"{cpu_freq.max:.2f} MHz" if cpu_freq else "N/A",
                'usage_per_core': [f"{p:.1f}%" for p in cpu_percent],
                'average_usage': f"{sum(cpu_percent) / len(cpu_percent):.1f}%"
            },
            'memory': {
                'total': f"{mem.total / (1024**3):.2f} GB",
                'available': f"{mem.available / (1024**3):.2f} GB",
                'used': f"{mem.used / (1024**3):.2f} GB",
                'percent': f"{mem.percent}%",
                'swap_total': f"{swap.total / (1024**3):.2f} GB",
                'swap_used': f"{swap.used / (1024**3):.2f} GB",
                'swap_percent': f"{swap.percent}%"
            },
            'disk': {
                'total': f"{disk.total / (1024**3):.2f} GB",
                'used': f"{disk.used / (1024**3):.2f} GB",
                'free': f"{disk.free / (1024**3):.2f} GB",
                'percent': f"{disk.percent}%",
                'read_count': disk_io.read_count if disk_io else 'N/A',
                'write_count': disk_io.write_count if disk_io else 'N/A',
                'read_bytes': f"{disk_io.read_bytes / (1024**3):.2f} GB" if disk_io else 'N/A',
                'write_bytes': f"{disk_io.write_bytes / (1024**3):.2f} GB" if disk_io else 'N/A'
            },
            'network': {
                'bytes_sent': f"{net_io.bytes_sent / (1024**3):.2f} GB",
                'bytes_recv': f"{net_io.bytes_recv / (1024**3):.2f} GB",
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errors_in': net_io.errin,
                'errors_out': net_io.errout,
                'drop_in': net_io.dropin,
                'drop_out': net_io.dropout
            }
        }
        
        return metrics
    
    def _display_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        显示系统指标
        
        Args:
            metrics: 系统指标字典
        """
        # 系统信息
        table = Table(title="系统信息", show_header=False)
        table.add_column("项目", style="cyan")
        table.add_column("值", style="white")
        
        for key, value in metrics['system'].items():
            table.add_row(key.replace('_', ' ').title(), str(value))
        
        self.console.print(table)
        self.console.print()
        
        # CPU信息
        table = Table(title="CPU信息")
        table.add_column("项目", style="cyan")
        table.add_column("值", style="white")
        
        for key, value in metrics['cpu'].items():
            if key != 'usage_per_core':
                table.add_row(key.replace('_', ' ').title(), str(value))
        
        self.console.print(table)
        self.console.print()
        
        # 内存信息
        table = Table(title="内存信息")
        table.add_column("项目", style="cyan")
        table.add_column("值", style="white")
        
        mem_percent = float(metrics['memory']['percent'].rstrip('%'))
        mem_color = "green" if mem_percent < 70 else "yellow" if mem_percent < 85 else "red"
        
        for key, value in metrics['memory'].items():
            style = mem_color if 'percent' in key else "white"
            table.add_row(key.replace('_', ' ').title(), str(value), style=style)
        
        self.console.print(table)
        self.console.print()
        
        # 磁盘信息
        table = Table(title="磁盘信息")
        table.add_column("项目", style="cyan")
        table.add_column("值", style="white")
        
        disk_percent = float(metrics['disk']['percent'].rstrip('%'))
        disk_color = "green" if disk_percent < 70 else "yellow" if disk_percent < 85 else "red"
        
        for key, value in metrics['disk'].items():
            style = disk_color if key == 'percent' else "white"
            table.add_row(key.replace('_', ' ').title(), str(value), style=style)
        
        self.console.print(table)
        self.console.print()
        
        # 网络信息
        table = Table(title="网络信息")
        table.add_column("项目", style="cyan")
        table.add_column("值", style="white")
        
        for key, value in metrics['network'].items():
            table.add_row(key.replace('_', ' ').title(), str(value))
        
        self.console.print(table)
