"""
命令行界面模块
提供交互式和非交互式的用户界面
"""

import sys
import logging
from typing import Dict, Any, Optional
import signal

from llm_interface import LLMManager
from command_processor import CommandProcessor
from user_interaction import UserInteractionManager, UserChoice
from config_manager import ConfigManager

logger = logging.getLogger(__name__)


class AgentCLI:
    """Agent命令行界面"""
    
    def __init__(self, config_manager: ConfigManager, auto_mode: bool = False):
        """初始化CLI"""
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.auto_mode = auto_mode
        
        # 初始化组件
        self.llm_manager = None
        self.command_processor = None
        self.ui_manager = UserInteractionManager(self.config, auto_mode)
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # 初始化组件
        self._initialize_components()
    
    def _signal_handler(self, signum, frame):
        """处理中断信号"""
        print("\n\n👋 程序被中断，正在退出...")
        sys.exit(0)
    
    def _initialize_components(self):
        """初始化各个组件"""
        try:
            # 验证配置
            config_errors = self.config_manager.validate_config()
            if config_errors:
                logger.error("配置验证失败:")
                for error in config_errors:
                    logger.error(f"  - {error}")
                    self.ui_manager.show_error(f"配置错误: {error}")
                return False
            
            # 初始化大模型管理器
            llm_config = self.config.get('llm', {})
            self.llm_manager = LLMManager(llm_config)
            
            # 初始化命令处理器
            self.command_processor = CommandProcessor(self.config)
            
            logger.info("所有组件初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            self.ui_manager.show_error(f"初始化失败: {e}")
            return False
    
    def run_interactive(self):
        """运行交互式模式"""
        if not self._initialize_components():
            return
        
        # 显示欢迎信息
        self.ui_manager.show_welcome_message()
        
        # 检查模型可用性
        if not self.llm_manager.is_available():
            self.ui_manager.show_error("大模型不可用，请检查配置")
            return
        
        # 主循环
        while True:
            try:
                # 获取用户输入
                user_input = self.ui_manager.get_user_input().strip()
                
                if not user_input:
                    continue
                
                # 处理特殊命令
                if self._handle_special_commands(user_input):
                    continue
                
                # 处理普通命令
                self._process_user_command(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                logger.error(f"处理命令时出错: {e}")
                self.ui_manager.show_error(f"处理命令时出错: {e}")
    
    def process_single_command(self, user_input: str):
        """处理单个命令（非交互模式）"""
        if not self._initialize_components():
            return
        
        if not self.llm_manager.is_available():
            self.ui_manager.show_error("大模型不可用，请检查配置")
            return
        
        self._process_user_command(user_input)
    
    def _handle_special_commands(self, user_input: str) -> bool:
        """处理特殊命令"""
        user_input_lower = user_input.lower()
        
        # 退出命令
        if user_input_lower in ['exit', 'quit', 'q']:
            print("👋 再见！")
            sys.exit(0)
        
        # 帮助命令
        elif user_input_lower in ['help', 'h', '?']:
            self.ui_manager.show_help_message()
            return True
        
        # 配置命令
        elif user_input_lower.startswith('config'):
            self._handle_config_command(user_input_lower)
            return True
        
        # 状态命令
        elif user_input_lower in ['status', 'info']:
            self._show_status_info()
            return True
        
        # 模型信息
        elif user_input_lower in ['model', 'llm']:
            self._show_model_info()
            return True
        
        return False
    
    def _handle_config_command(self, command: str):
        """处理配置相关命令"""
        if command == 'config show':
            self.config_manager.show_config()
        elif command == 'config setup':
            self.config_manager.setup_config()
            # 重新加载配置
            self.config = self.config_manager.get_config()
            self._initialize_components()
        else:
            self.ui_manager.show_info("配置命令:")
            self.ui_manager.show_info("  config show  - 显示当前配置")
            self.ui_manager.show_info("  config setup - 重新配置")
    
    def _show_status_info(self):
        """显示状态信息"""
        status_info = []
        
        # 系统状态
        status_info.append("📊 系统状态:")
        status_info.append(f"  • 配置文件: {'✅' if self.config_manager.config_exists() else '❌'}")
        status_info.append(f"  • 大模型: {'✅ 可用' if self.llm_manager and self.llm_manager.is_available() else '❌ 不可用'}")
        status_info.append(f"  • 命令处理器: {'✅ 就绪' if self.command_processor else '❌ 未就绪'}")
        
        # 配置信息
        llm_config = self.config.get('llm', {})
        security_config = self.config.get('security', {})
        
        status_info.append("\n⚙️ 当前设置:")
        status_info.append(f"  • 模型服务商: {llm_config.get('provider', '未设置')}")
        status_info.append(f"  • 模型: {llm_config.get('model', '未设置')}")
        status_info.append(f"  • 严格模式: {'启用' if security_config.get('strict_mode') else '禁用'}")
        status_info.append(f"  • 自动模式: {'启用' if self.auto_mode else '禁用'}")
        
        for line in status_info:
            print(line)
    
    def _show_model_info(self):
        """显示模型信息"""
        if self.llm_manager:
            model_info = self.llm_manager.get_model_info()
            
            info_lines = [
                "🤖 大模型信息:",
                f"  • 服务商: {model_info.get('provider', '未知')}",
                f"  • 模型: {model_info.get('model', '未知')}",
                f"  • 状态: {model_info.get('status', '未知')}"
            ]
            
            for line in info_lines:
                print(line)
        else:
            self.ui_manager.show_error("大模型管理器未初始化")
    
    def _process_user_command(self, user_input: str):
        """处理用户命令"""
        try:
            # 生成命令
            self.ui_manager.show_info("正在生成命令...")
            
            command_info = self.llm_manager.generate_command(user_input)
            
            if not command_info.get('command'):
                self.ui_manager.show_error("无法生成有效命令")
                return
            
            # 显示生成的命令信息
            self.ui_manager.display_command_info(command_info)
            
            # 验证命令
            command = command_info['command']
            is_valid, warnings = self.command_processor.validate_command(command)
            
            if not is_valid:
                self.ui_manager.show_error("命令验证失败")
                if warnings:
                    for warning in warnings:
                        self.ui_manager.show_error(f"  • {warning}")
                return
            
            # 处理用户选择循环
            while True:
                user_choice = self.ui_manager.get_user_confirmation(command_info)
                
                if user_choice == UserChoice.EXECUTE:
                    self._execute_command(command, warnings)
                    break
                    
                elif user_choice == UserChoice.MODIFY:
                    modified_command = self.ui_manager.get_modified_command(command)
                    if modified_command:
                        # 重新验证修改后的命令
                        is_valid, new_warnings = self.command_processor.validate_command(modified_command)
                        if is_valid:
                            command = modified_command
                            warnings = new_warnings
                            command_info['command'] = command
                            self.ui_manager.display_command_info(command_info)
                        else:
                            self.ui_manager.show_error("修改后的命令无效")
                            if new_warnings:
                                for warning in new_warnings:
                                    self.ui_manager.show_error(f"  • {warning}")
                    
                elif user_choice == UserChoice.EXPLAIN:
                    self.ui_manager.show_command_explanation(command, self.command_processor)
                    
                elif user_choice == UserChoice.HELP:
                    self.ui_manager.show_help_message()
                    
                elif user_choice == UserChoice.CANCEL:
                    self.ui_manager.show_info("命令已取消")
                    break
                
        except Exception as e:
            logger.error(f"处理用户命令失败: {e}")
            self.ui_manager.show_error(f"处理命令失败: {e}")
    
    def _execute_command(self, command: str, warnings: list = None):
        """执行命令"""
        try:
            # 检查是否启用干运行模式
            dry_run = self.config.get('execution', {}).get('dry_run_default', False)
            
            # 执行命令
            self.ui_manager.show_info(f"{'[干运行] ' if dry_run else ''}正在执行命令...")
            
            result = self.command_processor.execute_command(command, dry_run=dry_run)
            
            # 显示执行结果
            self.ui_manager.display_execution_result(result, warnings)
            
            # 记录执行日志
            if result.success:
                logger.info(f"命令执行成功: {command}")
            else:
                logger.warning(f"命令执行失败: {command}, 返回码: {result.return_code}")
                
        except Exception as e:
            logger.error(f"执行命令异常: {e}")
            self.ui_manager.show_error(f"执行命令异常: {e}")
    
    def get_version_info(self) -> Dict[str, str]:
        """获取版本信息"""
        return {
            "version": "1.0.0",
            "name": "Linux/Unix Agent Tool",
            "description": "智能命令行助手"
        }


def main():
    """CLI入口函数（用于测试）"""
    from config_manager import ConfigManager
    
    config_manager = ConfigManager()
    
    if not config_manager.config_exists():
        print("配置文件不存在，请运行 --setup 进行初始化")
        return
    
    cli = AgentCLI(config_manager)
    cli.run_interactive()


if __name__ == '__main__':
    main()
