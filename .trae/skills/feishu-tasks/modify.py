import argparse
import sys
import os
from datetime import datetime

# 获取当前脚本所在目录并添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from feishu_task_client import FeishuTask

def modify_task(task_guid, summary=None, description=None, due_time=None, complete=False):
    """修改任务"""
    assistant = FeishuTask()
    
    if not assistant.app_id:
        print("❌ 未配置，请先运行: python3 feishu_task_client.py")
        return False
    
    if complete:
        result = assistant.complete_task(task_guid)
        if result and result.get("code") == 0:
            print(f"✅ 任务已标记完成: {task_guid}")
        else:
            print(f"❌ 完成任务失败: {result}")
        # 如果只是完成，可能就不继续更新其他字段了，或者继续更新？
        # 这里假设可以同时进行
        
    if summary or description or due_time:
        due_timestamp = None
        if due_time:
            try:
                dt = datetime.strptime(due_time, "%Y-%m-%d %H:%M")
                due_timestamp = int(dt.timestamp() * 1000)
            except ValueError:
                print("❌ 时间格式错误，请使用 'YYYY-MM-DD HH:MM'")
                return False
                
        result = assistant.update_task(task_guid, summary=summary, description=description, due_timestamp=due_timestamp)
        
        if result and result.get("code") == 0:
            print(f"✏️ 更新成功: {task_guid}")
            task = result.get("data", {}).get("task", {})
            print(f"   新标题: {task.get('summary')}")
            return True
        else:
            print(f"❌ 更新失败: {result}")
            return False
            
    if not complete and not (summary or description or due_time):
        print("⚠️ 未指定任何修改内容")
        return False

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="修改飞书任务")
    parser.add_argument("guid", help="任务 GUID")
    parser.add_argument("--summary", help="新任务标题", default=None)
    parser.add_argument("--desc", help="新任务描述", default=None)
    parser.add_argument("--due", help="新截止时间 (YYYY-MM-DD HH:MM)", default=None)
    parser.add_argument("--complete", action="store_true", help="标记任务为完成")
    
    args = parser.parse_args()
    
    modify_task(args.guid, args.summary, args.desc, args.due, args.complete)
