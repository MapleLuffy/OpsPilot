"""
配置管理模块
"""
import os
import yaml
from typing import Dict, Any


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        if not os.path.exists(self.config_path):
            return self._create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"配置文件加载失败: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        创建默认配置
        
        Returns:
            默认配置字典
        """
        default_config = {
            'llm': {
                'mode': 'ollama',
                'ollama': {
                    'base_url': 'http://localhost:11434',
                    'model': 'llama2'
                },
                'api': {
                    'base_url': 'https://api.openai.com/v1',
                    'api_key': '',
                    'model': 'gpt-3.5-turbo'
                }
            },
            'jvm': {
                'large_object_threshold': 10
            },
            'command_check': {
                'dangerous_commands': [
                    'rm -rf',
                    'mkfs',
                    'dd if=',
                    '> /dev/',
                    'chmod -R 777',
                    'kill -9 1',
                    'reboot',
                    'shutdown',
                    'halt',
                    'poweroff'
                ]
            }
        }
        return default_config
    
    def save_config(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            是否保存成功
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
            return True
        except Exception as e:
            print(f"配置文件保存失败: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 配置键路径，使用.分隔，如 'llm.mode'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key_path: 配置键路径，使用.分隔
            value: 配置值
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def setup_interactive(self) -> None:
        """交互式配置向导"""
        from rich.console import Console
        from rich.prompt import Prompt, Confirm
        
        console = Console()
        
        console.print("\n[bold cyan]OpsPilot 配置向导[/bold cyan]\n")
        
        # LLM模式选择
        console.print("[yellow]请选择LLM模式:[/yellow]")
        console.print("1. Ollama (本地模型)")
        console.print("2. API (远程API，如OpenAI)")
        
        mode_choice = Prompt.ask("请输入选项", choices=["1", "2"], default="1")
        
        if mode_choice == "1":
            self.set('llm.mode', 'ollama')
            
            base_url = Prompt.ask(
                "Ollama服务地址",
                default=self.get('llm.ollama.base_url', 'http://localhost:11434')
            )
            self.set('llm.ollama.base_url', base_url)
            
            model = Prompt.ask(
                "模型名称",
                default=self.get('llm.ollama.model', 'llama2')
            )
            self.set('llm.ollama.model', model)
            
        else:
            self.set('llm.mode', 'api')
            
            base_url = Prompt.ask(
                "API服务地址",
                default=self.get('llm.api.base_url', 'https://api.openai.com/v1')
            )
            self.set('llm.api.base_url', base_url)
            
            api_key = Prompt.ask(
                "API Key",
                password=True
            )
            self.set('llm.api.api_key', api_key)
            
            model = Prompt.ask(
                "模型名称",
                default=self.get('llm.api.model', 'gpt-3.5-turbo')
            )
            self.set('llm.api.model', model)
        
        # 保存配置
        if self.save_config():
            console.print("\n[green]✓ 配置保存成功！[/green]\n")
        else:
            console.print("\n[red]✗ 配置保存失败！[/red]\n")
