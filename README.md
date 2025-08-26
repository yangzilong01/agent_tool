# Linux/Unix Agent Tool

🤖 **智能命令行助手** - 将自然语言转换为Linux/Unix命令并执行

## 📖 项目简介

Agent Tool 是一个智能的命令行助手，它能够理解用户的自然语言描述，并将其转换为相应的Linux/Unix命令。该工具支持多种大模型（OpenAI GPT、Anthropic Claude、本地模型等），具备完善的安全检查机制和用户友好的交互界面。

## ✨ 主要特性

- 🧠 **多模型支持**: 支持 OpenAI GPT、Anthropic Claude、本地模型（Ollama等）
- 🔒 **安全防护**: 内置危险命令检测和执行确认机制
- 🎯 **智能转换**: 准确理解自然语言并生成相应的命令
- 🎨 **友好界面**: 支持Rich库的美观输出和纯文本模式
- 📝 **完整日志**: 详细记录命令生成和执行历史
- ⚙️ **灵活配置**: 支持多种安全策略和执行模式
- 🔧 **便捷操作**: 支持交互模式和单命令执行

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 初始化配置

```bash
python main.py --setup
```

按照提示完成以下配置：
1. 选择大模型服务商（OpenAI/Anthropic/本地模型）
2. 配置API密钥或本地模型端点
3. 设置安全策略
4. 配置执行参数

### 启动程序

```bash
# 交互模式
python main.py

# 单命令执行
python main.py -c "列出当前目录的所有文件"

# 自动执行模式（跳过确认）
python main.py --auto

# 查看配置
python main.py --config
```

## 🎯 使用示例

### 基本操作示例

```
🔤 请描述您要执行的操作: 显示当前目录下所有txt文件的详细信息

🤖 AI生成的命令
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
命令:        ls -la *.txt
描述:        显示当前目录下所有txt文件的详细信息
风险等级:    LOW
说明:        这个命令会列出所有.txt文件的详细信息，包括权限、大小、修改时间等

选择操作:
y/yes - 执行命令
m/modify - 修改命令
e/explain - 解释命令
h/help - 显示帮助
n/no - 取消执行

请选择 [y]: y
```

### 系统管理示例

```
🔤 请描述您要执行的操作: 查看系统内存使用情况

🤖 AI生成的命令
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
命令:        free -h
描述:        以人类可读格式显示内存使用情况
风险等级:    LOW
说明:        这个命令显示系统内存的使用情况，-h参数使输出更易读
```

### 文件操作示例

```
🔤 请描述您要执行的操作: 创建一个名为backup的目录并复制所有日志文件到其中

🤖 AI生成的命令
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
命令:        mkdir -p backup && cp *.log backup/
描述:        创建backup目录并复制所有日志文件
风险等级:    MEDIUM
说明:        该命令分两步执行：首先创建backup目录，然后复制所有.log文件到该目录

⚠️ 警告信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 包含文件操作
• 包含管道或重定向操作
```

## 🔧 配置说明

### 配置文件位置
- 配置目录: `~/.agent_tool/`
- 主配置文件: `~/.agent_tool/config.yaml`
- 日志文件: `~/.agent_tool/logs/`
- 命令历史: `~/.agent_tool/command_history.jsonl`

### 主要配置项

```yaml
llm:
  provider: openai          # 大模型服务商: openai/anthropic/local
  model: gpt-3.5-turbo      # 模型名称
  api_key: ""               # API密钥
  base_url: ""              # 可选的基础URL（用于代理）
  temperature: 0.3          # 生成温度
  max_tokens: 1000          # 最大token数

security:
  strict_mode: true         # 严格模式（阻止高风险命令）
  allow_sudo: false         # 允许sudo命令
  allowed_dirs: []          # 限制操作目录
  dangerous_commands_block: true  # 阻止危险命令

execution:
  timeout: 30               # 命令执行超时（秒）
  working_dir: ""           # 工作目录
  dry_run_default: false    # 默认干运行模式
  auto_confirm: false       # 自动确认执行
```

### 预设配置模板

1. **安全模式**（推荐新手）
   - 启用严格模式
   - 禁止sudo命令
   - 默认启用干运行

2. **开发模式**（适合开发者）
   - 放宽安全限制
   - 允许sudo命令
   - 正常执行模式

3. **自动模式**（批处理）
   - 跳过执行确认
   - 适合脚本化使用

## 🔒 安全特性

### 危险命令检测

系统会自动检测并阻止以下类型的危险操作：

- 文件系统破坏: `rm -rf /`, `mkfs.*`, `wipefs` 等
- 权限危险操作: `chmod 777 /`, `chown * /` 等
- 系统服务操作: `systemctl stop`, `service stop` 等
- 恶意代码执行: Fork炸弹、远程代码执行等
- 网络危险操作: 下载并执行脚本等

### 风险等级分类

- **LOW**: 一般的查看和信息获取命令
- **MEDIUM**: 文件操作、网络操作等
- **HIGH**: 系统配置修改、权限操作等
- **CRITICAL**: 危险的系统操作，将被自动拒绝

### 安全配置

可通过配置文件调整安全策略：

- `strict_mode`: 严格模式，拒绝执行高风险命令
- `allow_sudo`: 是否允许需要管理员权限的命令
- `allowed_dirs`: 限制文件操作的目录范围
- `dangerous_commands_block`: 是否阻止危险命令

## 📋 命令行参数

```bash
usage: main.py [-h] [-c COMMAND] [--config] [--setup] [--auto] [--debug]

Linux/Unix Agent Tool - 智能命令行助手

options:
  -h, --help            显示帮助信息
  -c COMMAND, --command COMMAND
                        执行单个命令（非交互模式）
  --config              显示当前配置
  --setup               初始化配置
  --auto                自动执行模式（跳过确认）
  --debug               启用调试模式

示例:
  main.py                    # 启动交互模式
  main.py -c "列出当前目录的文件"   # 单次执行
  main.py --config             # 显示配置
  main.py --setup              # 初始化配置
```

## 🔍 支持的大模型

### OpenAI模型
- GPT-3.5 Turbo
- GPT-4
- GPT-4 Turbo
- 兼容OpenAI API的其他模型

### Anthropic模型
- Claude-3 Sonnet
- Claude-3 Haiku
- Claude-3 Opus

### 本地模型
- 支持Ollama等本地部署方案
- 兼容OpenAI API格式的本地模型
- 支持自定义端点配置

## 📊 日志和历史

### 日志功能
- 详细的命令生成和执行日志
- 安全违规记录
- 用户操作历史
- 系统错误记录

### 命令历史
- JSONL格式存储
- 支持历史查询和统计
- 可导出为JSON或CSV格式

### 统计信息
- 命令执行成功率
- 最常用命令统计
- 风险等级分布
- 平均执行时间

## 🛠️ 高级功能

### 交互式命令修改
在执行前可以修改生成的命令：
- `m/modify`: 修改命令
- `e/explain`: 查看命令解释
- `h/help`: 显示详细帮助

### 批处理模式
```bash
# 自动执行模式
python main.py --auto -c "更新系统软件包"

# 干运行模式（只显示命令不执行）
# 在配置中设置 dry_run_default: true
```

### 配置管理
```bash
# 显示当前配置
python main.py --config

# 重新配置
python main.py --setup

# 交互式配置修改
# 在程序中使用 "config show" 或 "config setup" 命令
```

## 🤝 贡献指南

欢迎提交问题报告和功能请求！如果您想为项目做贡献：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## ⚠️ 免责声明

- 请谨慎使用本工具，特别是在生产环境中
- 用户应当理解所执行命令的含义和风险
- 建议在测试环境中充分验证后再在生产环境使用
- 作者不对使用本工具造成的任何损失承担责任

## 📞 支持与反馈

如果您在使用过程中遇到问题或有建议，请：

1. 查看日志文件获取详细错误信息
2. 检查配置是否正确
3. 提交Issue描述问题和环境信息

---

**🎉 享受智能命令行体验！**
