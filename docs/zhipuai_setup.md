# 智谱清言 API 配置指南

## 1. 获取API密钥

1. 访问智谱AI开放平台：https://open.bigmodel.cn/
2. 注册账号并登录
3. 在控制台中创建API密钥
4. 复制API密钥备用

## 2. 安装依赖

```bash
pip install zhipuai
```

## 3. 配置方法

### 方法一：使用配置向导（推荐）

```bash
python main.py config
```

然后选择：
- 选择 "3. 智谱清言 (GLM-4)"
- 输入你的API密钥
- 选择模型（推荐 glm-4）

### 方法二：直接复制配置文件

```bash
cp config/zhipuai_example.yaml ~/.agent_tool/config.yaml
```

然后编辑 `~/.agent_tool/config.yaml`，填入你的API密钥：

```yaml
llm:
  provider: zhipuai
  model: glm-4
  api_key: "你的智谱清言API密钥"
  base_url: "https://open.bigmodel.cn/api/paas/v4/"
```

### 方法三：环境变量（推荐用于生产环境）

```bash
export ZHIPUAI_API_KEY="你的智谱清言API密钥"
```

## 4. 支持的模型

- `glm-4`: 最新的GLM-4模型，推荐使用
- `glm-4-turbo`: GLM-4的快速版本
- `glm-3-turbo`: GLM-3的快速版本

## 5. 配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `model` | 模型名称 | glm-4 |
| `api_key` | API密钥 | 必填 |
| `base_url` | API端点 | https://open.bigmodel.cn/api/paas/v4/ |
| `temperature` | 创造性程度(0-1) | 0.3 |
| `max_tokens` | 最大生成长度 | 1000 |

## 6. 验证配置

运行以下命令验证配置是否正确：

```bash
python main.py test
```

## 7. 使用示例

配置完成后，你就可以使用智谱清言作为你的AI助手：

```bash
python main.py "帮我查看当前目录下的文件"
python main.py "创建一个Python虚拟环境"
python main.py "安装项目依赖"
```

## 8. 故障排除

### 常见问题

1. **ImportError: 需要安装 zhipuai 库**
   ```bash
   pip install zhipuai
   ```

2. **API密钥错误**
   - 检查API密钥是否正确
   - 确认账户余额是否充足

3. **网络连接问题**
   - 检查网络连接
   - 确认防火墙设置

### 获取帮助

如果遇到问题，可以：
1. 查看日志文件：`~/.agent_tool/logs/agent.log`
2. 运行调试模式：`python main.py --debug`
3. 查看配置：`python main.py config --show`
