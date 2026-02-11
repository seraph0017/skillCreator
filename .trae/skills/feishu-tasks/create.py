import argparse
import sys
import os
import time
from datetime import datetime

# 获取当前脚本所在目录并添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from feishu_task_client import FeishuTask

def create_task(summary, description=None, due_time=None):
    """创建任务"""
    assistant = FeishuTask()
    
    if not assistant.app_id:
        print("❌ 未配置，请先运行: python3 feishu_task_client.py")
        return False
        
    due_timestamp = None
    if due_time:
        try:
            # 尝试解析时间 (YYYY-MM-DD HH:MM)
            dt = datetime.strptime(due_time, "%Y-%m-%d %H:%M")
            due_timestamp = int(dt.timestamp() * 1000)
        except ValueError:
            print("❌ 时间格式错误，请使用 'YYYY-MM-DD HH:MM'")
            return False

    result = assistant.create_task(summary, description=description, due_timestamp=due_timestamp)
    
    if result and result.get("code") == 0:
        task = result.get("data", {}).get("task", {})
        print(f"✅ 创建成功: {task.get('guid')}")
        print(f"📌 任务: {task.get('summary')}")
        return True
    else:
        print(f"❌ 创建失败: {result}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="创建飞书任务")
    parser.add_argument("summary", help="任务标题")
    parser.add_argument("--desc", help="任务描述", default=None)
    parser.add_argument("--due", help="截止时间 (YYYY-MM-DD HH:MM)", default=None)
    
    args = parser.parse_args()
    
    create_task(args.summary, args.desc, args.due)
