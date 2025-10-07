"""
LLM客户端模块
"""
import requests
from typing import List, Dict, Any, Optional
from openai import OpenAI


class LLMClient:
    """LLM客户端，支持Ollama和远程API"""
    
    def __init__(self, config_manager):
        """
        初始化LLM客户端
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config = config_manager
        self.mode = config_manager.get('llm.mode', 'ollama')
        
        if self.mode == 'ollama':
            self.base_url = config_manager.get('llm.ollama.base_url', 'http://localhost:11434')
            self.model = config_manager.get('llm.ollama.model', 'llama2')
            self.client = None
        else:
            self.base_url = config_manager.get('llm.api.base_url', 'https://api.openai.com/v1')
            self.api_key = config_manager.get('llm.api.api_key', '')
            self.model = config_manager.get('llm.api.model', 'gpt-3.5-turbo')
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Optional[str]:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            
        Returns:
            LLM响应文本，失败返回None
        """
        try:
            if self.mode == 'ollama':
                return self._chat_ollama(messages, temperature)
            else:
                return self._chat_api(messages, temperature)
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return None
    
    def _chat_ollama(self, messages: List[Dict[str, str]], temperature: float) -> Optional[str]:
        """
        使用Ollama进行聊天
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            
        Returns:
            响应文本
        """
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        return result.get('message', {}).get('content', '')
    
    def _chat_api(self, messages: List[Dict[str, str]], temperature: float) -> Optional[str]:
        """
        使用远程API进行聊天
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            
        Returns:
            响应文本
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    def generate_command(self, user_request: str) -> Optional[str]:
        """
        生成Linux命令
        
        Args:
            user_request: 用户需求描述
            
        Returns:
            生成的命令
        """
        system_prompt = """你是一个Linux命令生成助手。根据用户的需求，生成对应的Linux命令。
要求：
1. 只输出命令本身，不要有任何解释或额外文字
2. 如果需要多个命令，用 && 或 ; 连接
3. 命令要安全、准确、符合最佳实践
4. 优先使用常用命令和参数"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_request}
        ]
        
        return self.chat(messages, temperature=0.3)
    
    def analyze_system_metrics(self, metrics_data: Dict[str, Any]) -> Optional[str]:
        """
        分析系统指标
        
        Args:
            metrics_data: 系统指标数据
            
        Returns:
            分析结果
        """
        prompt = f"""作为系统运维专家，请分析以下系统指标数据，给出专业的评估和建议：

{metrics_data}

请从以下几个方面进行分析：
1. 当前系统状态评估（健康/警告/危险）
2. 潜在问题识别
3. 性能瓶颈分析
4. 优化建议"""

        messages = [
            {"role": "system", "content": "你是一个系统运维专家，擅长分析系统性能指标。"},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat(messages)
    
    def analyze_jvm(self, jvm_data: str) -> Optional[str]:
        """
        分析JVM数据
        
        Args:
            jvm_data: JVM数据
            
        Returns:
            分析结果
        """
        prompt = f"""作为Java性能调优专家，请分析以下JVM数据：

{jvm_data}

请提供：
1. GC性能评估（频率、时长、影响）
2. 内存使用分析
3. 潜在内存泄漏风险
4. JVM参数调优建议"""

        messages = [
            {"role": "system", "content": "你是一个Java性能调优专家。"},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat(messages)
    
    def analyze_web_api(self, api_data: str) -> Optional[str]:
        """
        分析Web API性能
        
        Args:
            api_data: API数据
            
        Returns:
            分析结果
        """
        prompt = f"""作为Web性能优化专家，请分析以下API接口数据：

{api_data}

请提供：
1. 性能瓶颈识别
2. 慢接口分析
3. 优化建议（包括代码层面和架构层面）
4. 监控告警建议"""

        messages = [
            {"role": "system", "content": "你是一个Web性能优化专家。"},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat(messages)
    
    def analyze_error_log(self, log_content: str) -> Optional[str]:
        """
        分析错误日志
        
        Args:
            log_content: 日志内容
            
        Returns:
            分析结果
        """
        prompt = f"""作为Java开发专家，请分析以下SpringBoot错误日志：

{log_content}

请提供：
1. 错误类型和根本原因
2. 受影响的功能模块
3. 可能的解决方案（按优先级排序）
4. 预防措施和最佳实践建议"""

        messages = [
            {"role": "system", "content": "你是一个经验丰富的Java开发专家。"},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat(messages)
