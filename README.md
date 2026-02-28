# 🎮 2048 网页游戏

经典的 2048 滑块益智游戏网页版实现。

## 🎯 快速开始

```bash
# 进入游戏目录
cd game

# 在浏览器中打开
open index.html  # macOS
# 或
xdg-open index.html  # Linux
# 或直接双击 index.html 文件
```

## 🎮 游戏规则

1. 使用**方向键**（↑ ↓ ← →）移动所有方块
2. 相同数字的方块碰撞时会**合并**
3. 目标是合并出 **2048** 或更高的数字！

## 📁 项目结构

```
2048-game/
├── game/              # 游戏文件
│   ├── index.html    # 游戏主页面
│   ├── style.css     # 样式
│   ├── game.js       # 游戏逻辑
│   └── README.md     # 详细说明
├── agent.py          # 自主代理核心
├── client.py         # API 客户端
├── tools.py          # 工具定义
├── state.py          # 状态管理
└── main.py           # CLI 入口
```

## ✨ 游戏特性

- ✅ 完整的 2048 游戏逻辑
- ✅ 流畅的动画效果
- ✅ 分数记录和最高分
- ✅ 响应式设计
- ✅ 触摸屏支持
- ✅ 游戏结束检测

## 🛠️ 技术栈

- HTML5 + CSS3 + JavaScript
- 自主代理系统（GLM 驱动）

## 📝 开发说明

本项目由自主代理系统创建，基于：
- **模型**: 智谱 GLM-4-flash
- **框架**: 自主代理 Demo
- **路径**: ~/BEN/AI/2048-game

---

*Created by Autonomous Agent with ❤️*
