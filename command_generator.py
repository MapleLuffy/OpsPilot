"""
Linux命令生成模块
"""
import os
import re
import subprocess
from typing import Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt


class CommandGenerator:
    """Linux命令生成器"""
    
    def __init__(self, llm_client, config_manager):
        """
        初始化命令生成器
        
        Args:
            llm_client: LLM客户端实例
            config_manager: 配置管理器实例
        """
        self.llm = llm_client
        self.config = config_manager
        self.console = Console()
        self.dangerous_commands = config_manager.get('command_check.dangerous_commands', [])
    
    def run(self) -> None:
        """运行命令生成功能"""
        self.console.print("\n[bold cyan]Linux命令生成助手[/bold cyan]\n")
        
        while True:
            user_request = Prompt.ask("\n请描述你想执行的操作（输入'q'返回主菜单）")
            
            if user_request.lower() == 'q':
                break
            
            if not user_request.strip():
                continue
            
            # 生成命令
            self.console.print("\n[yellow]正在生成命令...[/yellow]")
            command = self.llm.generate_command(user_request)
            
            if not command:
                self.console.print("[red]命令生成失败，请重试[/red]")
                continue
            
            # 清理命令（去除可能的markdown格式）
            command = self._clean_command(command)
            
            # 显示生成的命令
            self.console.print(Panel(
                command,
                title="[bold green]生成的命令[/bold green]",
                border_style="green"
            ))
            
            # 风险检查
            risk_level, risk_reasons = self._check_command_risk(command)
            
            if risk_level == "high":
                self.console.print("\n[bold red]⚠ 警告：检测到高危命令！[/bold red]")
                for reason in risk_reasons:
                    self.console.print(f"  • {reason}")
                
                if not Confirm.ask("\n确认要执行此命令吗？", default=False):
                    self.console.print("[yellow]已取消执行[/yellow]")
                    continue
            elif risk_level == "medium":
                self.console.print("\n[bold yellow]⚠ 注意：检测到中危命令[/bold yellow]")
                for reason in risk_reasons:
                    self.console.print(f"  • {reason}")
            
            # 询问是否执行
            if Confirm.ask("\n是否执行此命令？", default=False):
                self._execute_command(command)
    
    def _clean_command(self, command: str) -> str:
        """
        清理命令字符串
        
        Args:
            command: 原始命令
            
        Returns:
            清理后的命令
        """
        # 去除markdown代码块标记
        command = re.sub(r'^```(?:bash|shell|sh)?\s*\n?', '', command)
        command = re.sub(r'\n?```\s*$', '', command)
        
        # 去除首尾空白
        command = command.strip()
        
        # 如果有多行，只取第一行（通常是命令本身）
        lines = [line for line in command.split('\n') if line.strip() and not line.strip().startswith('#')]
        if lines:
            command = lines[0]
        
        return command
    
    def _check_command_risk(self, command: str) -> Tuple[str, list]:
        """
        检查命令风险等级
        
        Args:
            command: 要检查的命令
            
        Returns:
            (风险等级, 风险原因列表)
            风险等级: "low", "medium", "high"
        """
        risks = []
        risk_level = "low"
        
        # 检查高危命令
        for dangerous in self.dangerous_commands:
            if dangerous.lower() in command.lower():
                risks.append(f"包含危险操作: {dangerous}")
                risk_level = "high"
        
        # 检查sudo/root权限
        if command.strip().startswith('sudo ') or 'sudo ' in command:
            risks.append("需要root权限执行")
            if risk_level == "low":
                risk_level = "medium"
        
        # 检查递归删除
        if re.search(r'rm\s+.*-[rf]{1,2}', command) or re.search(r'rm\s+-[rf]{1,2}', command):
            risks.append("包含递归删除操作")
            risk_level = "high"
        
        # 检查管道到shell
        if '| sh' in command or '| bash' in command or '| zsh' in command:
            risks.append("包含管道执行shell命令")
            if risk_level == "low":
                risk_level = "medium"
        
        # 检查修改系统文件
        system_paths = ['/etc/', '/sys/', '/proc/', '/dev/', '/boot/']
        for path in system_paths:
            if path in command:
                risks.append(f"涉及系统目录: {path}")
                if risk_level == "low":
                    risk_level = "medium"
        
        # 检查通配符
        if re.search(r'\*|\?|\[|\]', command):
            if 'rm' in command or 'mv' in command:
                risks.append("使用通配符进行删除/移动操作")
                if risk_level == "low":
                    risk_level = "medium"
        
        return risk_level, risks
    
    def _execute_command(self, command: str) -> None:
        """
        执行命令
        
        Args:
            command: 要执行的命令
        """
        try:
            self.console.print("\n[yellow]正在执行命令...[/yellow]\n")
            
            # 使用shell=True以支持管道、重定向等
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 显示标准输出
            if result.stdout:
                self.console.print("[bold]标准输出:[/bold]")
                self.console.print(result.stdout)
            
            # 显示标准错误
            if result.stderr:
                self.console.print("[bold]标准错误:[/bold]")
                self.console.print(f"[red]{result.stderr}[/red]")
            
            # 显示返回码
            if result.returncode == 0:
                self.console.print(f"\n[green]✓ 命令执行成功（返回码: {result.returncode}）[/green]")
            else:
                self.console.print(f"\n[red]✗ 命令执行失败（返回码: {result.returncode}）[/red]")
                
        except subprocess.TimeoutExpired:
            self.console.print("[red]✗ 命令执行超时（30秒）[/red]")
        except Exception as e:
            self.console.print(f"[red]✗ 命令执行出错: {e}[/red]")
