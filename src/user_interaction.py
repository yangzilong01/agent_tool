"""
用户交互模块
处理用户确认、输入验证和交互界面
"""

import sys
import re
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging

try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.text import Text
    from rich.syntax import Syntax
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

logger = logging.getLogger(__name__)


class UserChoice(Enum):
    """用户选择选项"""
    EXECUTE = "execute"
    MODIFY = "modify"
    CANCEL = "cancel"
    HELP = "help"
    EXPLAIN = "explain"


class UserInteractionManager:
    """用户交互管理器"""
    
    def __init__(self, config: Dict[str, Any], auto_mode: bool = False):
        self.config = config
        self.auto_mode = auto_mode
        self.console = Console() if RICH_AVAILABLE else None
        
    def display_command_info(self, command_info: Dict[str, Any]) -> None:
        """显示命令信息"""
        if self.console:
            self._display_command_rich(command_info)
        else:
            self._display_command_plain(command_info)
    
    def _display_command_rich(self, command_info: Dict[str, Any]) -> None:
        """使用Rich库显示命令信息"""
        # 风险等级颜色映射
        risk_colors = {
            "low": "green",
            "medium": "yellow", 
            "high": "red",
            "critical": "bright_red"
        }
        
        risk_level = command_info.get("risk_level", "unknown").lower()
        risk_color = risk_colors.get(risk_level, "white")
        
        # 创建信息面板
        table = Table(show_header=False, box=None, padding=0)
        table.add_column("Key", style="bold cyan", width=12)
        table.add_column("Value", style="white")
        
        table.add_row("命令:", command_info.get("command", ""))
        table.add_row("描述:", command_info.get("description", ""))
        table.add_row("风险等级:", Text(risk_level.upper(), style=risk_color))
        table.add_row("说明:", command_info.get("explanation", ""))
        
        panel = Panel(
            table,
            title="🤖 AI生成的命令",
            border_style="blue",
            expand=False
        )
        
        self.console.print(panel)
    
    def _display_command_plain(self, command_info: Dict[str, Any]) -> None:
        """纯文本显示命令信息"""
        print("\n" + "="*60)
        print("🤖 AI生成的命令")
        print("="*60)
        print(f"命令: {command_info.get('command', '')}")
        print(f"描述: {command_info.get('description', '')}")
        print(f"风险等级: {command_info.get('risk_level', '').upper()}")
        print(f"说明: {command_info.get('explanation', '')}")
        print("="*60)
    
    def get_user_confirmation(self, command_info: Dict[str, Any]) -> UserChoice:
        """获取用户确认"""
        if self.auto_mode:
            logger.info("自动模式，直接执行命令")
            return UserChoice.EXECUTE
        
        # 检查风险等级
        risk_level = command_info.get("risk_level", "").lower()
        if risk_level == "critical":
            self._show_critical_warning()
            return UserChoice.CANCEL
        
        return self._prompt_user_choice(command_info)
    
    def _show_critical_warning(self) -> None:
        """显示高风险警告"""
        if self.console:
            warning = Panel(
                "[bold red]⚠️  危险命令警告 ⚠️[/bold red]\n\n"
                "检测到潜在危险的命令，为了系统安全，此命令已被自动拒绝执行。\n"
                "如果您确实需要执行此类操作，请手动执行并承担相应风险。",
                border_style="red",
                title="安全警告"
            )
            self.console.print(warning)
        else:
            print("\n" + "="*60)
            print("⚠️  危险命令警告 ⚠️")
            print("="*60)
            print("检测到潜在危险的命令，为了系统安全，此命令已被自动拒绝执行。")
            print("如果您确实需要执行此类操作，请手动执行并承担相应风险。")
            print("="*60)
    
    def _prompt_user_choice(self, command_info: Dict[str, Any]) -> UserChoice:
        """提示用户选择"""
        choices = {
            'y': UserChoice.EXECUTE,
            'yes': UserChoice.EXECUTE,
            'n': UserChoice.CANCEL,
            'no': UserChoice.CANCEL,
            'm': UserChoice.MODIFY,
            'modify': UserChoice.MODIFY,
            'h': UserChoice.HELP,
            'help': UserChoice.HELP,
            'e': UserChoice.EXPLAIN,
            'explain': UserChoice.EXPLAIN
        }
        
        if self.console:
            self.console.print("\n[bold]选择操作:[/bold]")
            self.console.print("[green]y/yes[/green] - 执行命令")
            self.console.print("[yellow]m/modify[/yellow] - 修改命令")
            self.console.print("[blue]e/explain[/blue] - 解释命令")
            self.console.print("[cyan]h/help[/cyan] - 显示帮助")
            self.console.print("[red]n/no[/red] - 取消执行")
            
            choice = Prompt.ask("\n请选择", default="y").lower().strip()
        else:
            print("\n选择操作:")
            print("y/yes - 执行命令")
            print("m/modify - 修改命令") 
            print("e/explain - 解释命令")
            print("h/help - 显示帮助")
            print("n/no - 取消执行")
            
            choice = input("\n请选择 [y]: ").lower().strip() or "y"
        
        return choices.get(choice, UserChoice.CANCEL)
    
    def get_modified_command(self, original_command: str) -> Optional[str]:
        """获取用户修改的命令"""
        if self.console:
            self.console.print(f"\n[bold]当前命令:[/bold] {original_command}")
            modified = Prompt.ask("请输入修改后的命令", default=original_command)
        else:
            print(f"\n当前命令: {original_command}")
            modified = input("请输入修改后的命令: ") or original_command
        
        if modified.strip() != original_command.strip():
            return modified.strip()
        return None
    
    def show_command_explanation(self, command: str, processor) -> None:
        """显示命令解释"""
        try:
            help_text = processor.get_command_help(command)
            
            if self.console:
                syntax = Syntax(help_text, "text", theme="monokai", line_numbers=False)
                panel = Panel(
                    syntax,
                    title=f"命令帮助: {command.split()[0]}",
                    border_style="blue"
                )
                self.console.print(panel)
            else:
                print("\n" + "-"*60)
                print(f"命令帮助: {command.split()[0]}")
                print("-"*60)
                print(help_text)
                print("-"*60)
                
        except Exception as e:
            logger.error(f"显示命令解释失败: {e}")
            if self.console:
                self.console.print(f"[red]获取命令帮助失败: {e}[/red]")
            else:
                print(f"获取命令帮助失败: {e}")
    
    def display_execution_result(self, result, warnings: List[str] = None) -> None:
        """显示执行结果"""
        if warnings:
            self._display_warnings(warnings)
        
        if self.console:
            self._display_result_rich(result)
        else:
            self._display_result_plain(result)
    
    def _display_warnings(self, warnings: List[str]) -> None:
        """显示警告信息"""
        if not warnings:
            return
            
        if self.console:
            warning_text = "\n".join(f"• {w}" for w in warnings)
            panel = Panel(
                warning_text,
                title="⚠️  警告信息",
                border_style="yellow"
            )
            self.console.print(panel)
        else:
            print("\n⚠️  警告信息:")
            for warning in warnings:
                print(f"  • {warning}")
    
    def _display_result_rich(self, result) -> None:
        """使用Rich显示执行结果"""
        # 状态信息
        status_color = "green" if result.success else "red"
        status_text = "✅ 成功" if result.success else "❌ 失败"
        
        # 创建结果表格
        table = Table(show_header=False, box=None, padding=0)
        table.add_column("Key", style="bold cyan", width=12)
        table.add_column("Value", style="white")
        
        table.add_row("状态:", Text(status_text, style=status_color))
        table.add_row("返回码:", str(result.return_code))
        table.add_row("执行时间:", f"{result.execution_time:.2f}s")
        
        panel = Panel(
            table,
            title="📋 执行结果",
            border_style=status_color
        )
        self.console.print(panel)
        
        # 显示输出
        if result.stdout:
            stdout_panel = Panel(
                result.stdout,
                title="📤 标准输出",
                border_style="green"
            )
            self.console.print(stdout_panel)
        
        if result.stderr:
            stderr_panel = Panel(
                result.stderr,
                title="📤 错误输出", 
                border_style="red"
            )
            self.console.print(stderr_panel)
    
    def _display_result_plain(self, result) -> None:
        """纯文本显示执行结果"""
        status_text = "✅ 成功" if result.success else "❌ 失败"
        
        print("\n" + "="*60)
        print("📋 执行结果")
        print("="*60)
        print(f"状态: {status_text}")
        print(f"返回码: {result.return_code}")
        print(f"执行时间: {result.execution_time:.2f}s")
        
        if result.stdout:
            print("\n📤 标准输出:")
            print("-"*40)
            print(result.stdout)
            print("-"*40)
        
        if result.stderr:
            print("\n📤 错误输出:")
            print("-"*40)
            print(result.stderr)
            print("-"*40)
        
        print("="*60)
    
    def show_welcome_message(self) -> None:
        """显示欢迎信息"""
        if self.console:
            welcome_text = """
[bold blue]🤖 Linux/Unix Agent Tool[/bold blue]

智能命令行助手，将自然语言转换为Linux/Unix命令并执行。

[bold]使用方法:[/bold]
• 直接描述您想要执行的操作
• 输入 [cyan]help[/cyan] 查看帮助信息
• 输入 [cyan]exit[/cyan] 或 [cyan]quit[/cyan] 退出程序

[yellow]⚠️  请注意系统安全，谨慎执行命令[/yellow]
            """
            
            panel = Panel(
                welcome_text.strip(),
                border_style="blue",
                padding=(1, 2)
            )
            self.console.print(panel)
        else:
            print("="*60)
            print("🤖 Linux/Unix Agent Tool")
            print("="*60)
            print("智能命令行助手，将自然语言转换为Linux/Unix命令并执行。")
            print()
            print("使用方法:")
            print("• 直接描述您想要执行的操作")
            print("• 输入 help 查看帮助信息")
            print("• 输入 exit 或 quit 退出程序")
            print()
            print("⚠️  请注意系统安全，谨慎执行命令")
            print("="*60)
    
    def show_help_message(self) -> None:
        """显示帮助信息"""
        help_text = """
[bold]🔧 命令说明:[/bold]

[cyan]基本操作:[/cyan]
• 列出文件 / 显示当前目录内容
• 查找文件 / 搜索包含特定内容的文件
• 创建目录 / 删除文件
• 查看文件内容 / 编辑文件
• 复制文件 / 移动文件

[cyan]系统信息:[/cyan]
• 查看系统信息 / 显示磁盘使用情况
• 查看内存使用 / 显示进程信息
• 查看网络连接 / 检查端口状态

[cyan]软件包管理:[/cyan]
• 安装软件包 / 更新系统
• 搜索软件包 / 卸载程序

[yellow]⚠️  安全提示:[/yellow]
• 高风险命令会被自动拦截
• 建议在测试环境中试用
• 重要操作前请备份数据
        """
        
        if self.console:
            panel = Panel(
                help_text.strip(),
                title="📚 帮助信息",
                border_style="blue"
            )
            self.console.print(panel)
        else:
            print("\n" + "="*60)
            print("📚 帮助信息")
            print("="*60)
            print(help_text.replace("[bold]", "").replace("[/bold]", "")
                           .replace("[cyan]", "").replace("[/cyan]", "")
                           .replace("[yellow]", "").replace("[/yellow]", ""))
            print("="*60)
    
    def get_user_input(self, prompt_text: str = "请描述您要执行的操作") -> str:
        """获取用户输入"""
        if self.console:
            return Prompt.ask(f"[bold green]🔤[/bold green] {prompt_text}")
        else:
            return input(f"🔤 {prompt_text}: ")
    
    def show_error(self, error_msg: str) -> None:
        """显示错误信息"""
        if self.console:
            self.console.print(f"[bold red]❌ 错误:[/bold red] {error_msg}")
        else:
            print(f"❌ 错误: {error_msg}")
    
    def show_info(self, info_msg: str) -> None:
        """显示信息"""
        if self.console:
            self.console.print(f"[bold blue]ℹ️ [/bold blue] {info_msg}")
        else:
            print(f"ℹ️  {info_msg}")
