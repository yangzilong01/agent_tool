#!/usr/bin/env python3
"""
Linux/Unix Agent Tool
一个智能的命令行助手，将自然语言转换为Linux/Unix命令并执行
"""

import sys
import os
import argparse
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cli import AgentCLI
from config_manager import ConfigManager
from logger import setup_logger


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description='Linux/Unix Agent Tool - 智能命令行助手',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                    # 启动交互模式
  %(prog)s -c "列出当前目录的文件"   # 单次执行
  %(prog)s --config             # 显示配置
  %(prog)s --setup              # 初始化配置
        """
    )
    
    parser.add_argument('-c', '--command', 
                       help='执行单个命令（非交互模式）')
    parser.add_argument('--config', action='store_true',
                       help='显示当前配置')
    parser.add_argument('--setup', action='store_true',
                       help='初始化配置')
    parser.add_argument('--auto', action='store_true',
                       help='自动执行模式（跳过确认）')
    parser.add_argument('--debug', action='store_true',
                       help='启用调试模式')
    
    args = parser.parse_args()
    
    # 设置日志
    log_level = 'DEBUG' if args.debug else 'INFO'
    logger = setup_logger(level=log_level)
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    
    # 处理特殊命令
    if args.setup:
        config_manager.setup_config()
        return
    
    if args.config:
        config_manager.show_config()
        return
    
    # 检查配置是否存在
    if not config_manager.config_exists():
        print("❌ 配置文件不存在，请先运行 --setup 进行初始化")
        return
    
    # 启动CLI
    cli = AgentCLI(config_manager, auto_mode=args.auto)
    
    if args.command:
        # 单次执行模式
        cli.process_single_command(args.command)
    else:
        # 交互模式
        cli.run_interactive()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 程序异常退出: {e}")
        sys.exit(1)
