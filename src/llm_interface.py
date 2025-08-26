"""
大模型接口抽象层
支持多种大模型服务商的统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging
import json

logger = logging.getLogger(__name__)


class LLMInterface(ABC):
    """大模型接口抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = config.get('model', '')
        self.api_key = config.get('api_key', '')
        self.base_url = config.get('base_url', '')
        
    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """生成响应"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查模型是否可用"""
        pass


class OpenAIInterface(LLMInterface):
    """OpenAI接口实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url if self.base_url else None
            )
        except ImportError:
            raise ImportError("需要安装 openai 库: pip install openai")
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """使用OpenAI生成响应"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 1000)
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查OpenAI接口是否可用"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            logger.warning(f"OpenAI接口不可用: {e}")
            return False


class AnthropicInterface(LLMInterface):
    """Anthropic Claude接口实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("需要安装 anthropic 库: pip install anthropic")
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """使用Anthropic生成响应"""
        try:
            message_content = prompt
            if system_prompt:
                message_content = f"{system_prompt}\n\n{prompt}"
            
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.config.get('max_tokens', 1000),
                messages=[{"role": "user", "content": message_content}]
            )
            
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic API调用失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查Anthropic接口是否可用"""
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            logger.warning(f"Anthropic接口不可用: {e}")
            return False


class ZhipuAIInterface(LLMInterface):
    """智谱清言接口实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("需要安装 zhipuai 库: pip install zhipuai")
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """使用智谱清言生成响应"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 1000)
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"智谱清言 API调用失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查智谱清言接口是否可用"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            logger.warning(f"智谱清言接口不可用: {e}")
            return False


class LocalLLMInterface(LLMInterface):
    """本地大模型接口（支持Ollama等）"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.endpoint = config.get('endpoint', 'http://localhost:11434')
        
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """使用本地模型生成响应"""
        try:
            import requests
            
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            data = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.get('temperature', 0.3),
                    "num_predict": self.config.get('max_tokens', 1000)
                }
            }
            
            response = requests.post(
                f"{self.endpoint}/api/generate",
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()['response'].strip()
        except Exception as e:
            logger.error(f"本地模型API调用失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查本地模型接口是否可用"""
        try:
            import requests
            response = requests.get(f"{self.endpoint}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"本地模型接口不可用: {e}")
            return False


class LLMManager:
    """大模型管理器"""
    
    SUPPORTED_PROVIDERS = {
        'openai': OpenAIInterface,
        'anthropic': AnthropicInterface,
        'zhipuai': ZhipuAIInterface,
        'local': LocalLLMInterface
    }
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """初始化大模型接口"""
        provider = self.config.get('provider', '').lower()
        
        if provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"不支持的服务商: {provider}. 支持的服务商: {list(self.SUPPORTED_PROVIDERS.keys())}")
        
        interface_class = self.SUPPORTED_PROVIDERS[provider]
        self.llm = interface_class(self.config)
        
        logger.info(f"初始化{provider}接口，模型: {self.config.get('model')}")
    
    def generate_command(self, user_input: str) -> Dict[str, Any]:
        """根据用户输入生成命令"""
        system_prompt = """你是一个Linux/Unix系统的命令行专家。用户会用自然语言描述他们想要执行的操作，你需要将其转换为合适的命令。

请按照以下JSON格式返回结果：
{
    "command": "具体的shell命令",
    "description": "命令的作用说明",
    "risk_level": "low/medium/high",
    "explanation": "命令解释和注意事项"
}

规则：
1. 只生成Linux/Unix系统的命令
2. 避免生成危险的命令（如rm -rf /等）
3. 如果操作有风险，在risk_level中标明
4. 提供清晰的命令解释
5. 如果用户请求不明确，给出最常用的实现方式"""

        try:
            response = self.llm.generate_response(user_input, system_prompt)
            logger.debug(f"LLM原始响应: {response}")
            
            # 尝试解析JSON响应
            try:
                # 提取JSON部分（可能包含在代码块中）
                if '```json' in response:
                    start = response.find('```json') + 7
                    end = response.find('```', start)
                    json_str = response[start:end].strip()
                elif '{' in response and '}' in response:
                    start = response.find('{')
                    end = response.rfind('}') + 1
                    json_str = response[start:end]
                else:
                    json_str = response
                
                result = json.loads(json_str)
                
                # 验证必需字段
                required_fields = ['command', 'description', 'risk_level', 'explanation']
                for field in required_fields:
                    if field not in result:
                        result[field] = "未提供"
                
                return result
                
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回原始响应
                return {
                    "command": response,
                    "description": "AI生成的命令",
                    "risk_level": "unknown",
                    "explanation": "无法解析结构化响应"
                }
                
        except Exception as e:
            logger.error(f"生成命令失败: {e}")
            return {
                "command": "",
                "description": "命令生成失败",
                "risk_level": "high",
                "explanation": f"错误: {e}"
            }
    
    def is_available(self) -> bool:
        """检查模型是否可用"""
        return self.llm and self.llm.is_available()
    
    def get_model_info(self) -> Dict[str, str]:
        """获取模型信息"""
        return {
            "provider": self.config.get('provider', ''),
            "model": self.config.get('model', ''),
            "status": "可用" if self.is_available() else "不可用"
        }
