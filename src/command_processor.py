"""
命令处理器模块
负责命令解析、安全检查、执行和结果处理
"""

import re
import subprocess
import shlex
import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """命令风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CommandResult:
    """命令执行结果"""
    success: bool
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    command: str


class SecurityChecker:
    """安全检查器"""
    
    # 危险命令模式
    DANGEROUS_PATTERNS = [
        r'rm\s+-rf\s*/',           # rm -rf /
        r'rm\s+-rf\s*\*',          # rm -rf *
        r'dd\s+if=.*of=/dev/',     # dd写入设备
        r'mkfs\.',                 # 格式化文件系统
        r'fdisk',                  # 磁盘分区
        r'parted',                 # 磁盘分区
        r'wipefs',                 # 擦除文件系统
        r'shred',                  # 安全删除
        r'>/dev/sda',              # 写入硬盘
        r'chmod\s+777\s+/',        # 根目录权限
        r'chown\s+.*:.*\s+/',      # 根目录所有者
        r'systemctl\s+stop',       # 停止系统服务
        r'systemctl\s+disable',    # 禁用系统服务
        r'service\s+.*\s+stop',    # 停止服务
        r'killall\s+-9',           # 强制杀死所有进程
        r'pkill\s+-9',             # 强制杀死进程
        r':()\{\s*:\|\:\&\s*\};:', # Fork bomb
        r'curl.*\|\s*sh',          # 下载并执行
        r'wget.*\|\s*sh',          # 下载并执行
        r'eval\s*\$\(',            # 动态执行
    ]
    
    # 需要sudo的命令
    SUDO_COMMANDS = [
        'apt', 'yum', 'dnf', 'pacman', 'zypper',
        'systemctl', 'service', 'mount', 'umount',
        'fdisk', 'parted', 'mkfs', 'fsck',
        'iptables', 'ufw', 'firewall-cmd',
        'docker', 'podman'  # 通常需要特殊权限
    ]
    
    # 文件操作命令
    FILE_COMMANDS = [
        'rm', 'cp', 'mv', 'chmod', 'chown', 'ln',
        'touch', 'mkdir', 'rmdir'
    ]
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.strict_mode = config.get('security', {}).get('strict_mode', True)
        self.allow_sudo = config.get('security', {}).get('allow_sudo', False)
        self.allowed_dirs = config.get('security', {}).get('allowed_dirs', [])
        
    def check_command_safety(self, command: str) -> Tuple[RiskLevel, List[str]]:
        """检查命令安全性"""
        warnings = []
        risk_level = RiskLevel.LOW
        
        # 检查危险模式
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                warnings.append(f"发现危险操作模式: {pattern}")
                risk_level = RiskLevel.CRITICAL
        
        # 检查sudo命令
        if any(cmd in command for cmd in self.SUDO_COMMANDS):
            if not self.allow_sudo:
                warnings.append("命令需要管理员权限，但未允许sudo操作")
                risk_level = max(risk_level, RiskLevel.HIGH)
            else:
                warnings.append("命令需要管理员权限")
                risk_level = max(risk_level, RiskLevel.MEDIUM)
        
        # 检查文件操作
        if any(cmd in command for cmd in self.FILE_COMMANDS):
            # 检查是否操作重要目录
            important_dirs = ['/bin', '/sbin', '/usr', '/etc', '/boot', '/lib', '/var']
            for dir_path in important_dirs:
                if dir_path in command:
                    warnings.append(f"操作系统重要目录: {dir_path}")
                    risk_level = max(risk_level, RiskLevel.HIGH)
                    break
            
            # 检查是否在允许的目录内
            if self.allowed_dirs:
                command_safe = False
                for allowed_dir in self.allowed_dirs:
                    if allowed_dir in command:
                        command_safe = True
                        break
                
                if not command_safe:
                    warnings.append("文件操作不在允许的目录范围内")
                    risk_level = max(risk_level, RiskLevel.MEDIUM)
        
        # 检查网络操作
        network_commands = ['curl', 'wget', 'nc', 'netcat', 'ssh', 'scp', 'rsync']
        if any(cmd in command for cmd in network_commands):
            warnings.append("包含网络操作")
            risk_level = max(risk_level, RiskLevel.MEDIUM)
        
        # 检查管道和重定向
        if '|' in command or '>' in command or '>>' in command:
            warnings.append("包含管道或重定向操作")
            risk_level = max(risk_level, RiskLevel.MEDIUM)
        
        return risk_level, warnings
    
    def is_command_allowed(self, command: str) -> bool:
        """检查命令是否被允许执行"""
        risk_level, warnings = self.check_command_safety(command)
        
        if risk_level == RiskLevel.CRITICAL:
            return False
        
        if self.strict_mode and risk_level == RiskLevel.HIGH:
            return False
        
        return True


class CommandProcessor:
    """命令处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.security_checker = SecurityChecker(config)
        self.execution_timeout = config.get('execution', {}).get('timeout', 30)
        self.working_dir = config.get('execution', {}).get('working_dir', os.getcwd())
        
    def validate_command(self, command: str) -> Tuple[bool, List[str]]:
        """验证命令"""
        warnings = []
        
        if not command.strip():
            warnings.append("命令为空")
            return False, warnings
        
        # 基本语法检查
        try:
            shlex.split(command)
        except ValueError as e:
            warnings.append(f"命令语法错误: {e}")
            return False, warnings
        
        # 安全检查
        risk_level, security_warnings = self.security_checker.check_command_safety(command)
        warnings.extend(security_warnings)
        
        # 检查是否允许执行
        if not self.security_checker.is_command_allowed(command):
            warnings.append("命令被安全策略拒绝")
            return False, warnings
        
        return True, warnings
    
    def execute_command(self, command: str, dry_run: bool = False) -> CommandResult:
        """执行命令"""
        import time
        
        start_time = time.time()
        
        if dry_run:
            logger.info(f"干运行模式，不实际执行命令: {command}")
            return CommandResult(
                success=True,
                return_code=0,
                stdout="[DRY RUN] 命令未实际执行",
                stderr="",
                execution_time=0.0,
                command=command
            )
        
        try:
            logger.info(f"执行命令: {command}")
            
            # 使用subprocess执行命令
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.working_dir
            )
            
            stdout, stderr = process.communicate(timeout=self.execution_timeout)
            execution_time = time.time() - start_time
            
            result = CommandResult(
                success=process.returncode == 0,
                return_code=process.returncode,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                command=command
            )
            
            logger.info(f"命令执行完成，返回码: {process.returncode}")
            if not result.success:
                logger.warning(f"命令执行失败: {stderr}")
            
            return result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.error(f"命令执行超时 ({self.execution_timeout}s): {command}")
            return CommandResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr=f"命令执行超时 ({self.execution_timeout}s)",
                execution_time=execution_time,
                command=command
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"命令执行异常: {e}")
            return CommandResult(
                success=False,
                return_code=-2,
                stdout="",
                stderr=f"执行异常: {e}",
                execution_time=execution_time,
                command=command
            )
    
    def format_output(self, result: CommandResult) -> str:
        """格式化输出结果"""
        lines = []
        
        # 命令信息
        lines.append(f"命令: {result.command}")
        lines.append(f"返回码: {result.return_code}")
        lines.append(f"执行时间: {result.execution_time:.2f}s")
        lines.append("-" * 50)
        
        # 标准输出
        if result.stdout:
            lines.append("标准输出:")
            lines.append(result.stdout)
        
        # 标准错误
        if result.stderr:
            lines.append("错误输出:")
            lines.append(result.stderr)
        
        return "\n".join(lines)
    
    def get_command_help(self, command: str) -> str:
        """获取命令帮助信息"""
        try:
            # 尝试获取命令的帮助信息
            base_command = command.split()[0]
            help_commands = [
                f"{base_command} --help",
                f"man {base_command}",
                f"help {base_command}"
            ]
            
            for help_cmd in help_commands:
                try:
                    result = subprocess.run(
                        help_cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and result.stdout:
                        return result.stdout[:1000]  # 限制输出长度
                except:
                    continue
            
            return f"无法获取 {base_command} 的帮助信息"
            
        except Exception as e:
            return f"获取帮助信息失败: {e}"
