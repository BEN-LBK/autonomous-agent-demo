"""
核心代理模块
负责任务规划、执行和状态管理
"""

import json
from typing import Dict, Any, List, Optional
from client import get_client
from tools import TOOLS, execute_tool
import state as state_module


class Agent:
    """自主代理类"""

    def __init__(self):
        self.client = get_client()
        self.state = state_module.load_state()
        self.max_iterations = 50  # 最大迭代次数，防止无限循环

    def _get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是一个自主执行代理。你的任务是使用可用工具完成用户指定的任务。

可用工具：
- read_file: 读取文件内容（参数: file_path）
- write_file: 写入文件（参数: file_path, content）
- run_bash: 执行 bash 命令（参数: command）

工作原则：
1. 每次只执行一个工具调用
2. 仔细检查工具参数，确保路径正确
3. 如果某个步骤失败，尝试其他方法
4. 完成当前步骤后，继续下一个步骤
5. 当所有步骤完成后，回复 "TASK_COMPLETED" 表示任务完成

当前任务计划：
{plan}

当前进度：步骤 {current_step}/{total_steps}
待执行步骤：{current_step_description}"""

    def start(self, task: str) -> bool:
        """
        开始新任务

        Args:
            task: 任务描述

        Returns:
            是否成功启动
        """
        print(f"\n[代理] 开始新任务: {task}")

        # 重置状态
        self.state = state_module.reset_state()
        self.state["task"] = task
        self.state["status"] = "planning"
        state_module.save_state(self.state)

        # 规划任务
        print("[代理] 正在规划任务步骤...")
        plan = self.client.plan(task)

        if not plan:
            print("[代理] 规划失败，无法生成执行计划")
            self.state["status"] = "failed"
            state_module.save_state(self.state)
            return False

        # 设置计划
        self.state = state_module.set_plan(self.state, plan)
        state_module.save_state(self.state)

        print(f"[代理] 生成了 {len(plan)} 个步骤:")
        for i, step in enumerate(plan, 1):
            print(f"  {i}. {step}")

        # 开始执行
        self.state["status"] = "executing"
        state_module.save_state(self.state)

        return self.run()

    def resume(self) -> bool:
        """
        从断点恢复执行

        Returns:
            是否成功恢复
        """
        self.state = state_module.load_state()

        if not state_module.can_resume(self.state):
            print("[代理] 没有可恢复的任务")
            state_module.print_state_summary(self.state)
            return False

        print(f"[代理] 恢复任务: {self.state['task']}")
        state_module.print_state_summary(self.state)

        return self.run()

    def run(self) -> bool:
        """
        运行代理主循环

        Returns:
            任务是否成功完成
        """
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            # 检查是否已完成
            if state_module.is_completed(self.state):
                print("\n[代理] 任务已完成!")
                state_module.print_state_summary(self.state)
                return True

            # 获取当前步骤
            current_step_idx = self.state["current_step"]
            if current_step_idx >= len(self.state["plan"]):
                self.state["status"] = "completed"
                state_module.save_state(self.state)
                print("\n[代理] 任务已完成!")
                return True

            current_step = self.state["plan"][current_step_idx]
            print(f"\n[代理] 执行步骤 {current_step_idx + 1}/{len(self.state['plan'])}: {current_step}")

            # 构建对话消息
            messages = self._build_messages(current_step)

            # 调用 LLM
            response = self.client.chat(
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )

            # 处理响应
            if response.get("error"):
                print(f"[代理] API 错误: {response['error']}")
                continue

            # 添加助手回复到历史
            if response["content"]:
                self.state = state_module.add_message(
                    self.state, "assistant", response["content"]
                )

            # 处理工具调用
            if response["tool_calls"]:
                all_success = True
                for tool_call in response["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    arguments = json.loads(tool_call["function"]["arguments"])

                    print(f"[代理] 调用工具: {tool_name}({arguments})")

                    # 执行工具
                    result = execute_tool(tool_name, arguments)

                    if result["success"]:
                        print(f"[代理] 工具执行成功")
                        if result["output"]:
                            print(f"[代理] 输出: {result['output'][:200]}...")
                    else:
                        print(f"[代理] 工具执行失败: {result['error']}")
                        all_success = False

                    # 添加工具结果到历史
                    self.state = state_module.add_tool_result(
                        self.state,
                        tool_call["id"],
                        tool_name,
                        result
                    )

                # 如果工具执行成功，标记步骤完成
                if all_success:
                    self.state = state_module.complete_step(self.state, current_step_idx)
                    state_module.save_state(self.state)
                    print(f"[代理] 步骤 {current_step_idx + 1} 完成")

            elif "TASK_COMPLETED" in (response["content"] or ""):
                # LLM 认为任务完成
                self.state["status"] = "completed"
                state_module.save_state(self.state)
                print("\n[代理] 任务已完成!")
                return True

            # 保存状态
            state_module.save_state(self.state)

        print(f"\n[代理] 达到最大迭代次数 ({self.max_iterations})，任务未完成")
        self.state["status"] = "failed"
        state_module.save_state(self.state)
        return False

    def _build_messages(self, current_step: str) -> List[Dict[str, Any]]:
        """
        构建对话消息列表

        Args:
            current_step: 当前步骤描述

        Returns:
            消息列表
        """
        # 系统消息
        system_content = self._get_system_prompt().format(
            plan="\n".join(f"{i+1}. {s}" for i, s in enumerate(self.state["plan"])),
            current_step=self.state["current_step"] + 1,
            total_steps=len(self.state["plan"]),
            current_step_description=current_step
        )

        messages = [{"role": "system", "content": system_content}]

        # 添加历史消息（保留最近 20 条以控制上下文长度）
        history = self.state["history"][-20:] if len(self.state["history"]) > 20 else self.state["history"]
        messages.extend(history)

        # 如果历史为空或最后一条不是用户消息，添加当前步骤提示
        if not history or history[-1].get("role") != "user":
            messages.append({
                "role": "user",
                "content": f"请执行当前步骤: {current_step}"
            })

        return messages

    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return self.state.copy()
