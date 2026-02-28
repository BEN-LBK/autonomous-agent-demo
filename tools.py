"""
工具定义和执行模块
提供三个基础工具：read_file, write_file, run_bash
"""

import os
import subprocess
import json
from typing import Dict, Any


# 工具定义（OpenAI Function Calling 格式）
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取指定路径的文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要读取的文件绝对路径"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "将内容写入指定路径的文件。如果文件不存在会创建，如果存在会覆盖。",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要写入的文件绝对路径"
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入的文件内容"
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_bash",
            "description": "执行 bash 命令。可以用于创建目录、列出文件、运行程序等操作。",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要执行的 bash 命令"
                    }
                },
                "required": ["command"]
            }
        }
    }
]


def read_file(file_path: str) -> Dict[str, Any]:
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"success": True, "output": content, "error": None}
    except FileNotFoundError:
        return {"success": False, "output": "", "error": f"文件不存在: {file_path}"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}


def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """写入文件内容"""
    try:
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "output": f"成功写入文件: {file_path}", "error": None}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}


def run_bash(command: str) -> Dict[str, Any]:
    """执行 bash 命令"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout
        if result.returncode != 0:
            return {
                "success": False,
                "output": output,
                "error": f"命令执行失败 (exit code {result.returncode}): {result.stderr}"
            }
        return {"success": True, "output": output, "error": None}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": "命令执行超时"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}


# 工具名称到函数的映射
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "run_bash": run_bash
}


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """执行指定的工具"""
    if tool_name not in TOOL_FUNCTIONS:
        return {"success": False, "output": "", "error": f"未知工具: {tool_name}"}

    func = TOOL_FUNCTIONS[tool_name]
    return func(**arguments)
