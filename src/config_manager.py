"""
配置管理模块
处理配置文件的读取、写入、验证和管理
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
from getpass import getpass

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        "llm": {
            "provider": "openai",  # openai, anthropic, zhipuai, local
            "model": "gpt-3.5-turbo",
            "api_key": "",
            "base_url": "",
            "temperature": 0.3,
            "max_tokens": 1000
        },
        "security": {
            "strict_mode": True,
            "allow_sudo": False,
            "allowed_dirs": [],
            "dangerous_commands_block": True
        },
        "execution": {
            "timeout": 30,
            "working_dir": "",
            "dry_run_default": False,
            "auto_confirm": False
        },
        "logging": {
            "level": "INFO",
            "file": "logs/agent.log",
            "max_size": "10MB",
            "backup_count": 3
        },
        "ui": {
            "use_rich": True,
            "show_warnings": True,
            "confirm_high_risk": True
        }
    }
    
    # 预设配置模板
    CONFIG_TEMPLATES = {
        "safe": {
            "security": {
                "strict_mode": True,
                "allow_sudo": False,
                "dangerous_commands_block": True
            },
            "execution": {
                "dry_run_default": True,
                "auto_confirm": False
            }
        },
        "development": {
            "security": {
                "strict_mode": False,
                "allow_sudo": True,
                "dangerous_commands_block": False
            },
            "execution": {
                "dry_run_default": False,
                "auto_confirm": False
            }
        },
        "auto": {
            "execution": {
                "auto_confirm": True,
                "dry_run_default": False
            },
            "ui": {
                "confirm_high_risk": False
            }
        }
    }
    
    def __init__(self, config_dir: str = None):
        """初始化配置管理器"""
        if config_dir is None:
            config_dir = os.path.join(Path.home(), '.agent_tool')
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / 'config.yaml'
        self.env_file = self.config_dir / '.env'
        
        self.config = {}
        self._ensure_config_dir()
        
        if self.config_exists():
            self.load_config()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建日志目录
        logs_dir = self.config_dir / 'logs'
        logs_dir.mkdir(exist_ok=True)
    
    def config_exists(self) -> bool:
        """检查配置文件是否存在"""
        return self.config_file.exists()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                
                # 合并默认配置
                self.config = self._deep_merge(self.DEFAULT_CONFIG.copy(), self.config)
                
                logger.info("配置文件加载成功")
            else:
                self.config = self.DEFAULT_CONFIG.copy()
                logger.info("使用默认配置")
            
            return self.config
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self.config = self.DEFAULT_CONFIG.copy()
            return self.config
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info("配置文件保存成功")
            return True
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            return False
    
    def setup_config(self):
        """交互式配置设置"""
        print("🔧 Agent Tool 配置向导")
        print("=" * 50)
        
        # 选择配置模板
        template = self._select_template()
        if template:
            self.config = self._deep_merge(self.DEFAULT_CONFIG.copy(), template)
        else:
            self.config = self.DEFAULT_CONFIG.copy()
        
        # 配置大模型
        self._setup_llm_config()
        
        # 配置安全选项
        self._setup_security_config()
        
        # 配置执行选项
        self._setup_execution_config()
        
        # 保存配置
        if self.save_config():
            print("\n✅ 配置保存成功！")
            print(f"配置文件位置: {self.config_file}")
        else:
            print("\n❌ 配置保存失败！")
    
    def _select_template(self) -> Optional[Dict[str, Any]]:
        """选择配置模板"""
        print("\n请选择配置模板:")
        print("1. 安全模式 (推荐新手)")
        print("2. 开发模式 (适合开发者)")
        print("3. 自动模式 (自动执行)")
        print("4. 自定义配置")
        
        while True:
            choice = input("\n请选择 [1]: ").strip() or "1"
            
            if choice == "1":
                return self.CONFIG_TEMPLATES["safe"]
            elif choice == "2":
                return self.CONFIG_TEMPLATES["development"]
            elif choice == "3":
                return self.CONFIG_TEMPLATES["auto"]
            elif choice == "4":
                return None
            else:
                print("无效选择，请重新输入")
    
    def _setup_llm_config(self):
        """配置大模型"""
        print("\n🤖 大模型配置")
        print("-" * 30)
        
        # 选择服务商
        providers = {
            "1": ("openai", "OpenAI (GPT-3.5/GPT-4)"),
            "2": ("anthropic", "Anthropic (Claude)"),
            "3": ("zhipuai", "智谱清言 (GLM-4)"),
            "4": ("local", "本地模型 (Ollama等)")
        }
        
        print("请选择大模型服务商:")
        for key, (_, name) in providers.items():
            print(f"{key}. {name}")
        
        while True:
            choice = input(f"\n请选择 [{self.config['llm']['provider']}]: ").strip()
            if not choice:
                break
            if choice in providers:
                self.config['llm']['provider'] = providers[choice][0]
                break
            print("无效选择，请重新输入")
        
        # 配置模型
        provider = self.config['llm']['provider']
        
        if provider == "openai":
            default_model = "gpt-3.5-turbo"
            print("\n常用OpenAI模型: gpt-3.5-turbo, gpt-4, gpt-4-turbo")
        elif provider == "anthropic":
            default_model = "claude-3-sonnet-20240229"
            print("\n常用Claude模型: claude-3-sonnet-20240229, claude-3-haiku-20240307")
        elif provider == "zhipuai":
            default_model = "glm-4"
            print("\n常用智谱清言模型: glm-4, glm-4-turbo, glm-3-turbo")
        elif provider == "local":
            default_model = "llama2"
            print("\n本地模型示例: llama2, codellama, mistral")
        
        model = input(f"模型名称 [{default_model}]: ").strip() or default_model
        self.config['llm']['model'] = model
        
        # API Key
        if provider in ["openai", "anthropic", "zhipuai"]:
            current_key = self.config['llm'].get('api_key', '')
            masked_key = '*' * len(current_key) if current_key else '未设置'
            
            print(f"\n当前API Key: {masked_key}")
            new_key = getpass("请输入API Key (留空保持不变): ")
            if new_key:
                self.config['llm']['api_key'] = new_key
        
        # Base URL (可选)
        if provider == "openai":
            base_url = input("Base URL (可选，支持代理): ").strip()
            if base_url:
                self.config['llm']['base_url'] = base_url
        elif provider == "zhipuai":
            default_base_url = "https://open.bigmodel.cn/api/paas/v4/"
            base_url = input(f"API端点 [{default_base_url}]: ").strip() or default_base_url
            self.config['llm']['base_url'] = base_url
        elif provider == "local":
            default_endpoint = "http://localhost:11434"
            endpoint = input(f"本地服务端点 [{default_endpoint}]: ").strip() or default_endpoint
            self.config['llm']['endpoint'] = endpoint
    
    def _setup_security_config(self):
        """配置安全选项"""
        print("\n🔒 安全配置")
        print("-" * 30)
        
        # 严格模式
        strict = input(f"启用严格模式 (阻止高风险命令) [{'y' if self.config['security']['strict_mode'] else 'n'}]: ").strip().lower()
        if strict in ['y', 'yes']:
            self.config['security']['strict_mode'] = True
        elif strict in ['n', 'no']:
            self.config['security']['strict_mode'] = False
        
        # sudo权限
        sudo = input(f"允许sudo命令 [{'y' if self.config['security']['allow_sudo'] else 'n'}]: ").strip().lower()
        if sudo in ['y', 'yes']:
            self.config['security']['allow_sudo'] = True
        elif sudo in ['n', 'no']:
            self.config['security']['allow_sudo'] = False
        
        # 允许的目录
        print("\n允许的工作目录 (用逗号分隔，留空表示不限制):")
        dirs = input().strip()
        if dirs:
            self.config['security']['allowed_dirs'] = [d.strip() for d in dirs.split(',')]
    
    def _setup_execution_config(self):
        """配置执行选项"""
        print("\n⚙️  执行配置")
        print("-" * 30)
        
        # 默认工作目录
        work_dir = input(f"工作目录 [{os.getcwd()}]: ").strip() or os.getcwd()
        self.config['execution']['working_dir'] = work_dir
        
        # 执行超时
        timeout = input(f"命令超时时间(秒) [{self.config['execution']['timeout']}]: ").strip()
        if timeout.isdigit():
            self.config['execution']['timeout'] = int(timeout)
        
        # 默认干运行
        dry_run = input(f"默认启用干运行模式 [{'y' if self.config['execution']['dry_run_default'] else 'n'}]: ").strip().lower()
        if dry_run in ['y', 'yes']:
            self.config['execution']['dry_run_default'] = True
        elif dry_run in ['n', 'no']:
            self.config['execution']['dry_run_default'] = False
    
    def show_config(self):
        """显示当前配置"""
        print("\n📋 当前配置")
        print("=" * 50)
        
        # 大模型配置
        llm_config = self.config.get('llm', {})
        print(f"🤖 大模型:")
        print(f"   服务商: {llm_config.get('provider', '未设置')}")
        print(f"   模型: {llm_config.get('model', '未设置')}")
        
        api_key = llm_config.get('api_key', '')
        if api_key:
            masked_key = api_key[:8] + '*' * (len(api_key) - 8) if len(api_key) > 8 else '*' * len(api_key)
            print(f"   API Key: {masked_key}")
        else:
            print("   API Key: 未设置")
        
        # 安全配置
        security_config = self.config.get('security', {})
        print(f"\n🔒 安全配置:")
        print(f"   严格模式: {'是' if security_config.get('strict_mode') else '否'}")
        print(f"   允许sudo: {'是' if security_config.get('allow_sudo') else '否'}")
        
        allowed_dirs = security_config.get('allowed_dirs', [])
        if allowed_dirs:
            print(f"   允许目录: {', '.join(allowed_dirs)}")
        else:
            print("   允许目录: 不限制")
        
        # 执行配置
        exec_config = self.config.get('execution', {})
        print(f"\n⚙️  执行配置:")
        print(f"   工作目录: {exec_config.get('working_dir', '当前目录')}")
        print(f"   超时时间: {exec_config.get('timeout', 30)}秒")
        print(f"   默认干运行: {'是' if exec_config.get('dry_run_default') else '否'}")
        
        print(f"\n📄 配置文件: {self.config_file}")
        print("=" * 50)
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self.config.copy()
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """更新配置"""
        try:
            self.config = self._deep_merge(self.config, updates)
            return self.save_config()
        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            return False
    
    def get(self, key: str, default=None):
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置项"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        return self.save_config()
    
    def validate_config(self) -> List[str]:
        """验证配置"""
        errors = []
        
        # 验证大模型配置
        llm_config = self.config.get('llm', {})
        provider = llm_config.get('provider')
        
        if not provider:
            errors.append("未设置大模型服务商")
        elif provider not in ['openai', 'anthropic', 'zhipuai', 'local']:
            errors.append(f"不支持的服务商: {provider}")
        
        if not llm_config.get('model'):
            errors.append("未设置模型名称")
        
        if provider in ['openai', 'anthropic', 'zhipuai'] and not llm_config.get('api_key'):
            errors.append(f"未设置{provider} API Key")
        
        # 验证安全配置
        security_config = self.config.get('security', {})
        allowed_dirs = security_config.get('allowed_dirs', [])
        
        for dir_path in allowed_dirs:
            if not os.path.exists(dir_path):
                errors.append(f"允许目录不存在: {dir_path}")
        
        # 验证执行配置
        exec_config = self.config.get('execution', {})
        work_dir = exec_config.get('working_dir')
        
        if work_dir and not os.path.exists(work_dir):
            errors.append(f"工作目录不存在: {work_dir}")
        
        timeout = exec_config.get('timeout', 30)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            errors.append("超时时间必须是正数")
        
        return errors
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def backup_config(self) -> bool:
        """备份配置文件"""
        try:
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.config_dir / f"config_backup_{timestamp}.yaml"
            
            shutil.copy2(self.config_file, backup_file)
            logger.info(f"配置备份成功: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"配置备份失败: {e}")
            return False
