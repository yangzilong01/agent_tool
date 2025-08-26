# 🚀 快速开始指南

## 安装和配置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 初始化配置
```bash
python main.py --setup
```

按照提示选择：
- **服务商**: OpenAI/Anthropic/本地模型
- **API密钥**: 输入相应的API密钥
- **安全设置**: 建议新手选择"安全模式"

### 3. 首次运行
```bash
python main.py
```

## 基本使用

### 交互模式示例

```
🔤 请描述您要执行的操作: 显示当前目录的文件大小

🤖 AI生成的命令
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
命令:        ls -lh
描述:        以人类可读格式显示文件大小
风险等级:    LOW
说明:        列出当前目录文件，-l显示详细信息，-h显示易读的文件大小

选择操作:
y/yes - 执行命令
m/modify - 修改命令  
e/explain - 解释命令
h/help - 显示帮助
n/no - 取消执行

请选择 [y]: y

📋 执行结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
状态: ✅ 成功
返回码: 0
执行时间: 0.02s

📤 标准输出
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
total 48K
-rw-r--r-- 1 user user 1.2K Jan 15 10:30 config.yaml
-rw-r--r-- 1 user user  15K Jan 15 10:25 main.py
drwxr-xr-x 2 user user 4.0K Jan 15 10:20 logs
```

### 常用命令示例

| 自然语言描述 | 生成的命令示例 |
|-------------|---------------|
| "查看系统内存使用" | `free -h` |
| "列出所有运行的进程" | `ps aux` |
| "查找包含error的日志文件" | `grep -r "error" /var/log/` |
| "创建backup目录" | `mkdir -p backup` |
| "查看磁盘使用情况" | `df -h` |
| "显示最近10个命令" | `history \| tail -10` |

## 命令行选项

```bash
# 单命令执行
python main.py -c "查看当前用户"

# 自动执行模式（跳过确认）
python main.py --auto -c "列出文件"

# 显示配置信息
python main.py --config

# 重新配置
python main.py --setup

# 调试模式
python main.py --debug
```

## 安全提示

### 风险等级说明
- **LOW** 🟢: 安全的查看命令
- **MEDIUM** 🟡: 文件操作、网络命令
- **HIGH** 🔴: 系统配置修改
- **CRITICAL** ⛔: 危险操作，会被自动拒绝

### 被阻止的危险操作
```bash
rm -rf /        # 删除根目录
chmod 777 /     # 修改根目录权限
dd if=/dev/zero of=/dev/sda  # 清空硬盘
:(){ :|:& };:   # Fork炸弹
```

## 配置模式

### 安全模式 (推荐新手)
- ✅ 严格模式启用
- ❌ 禁止sudo命令
- ✅ 默认干运行模式

### 开发模式 (适合开发者)
- ❌ 严格模式关闭
- ✅ 允许sudo命令
- ❌ 正常执行模式

### 自动模式 (批处理)
- ✅ 跳过用户确认
- ⚡ 适合脚本化使用

## 故障排除

### 常见问题

**Q: 提示"大模型不可用"**
```
A: 检查API密钥是否正确设置
   python main.py --config  # 查看配置
   python main.py --setup   # 重新配置
```

**Q: 命令被拒绝执行**
```
A: 检查安全设置
   1. 查看风险等级是否过高
   2. 考虑调整安全模式设置
   3. 使用 'm/modify' 修改命令
```

**Q: 安装依赖失败**
```bash
# 尝试升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 进阶使用

### 自定义工作目录
```yaml
# ~/.agent_tool/config.yaml
execution:
  working_dir: "/home/user/workspace"
```

### 限制操作目录
```yaml
# ~/.agent_tool/config.yaml
security:
  allowed_dirs:
    - "/home/user/projects"
    - "/tmp"
```

### 使用本地模型 (Ollama)
```yaml
# ~/.agent_tool/config.yaml
llm:
  provider: local
  model: llama2
  endpoint: "http://localhost:11434"
```

## 支持的大模型

| 服务商 | 推荐模型 | 配置示例 |
|--------|---------|---------|
| OpenAI | `gpt-3.5-turbo` | 需要API Key |
| Anthropic | `claude-3-sonnet-20240229` | 需要API Key |
| 本地 | `llama2`, `codellama` | 需要Ollama等 |

---

🎉 **开始您的智能命令行之旅！**

如需更多详细信息，请查看 [README.md](README.md)
