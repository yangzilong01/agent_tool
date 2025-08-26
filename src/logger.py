"""
日志模块
提供统一的日志记录功能
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime


def setup_logger(name: str = None, level: str = 'INFO', config: Dict[str, Any] = None) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志器名称
        level: 日志级别
        config: 日志配置字典
    
    Returns:
        配置好的日志器
    """
    if name is None:
        name = 'agent_tool'
    
    logger = logging.getLogger(name)
    
    # 避免重复配置
    if logger.handlers:
        return logger
    
    # 设置日志级别
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # 默认配置
    default_config = {
        'file': 'logs/agent.log',
        'max_size': '10MB',
        'backup_count': 3,
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'date_format': '%Y-%m-%d %H:%M:%S'
    }
    
    if config:
        log_config = config.get('logging', {})
        default_config.update(log_config)
    
    # 创建格式器
    formatter = logging.Formatter(
        default_config['format'],
        datefmt=default_config['date_format']
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)  # 控制台只显示警告及以上级别
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    log_file = default_config['file']
    if not os.path.isabs(log_file):
        # 相对路径时，放在用户配置目录下
        home_dir = Path.home()
        config_dir = home_dir / '.agent_tool'
        config_dir.mkdir(exist_ok=True)
        log_file = config_dir / log_file
    
    # 确保日志目录存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 解析文件大小
    max_size = _parse_size(default_config['max_size'])
    backup_count = default_config.get('backup_count', 3)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def _parse_size(size_str: str) -> int:
    """解析文件大小字符串"""
    size_str = size_str.upper()
    
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        return int(size_str)


class CommandLogger:
    """命令执行日志记录器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = setup_logger('command_logger', config=config)
        self.config = config or {}
        
        # 命令历史文件
        self.history_file = self._get_history_file()
        
    def _get_history_file(self) -> Path:
        """获取命令历史文件路径"""
        home_dir = Path.home()
        config_dir = home_dir / '.agent_tool'
        config_dir.mkdir(exist_ok=True)
        return config_dir / 'command_history.jsonl'
    
    def log_command_generation(self, user_input: str, command_info: Dict[str, Any]):
        """记录命令生成"""
        self.logger.info(f"生成命令 - 用户输入: {user_input}")
        self.logger.info(f"生成结果: {command_info.get('command', '')}")
        self.logger.info(f"风险等级: {command_info.get('risk_level', '')}")
        
        # 保存到历史文件
        self._save_to_history({
            'timestamp': datetime.now().isoformat(),
            'type': 'command_generation',
            'user_input': user_input,
            'command_info': command_info
        })
    
    def log_command_execution(self, command: str, result, warnings: list = None):
        """记录命令执行"""
        self.logger.info(f"执行命令: {command}")
        self.logger.info(f"执行结果: {'成功' if result.success else '失败'}")
        self.logger.info(f"返回码: {result.return_code}")
        self.logger.info(f"执行时间: {result.execution_time:.2f}s")
        
        if not result.success:
            self.logger.error(f"错误输出: {result.stderr}")
        
        if warnings:
            for warning in warnings:
                self.logger.warning(f"命令警告: {warning}")
        
        # 保存到历史文件
        self._save_to_history({
            'timestamp': datetime.now().isoformat(),
            'type': 'command_execution',
            'command': command,
            'success': result.success,
            'return_code': result.return_code,
            'execution_time': result.execution_time,
            'stdout': result.stdout[:1000] if result.stdout else '',  # 限制长度
            'stderr': result.stderr[:1000] if result.stderr else '',
            'warnings': warnings or []
        })
    
    def log_security_violation(self, command: str, violations: list):
        """记录安全违规"""
        self.logger.warning(f"安全违规 - 命令: {command}")
        for violation in violations:
            self.logger.warning(f"违规详情: {violation}")
        
        # 保存到历史文件
        self._save_to_history({
            'timestamp': datetime.now().isoformat(),
            'type': 'security_violation',
            'command': command,
            'violations': violations
        })
    
    def log_user_action(self, action: str, details: Dict[str, Any] = None):
        """记录用户操作"""
        self.logger.info(f"用户操作: {action}")
        if details:
            self.logger.debug(f"操作详情: {details}")
        
        # 保存到历史文件
        self._save_to_history({
            'timestamp': datetime.now().isoformat(),
            'type': 'user_action',
            'action': action,
            'details': details or {}
        })
    
    def log_error(self, error: Exception, context: str = ''):
        """记录错误"""
        self.logger.error(f"系统错误{' - ' + context if context else ''}: {error}")
        self.logger.debug(f"错误详情", exc_info=True)
        
        # 保存到历史文件
        self._save_to_history({
            'timestamp': datetime.now().isoformat(),
            'type': 'error',
            'error': str(error),
            'context': context,
            'error_type': type(error).__name__
        })
    
    def _save_to_history(self, record: Dict[str, Any]):
        """保存记录到历史文件"""
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                json.dump(record, f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"保存历史记录失败: {e}")
    
    def get_command_history(self, limit: int = 100) -> list:
        """获取命令历史"""
        history = []
        
        if not self.history_file.exists():
            return history
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # 读取最后N行
            for line in lines[-limit:]:
                if line.strip():
                    try:
                        record = json.loads(line.strip())
                        history.append(record)
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            self.logger.error(f"读取命令历史失败: {e}")
        
        return history
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        history = self.get_command_history(1000)  # 获取最近1000条记录
        
        stats = {
            'total_commands': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'security_violations': 0,
            'most_used_commands': {},
            'risk_level_distribution': {},
            'average_execution_time': 0.0
        }
        
        execution_times = []
        
        for record in history:
            record_type = record.get('type', '')
            
            if record_type == 'command_execution':
                stats['total_commands'] += 1
                
                if record.get('success'):
                    stats['successful_commands'] += 1
                else:
                    stats['failed_commands'] += 1
                
                # 统计执行时间
                exec_time = record.get('execution_time', 0)
                if exec_time > 0:
                    execution_times.append(exec_time)
                
                # 统计常用命令
                command = record.get('command', '').split()[0]
                if command:
                    stats['most_used_commands'][command] = stats['most_used_commands'].get(command, 0) + 1
            
            elif record_type == 'command_generation':
                # 统计风险等级分布
                risk_level = record.get('command_info', {}).get('risk_level', '')
                if risk_level:
                    stats['risk_level_distribution'][risk_level] = stats['risk_level_distribution'].get(risk_level, 0) + 1
            
            elif record_type == 'security_violation':
                stats['security_violations'] += 1
        
        # 计算平均执行时间
        if execution_times:
            stats['average_execution_time'] = sum(execution_times) / len(execution_times)
        
        # 排序最常用的命令
        stats['most_used_commands'] = dict(sorted(
            stats['most_used_commands'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])  # 只保留前10个
        
        return stats
    
    def clean_old_logs(self, days: int = 30):
        """清理旧日志"""
        if not self.history_file.exists():
            return
        
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days)
            temp_file = self.history_file.with_suffix('.tmp')
            
            with open(self.history_file, 'r', encoding='utf-8') as input_file, \
                 open(temp_file, 'w', encoding='utf-8') as output_file:
                
                for line in input_file:
                    if line.strip():
                        try:
                            record = json.loads(line.strip())
                            record_date = datetime.fromisoformat(record.get('timestamp', ''))
                            
                            if record_date >= cutoff_date:
                                output_file.write(line)
                        except (json.JSONDecodeError, ValueError):
                            continue
            
            # 替换原文件
            temp_file.replace(self.history_file)
            self.logger.info(f"清理了{days}天前的日志记录")
            
        except Exception as e:
            self.logger.error(f"清理日志失败: {e}")
    
    def export_logs(self, output_file: str, format: str = 'json'):
        """导出日志"""
        history = self.get_command_history(10000)  # 导出最近10000条记录
        
        try:
            if format.lower() == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(history, f, ensure_ascii=False, indent=2)
            
            elif format.lower() == 'csv':
                import csv
                
                if not history:
                    return
                
                fieldnames = set()
                for record in history:
                    fieldnames.update(record.keys())
                
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=list(fieldnames))
                    writer.writeheader()
                    
                    for record in history:
                        # 扁平化嵌套字典
                        flattened = {}
                        for k, v in record.items():
                            if isinstance(v, dict):
                                for sub_k, sub_v in v.items():
                                    flattened[f"{k}_{sub_k}"] = sub_v
                            else:
                                flattened[k] = v
                        writer.writerow(flattened)
            
            self.logger.info(f"日志导出成功: {output_file}")
            
        except Exception as e:
            self.logger.error(f"导出日志失败: {e}")
            raise
