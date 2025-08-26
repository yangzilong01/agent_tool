"""
Linux/Unix Agent Tool
智能命令行助手

该包提供了将自然语言转换为Linux/Unix命令并执行的功能，
支持多种大模型，具备完善的安全检查和日志记录功能。
"""

__version__ = "1.0.0"
__author__ = "Agent Tool Team"
__description__ = "智能Linux/Unix命令行助手"

from .config_manager import ConfigManager
from .llm_interface import LLMManager
from .command_processor import CommandProcessor
from .user_interaction import UserInteractionManager
from .cli import AgentCLI
from .logger import setup_logger, CommandLogger

__all__ = [
    'ConfigManager',
    'LLMManager', 
    'CommandProcessor',
    'UserInteractionManager',
    'AgentCLI',
    'setup_logger',
    'CommandLogger'
]
