"""
状态管理模块
负责任务状态的持久化和恢复
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional


STATE_FILE = "agent_state.json"


def get_default_state() -> Dict[str, Any]:
    """返回默认的状态结构"""
    return {
        "task": "",
        "goal": "",
        "plan": [],
        "current_step": 0,
        "completed_steps": [],
        "history": [],
        "status": "idle",  # idle, planning, executing, completed, failed
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }


def load_state() -> Dict[str, Any]:
    """从文件加载状态"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[状态] 加载状态文件失败: {e}")
    return get_default_state()


def save_state(state: Dict[str, Any]) -> bool:
    """保存状态到文件"""
    try:
        state["updated_at"] = datetime.now().isoformat()
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[状态] 保存状态文件失败: {e}")
        return False


def reset_state() -> Dict[str, Any]:
    """重置状态"""
    state = get_default_state()
    save_state(state)
    return state


def add_message(state: Dict[str, Any], role: str, content: str) -> Dict[str, Any]:
    """添加消息到历史记录"""
    state["history"].append({
        "role": role,
        "content": content
    })
    return state


def add_tool_result(state: Dict[str, Any], tool_call_id: str, tool_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """添加工具调用结果到历史记录"""
    state["history"].append({
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": tool_name,
        "content": json.dumps(result, ensure_ascii=False)
    })
    return state


def set_plan(state: Dict[str, Any], plan: List[str]) -> Dict[str, Any]:
    """设置执行计划"""
    state["plan"] = plan
    state["current_step"] = 0
    state["completed_steps"] = []
    state["status"] = "executing"
    return state


def complete_step(state: Dict[str, Any], step_index: int) -> Dict[str, Any]:
    """标记步骤完成"""
    if step_index not in state["completed_steps"]:
        state["completed_steps"].append(step_index)
    state["current_step"] = step_index + 1

    # 检查是否所有步骤都完成
    if state["current_step"] >= len(state["plan"]):
        state["status"] = "completed"

    return state


def is_completed(state: Dict[str, Any]) -> bool:
    """检查任务是否已完成"""
    return state["status"] == "completed"


def can_resume(state: Dict[str, Any]) -> bool:
    """检查是否可以恢复执行"""
    return (
        state["status"] in ["planning", "executing"] and
        len(state["plan"]) > 0 and
        state["current_step"] < len(state["plan"])
    )


def print_state_summary(state: Dict[str, Any]) -> None:
    """打印状态摘要"""
    print(f"\n{'='*50}")
    print(f"[状态摘要]")
    print(f"  任务: {state['task'] or '(未设置)'}")
    print(f"  状态: {state['status']}")
    print(f"  当前进度: {state['current_step']}/{len(state['plan'])}")

    if state['plan']:
        print(f"\n[执行计划]")
        for i, step in enumerate(state['plan']):
            status = "✓" if i in state['completed_steps'] else "○"
            current = ">" if i == state['current_step'] else " "
            print(f"  {current} {status} {i+1}. {step}")

    print(f"{'='*50}\n")
