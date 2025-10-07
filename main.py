#!/usr/bin/env python3
"""
OpsPilot - 产品智能运维工具
"""
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from config_manager import ConfigManager
from llm_client import LLMClient
from command_generator import CommandGenerator
from system_analyzer import SystemAnalyzer
from jvm_analyzer import JVMAnalyzer
from web_api_analyzer import WebApiAnalyzer
from log_analyzer import LogAnalyzer


class OpsPilot:
    """OpsPilot主程序"""
    
    def __init__(self):
        """初始化OpsPilot"""
        self.console = Console()
        self.config_manager = None
        self.llm_client = None
        self.running = True
    
    def initialize(self) -> bool:
        """
        初始化系统
        
        Returns:
            是否初始化成功
        """
        # 显示欢迎信息
        self.console.print(Panel.fit(
            "[bold cyan]OpsPilot - 产品智能运维工具[/bold cyan]\n"
            "[white]基于LLM的智能运维助手[/white]",
            border_style="cyan"
        ))
        
        # 加载配置
        self.config_manager = ConfigManager()
        
        # 检查是否需要配置
        llm_mode = self.config_manager.get('llm.mode')
        if not llm_mode:
            self.console.print("\n[yellow]首次运行，需要配置LLM模型[/yellow]")
            self.config_manager.setup_interactive()
        else:
            # 验证配置
            if llm_mode == 'api':
                api_key = self.config_manager.get('llm.api.api_key')
                if not api_key:
                    self.console.print("\n[yellow]API Key未配置，请重新配置[/yellow]")
                    self.config_manager.setup_interactive()
        
        # 初始化LLM客户端
        try:
            self.llm_client = LLMClient(self.config_manager)
            self.console.print("\n[green]✓ 初始化成功！[/green]\n")
            return True
        except Exception as e:
            self.console.print(f"\n[red]✗ 初始化失败: {e}[/red]\n")
            return False
    
    def show_menu(self) -> None:
        """显示主菜单"""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("选项", style="cyan", width=8)
        table.add_column("功能", style="white")
        
        table.add_row("1", "Linux命令生成")
        table.add_row("2", "操作系统指标分析")
        table.add_row("3", "JVM情况分析")
        table.add_row("4", "Web接口性能分析")
        table.add_row("5", "SpringBoot异常日志分析")
        table.add_row("", "")
        table.add_row("6", "LLM配置管理")
        table.add_row("0", "退出程序")
        
        self.console.print("\n")
        self.console.print(Panel(table, title="[bold cyan]主菜单[/bold cyan]", border_style="cyan"))
    
    def run(self) -> None:
        """运行主程序"""
        if not self.initialize():
            return
        
        while self.running:
            try:
                self.show_menu()
                choice = Prompt.ask("\n请选择功能", choices=["0", "1", "2", "3", "4", "5", "6"], default="1")
                
                if choice == "0":
                    self.exit_program()
                elif choice == "1":
                    self.run_command_generator()
                elif choice == "2":
                    self.run_system_analyzer()
                elif choice == "3":
                    self.run_jvm_analyzer()
                elif choice == "4":
                    self.run_web_api_analyzer()
                elif choice == "5":
                    self.run_log_analyzer()
                elif choice == "6":
                    self.run_config_manager()
                    
            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]检测到中断信号[/yellow]")
                self.exit_program()
            except Exception as e:
                self.console.print(f"\n[red]发生错误: {e}[/red]")
                import traceback
                traceback.print_exc()
                input("\n按回车键继续...")
    
    def run_command_generator(self) -> None:
        """运行Linux命令生成功能"""
        generator = CommandGenerator(self.llm_client, self.config_manager)
        generator.run()
    
    def run_system_analyzer(self) -> None:
        """运行系统指标分析功能"""
        analyzer = SystemAnalyzer(self.llm_client)
        analyzer.run()
    
    def run_jvm_analyzer(self) -> None:
        """运行JVM分析功能"""
        analyzer = JVMAnalyzer(self.llm_client, self.config_manager)
        analyzer.run()
    
    def run_web_api_analyzer(self) -> None:
        """运行Web接口分析功能"""
        analyzer = WebApiAnalyzer(self.llm_client)
        analyzer.run()
    
    def run_log_analyzer(self) -> None:
        """运行日志分析功能"""
        analyzer = LogAnalyzer(self.llm_client)
        analyzer.run()
    
    def run_config_manager(self) -> None:
        """运行配置管理功能"""
        self.config_manager.setup_interactive()
        
        # 重新初始化LLM客户端
        try:
            self.llm_client = LLMClient(self.config_manager)
            self.console.print("[green]✓ LLM客户端已更新[/green]")
        except Exception as e:
            self.console.print(f"[red]✗ LLM客户端更新失败: {e}[/red]")
        
        input("\n按回车键返回主菜单...")
    
    def exit_program(self) -> None:
        """退出程序"""
        self.console.print("\n[cyan]感谢使用 OpsPilot！[/cyan]\n")
        self.running = False


def main():
    """主函数"""
    try:
        pilot = OpsPilot()
        pilot.run()
    except Exception as e:
        print(f"程序异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
