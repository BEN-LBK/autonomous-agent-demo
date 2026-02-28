#!/usr/bin/env python3
"""
自主代理系统 - 主程序入口

用法:
    python main.py --task "任务描述"   # 开始新任务
    python main.py --resume           # 从断点恢复
    python main.py --status           # 查看当前状态
    python main.py --reset            # 重置状态
"""

import argparse
import sys
from agent import AutonomousAgent


def main():
    parser = argparse.ArgumentParser(
        description="自主代理系统 - 自动分解和执行任务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 开始新任务
  python main.py --task "创建一个简单的 Python 项目"

  # 从断点恢复
  python main.py --resume

  # 查看状态
  python main.py --status
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--task",
        type=str,
        help="任务描述"
    )
    group.add_argument(
        "--resume",
        action="store_true",
        help="从断点恢复执行"
    )
    group.add_argument(
        "--status",
        action="store_true",
        help="查看当前状态"
    )
    group.add_argument(
        "--reset",
        action="store_true",
        help="重置状态"
    )

    args = parser.parse_args()

    # 创建代理实例
    agent = AutonomousAgent()

    try:
        if args.task:
            # 开始新任务
            agent.run(args.task)
        elif args.resume:
            # 从断点恢复
            agent.resume()
        elif args.status:
            # 查看状态
            agent.show_status()
        elif args.reset:
            # 重置状态
            agent.reset()
            print("[代理] 状态已重置")

    except KeyboardInterrupt:
        print("\n\n[代理] 用户中断执行")
        print("[代理] 状态已保存，可以使用 --resume 恢复")
        sys.exit(0)
    except Exception as e:
        print(f"\n[代理] 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
