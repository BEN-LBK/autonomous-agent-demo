# 自主代理系统 (Autonomous Agent Demo)

一个简化版的自主代理系统，能够自动分解任务、执行步骤并持久化状态。

## 特性

- **自动任务分解**: 将复杂任务分解为可执行步骤
- **工具调用**: 支持 read_file、write_file、run_bash 三个基础工具
- **状态持久化**: 自动保存执行状态，支持断点恢复
- **API 兼容**: 使用 OpenAI SDK，兼容 GLM、Claude 等 API

## 项目结构

```
autonomous-agent-demo/
├── agent.py      # 核心代理逻辑
├── client.py     # API 客户端封装
├── tools.py      # 工具定义和执行
├── state.py      # 状态管理
├── main.py       # 主程序入口
├── requirements.txt
├── .env.example  # 环境变量示例
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API 配置
# 支持 OpenAI、GLM、Claude 等 API
```

### 3. 运行代理

```bash
# 开始新任务
python main.py --task "创建一个简单的 Python 项目"

# 从断点恢复
python main.py --resume

# 查看状态
python main.py --status

# 重置状态
python main.py --reset
```

## API 配置

### OpenAI 官方 API

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o
```

### 智谱 GLM API

```env
OPENAI_API_KEY=your_glm_api_key
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
OPENAI_MODEL=glm-4-flash
```

### Claude API (通过 OpenAI 兼容接口)

```env
OPENAI_API_KEY=your_claude_api_key
OPENAI_BASE_URL=https://api.anthropic.com/v1
OPENAI_MODEL=claude-3-5-sonnet-20241022
```

## 示例任务

```bash
# 创建简单的 Python 项目
python main.py --task "创建一个 Python 项目，包含 README.md、main.py 和 requirements.txt"

# 创建 Web 应用
python main.py --task "创建一个 Flask 应用，包含首页路由"

# 创建工具
python main.py --task "创建一个文件批量重命名工具"
```

## 工作原理

1. **任务理解**: 代理接收任务描述
2. **自动规划**: LLM 将任务分解为具体步骤
3. **工具调用**: 代理调用工具执行每个步骤
4. **状态保存**: 每步执行后保存状态到 JSON 文件
5. **断点恢复**: 支持从任意步骤恢复执行

## 可用工具

- `read_file`: 读取文件内容
- `write_file`: 写入文件内容
- `run_bash`: 执行 bash 命令

## 状态文件

执行状态保存在 `agent_state.json`，包含：

```json
{
  "task": "原始任务描述",
  "plan": ["步骤1", "步骤2", ...],
  "current_step": 0,
  "completed_steps": [],
  "history": [...],
  "status": "planning|executing|completed|failed"
}
```

## 技术栈

- Python 3.8+
- OpenAI SDK
- python-dotenv

## License

MIT

## 参考

基于 [Claude Autonomous Coding](https://github.com/anthropics/claude-code-examples/tree/main/autonomous-coding) 简化实现。
