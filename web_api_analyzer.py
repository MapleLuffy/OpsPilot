"""
Web接口性能分析模块
"""
import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm


class WebApiAnalyzer:
    """Web接口性能分析器"""
    
    def __init__(self, llm_client):
        """
        初始化Web接口分析器
        
        Args:
            llm_client: LLM客户端实例
        """
        self.llm = llm_client
        self.console = Console()
    
    def run(self) -> None:
        """运行Web接口分析功能"""
        self.console.print("\n[bold cyan]Web接口性能分析[/bold cyan]\n")
        
        # 选择工程目录
        project_path = Prompt.ask("请输入SpringBoot工程代码路径")
        
        if not os.path.exists(project_path):
            self.console.print("[red]路径不存在[/red]")
            input("\n按回车键返回主菜单...")
            return
        
        # 扫描Controller
        self.console.print("\n[yellow]正在扫描Controller接口...[/yellow]\n")
        controllers = self._scan_controllers(project_path)
        
        if not controllers:
            self.console.print("[yellow]未找到Controller接口[/yellow]")
            input("\n按回车键返回主菜单...")
            return
        
        # 显示Controller统计
        self._display_controllers(controllers)
        
        # 生成分析报告
        if Confirm.ask("\n是否生成AI性能分析报告？", default=True):
            self.console.print("\n[yellow]正在生成分析报告...[/yellow]\n")
            
            # 格式化数据
            api_data = self._format_api_data(controllers)
            analysis = self.llm.analyze_web_api(api_data)
            
            if analysis:
                self.console.print(Panel(
                    analysis,
                    title="[bold green]AI分析报告[/bold green]",
                    border_style="green"
                ))
            else:
                self.console.print("[red]分析报告生成失败[/red]")
        
        input("\n按回车键返回主菜单...")
    
    def _scan_controllers(self, project_path: str) -> List[Dict[str, Any]]:
        """
        扫描Controller接口
        
        Args:
            project_path: 项目路径
            
        Returns:
            Controller列表
        """
        controllers = []
        
        # 查找Java文件
        for root, dirs, files in os.walk(project_path):
            # 跳过常见的非源码目录
            dirs[:] = [d for d in dirs if d not in ['target', 'build', '.git', '.idea', 'node_modules']]
            
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    controller_info = self._parse_controller(file_path)
                    if controller_info:
                        controllers.append(controller_info)
        
        return controllers
    
    def _parse_controller(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        解析Controller文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Controller信息字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否是Controller类
            if not (re.search(r'@RestController', content) or re.search(r'@Controller', content)):
                return None
            
            # 提取类名
            class_match = re.search(r'public\s+class\s+(\w+)', content)
            class_name = class_match.group(1) if class_match else 'Unknown'
            
            # 提取类级别的RequestMapping
            class_mapping = ''
            class_mapping_match = re.search(r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']', content)
            if class_mapping_match:
                class_mapping = class_mapping_match.group(1)
            
            # 提取所有接口方法
            methods = self._extract_methods(content, class_mapping)
            
            if not methods:
                return None
            
            return {
                'file': file_path,
                'class_name': class_name,
                'base_path': class_mapping,
                'methods': methods,
                'method_count': len(methods)
            }
        except Exception as e:
            self.console.print(f"[yellow]解析文件失败 {file_path}: {e}[/yellow]")
            return None
    
    def _extract_methods(self, content: str, base_path: str) -> List[Dict[str, Any]]:
        """
        提取Controller方法
        
        Args:
            content: 文件内容
            base_path: 基础路径
            
        Returns:
            方法列表
        """
        methods = []
        
        # 匹配各种Mapping注解
        mapping_patterns = [
            (r'@GetMapping\s*\(\s*["\']([^"\']+)["\']', 'GET'),
            (r'@PostMapping\s*\(\s*["\']([^"\']+)["\']', 'POST'),
            (r'@PutMapping\s*\(\s*["\']([^"\']+)["\']', 'PUT'),
            (r'@DeleteMapping\s*\(\s*["\']([^"\']+)["\']', 'DELETE'),
            (r'@PatchMapping\s*\(\s*["\']([^"\']+)["\']', 'PATCH'),
            (r'@RequestMapping\s*\([^)]*value\s*=\s*["\']([^"\']+)["\'][^)]*method\s*=\s*RequestMethod\.(\w+)', None),
        ]
        
        for pattern, method_type in mapping_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                if method_type:
                    path = match.group(1)
                    http_method = method_type
                else:
                    path = match.group(1)
                    http_method = match.group(2)
                
                # 提取方法名（往后查找）
                start_pos = match.end()
                method_match = re.search(r'public\s+\w+(?:<[^>]+>)?\s+(\w+)\s*\(', content[start_pos:start_pos+200])
                method_name = method_match.group(1) if method_match else 'unknown'
                
                full_path = base_path + path if not path.startswith('/') else path
                
                methods.append({
                    'method_name': method_name,
                    'http_method': http_method,
                    'path': full_path,
                    'full_signature': f"{http_method} {full_path}"
                })
        
        return methods
    
    def _display_controllers(self, controllers: List[Dict[str, Any]]) -> None:
        """
        显示Controller统计
        
        Args:
            controllers: Controller列表
        """
        # 统计信息
        total_controllers = len(controllers)
        total_methods = sum(c['method_count'] for c in controllers)
        
        self.console.print(f"[bold]发现 {total_controllers} 个Controller，共 {total_methods} 个接口[/bold]\n")
        
        # 显示详细列表
        for controller in controllers[:10]:  # 只显示前10个
            table = Table(title=f"{controller['class_name']} ({controller['method_count']} 个接口)")
            table.add_column("HTTP方法", style="cyan")
            table.add_column("路径", style="white")
            table.add_column("方法名", style="yellow")
            
            for method in controller['methods']:
                table.add_row(
                    method['http_method'],
                    method['path'],
                    method['method_name']
                )
            
            self.console.print(table)
            self.console.print()
        
        if len(controllers) > 10:
            self.console.print(f"[yellow]... 还有 {len(controllers) - 10} 个Controller未显示[/yellow]\n")
    
    def _format_api_data(self, controllers: List[Dict[str, Any]]) -> str:
        """
        格式化API数据用于分析
        
        Args:
            controllers: Controller列表
            
        Returns:
            格式化的文本
        """
        lines = []
        lines.append(f"总计: {len(controllers)} 个Controller\n")
        
        # 按HTTP方法统计
        method_stats = {}
        for controller in controllers:
            for method in controller['methods']:
                http_method = method['http_method']
                method_stats[http_method] = method_stats.get(http_method, 0) + 1
        
        lines.append("接口统计:")
        for method, count in sorted(method_stats.items()):
            lines.append(f"  {method}: {count} 个")
        
        lines.append("\n详细接口列表:")
        for controller in controllers:
            lines.append(f"\n{controller['class_name']}:")
            for method in controller['methods']:
                lines.append(f"  {method['http_method']} {method['path']} -> {method['method_name']}()")
        
        lines.append("\n请分析以下方面:")
        lines.append("1. RESTful API设计规范性")
        lines.append("2. 潜在性能瓶颈（如同步IO、大数据量查询等）")
        lines.append("3. 接口命名和路径设计建议")
        lines.append("4. 推荐的监控指标和告警策略")
        
        return '\n'.join(lines)
