"""
API 客户端封装模块
支持 OpenAI 兼容的 API（包括 GLM、Claude 等）
"""

import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class APIClient:
    """OpenAI 兼容的 API 客户端"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", None)  # 默认使用 OpenAI 官方
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")

        # 初始化客户端
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client = OpenAI(**client_kwargs)

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto"
    ) -> Dict[str, Any]:
        """
        发送聊天请求

        Args:
            messages: 对话历史
            tools: 可用工具列表
            tool_choice: 工具选择策略 ("auto", "none", 或特定工具)

        Returns:
            响应字典，包含 content, tool_calls 等字段
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice

        try:
            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message

            result = {
                "content": message.content or "",
                "tool_calls": None
            }

            # 处理工具调用
            if message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]

            return result

        except Exception as e:
            print(f"[API错误] {e}")
            return {
                "content": f"API 调用失败: {e}",
                "tool_calls": None,
                "error": str(e)
            }

    def plan(self, task: str) -> List[str]:
        """
        规划任务步骤

        Args:
            task: 任务描述

        Returns:
            步骤列表
        """
        system_prompt = """你是一个任务规划助手。给定一个任务，你需要将其分解为具体的、可执行的步骤。

每个步骤应该：
1. 清晰明确，可以直接执行
2. 使用可用工具完成：read_file（读文件）、write_file（写文件）、run_bash（执行命令）
3. 步骤之间有逻辑顺序

请直接返回步骤列表，每行一个步骤，不要编号或其他格式。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请将以下任务分解为具体步骤：\n\n{task}"}
        ]

        response = self.chat(messages)

        # 解析步骤
        steps = []
        for line in response["content"].strip().split("\n"):
            line = line.strip()
            # 移除可能的编号
            if line and len(line) > 2:
                # 移除 "1. " 或 "1) " 等前缀
                if line[0].isdigit() and (line[1] == '.' or line[1] == ')' or line[1] == ' '):
                    line = line[2:].strip()
                elif line[0] in ['-', '*', '•']:
                    line = line[1:].strip()
                if line:
                    steps.append(line)

        return steps


# 全局客户端实例
_client = None


def get_client() -> APIClient:
    """获取全局客户端实例"""
    global _client
    if _client is None:
        _client = APIClient()
    return _client
