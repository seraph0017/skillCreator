import argparse
import sys
import os
import time
from datetime import datetime

# 获取当前脚本所在目录并添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from feishu_task_client import FeishuTask

def list_tasks(limit=20, type_filter=None):
    """列出任务"""
    assistant = FeishuTask()
    
    if not assistant.app_id:
        print("❌ 未配置，请先运行: python3 feishu_task_client.py")
        return False
        
    result = assistant.list_tasks(page_size=limit, task_list_type=type_filter)
    
    if result and result.get("code") == 0:
        items = result.get("data", {}).get("items", [])
        if not items:
            print("📭 没有找到任务")
            return True
            
        print(f"📋 找到 {len(items)} 个任务:")
        for item in items:
            summary = item.get("summary", "无标题")
            guid = item.get("guid")
            completed_at = item.get("completed_at", "0")
            status = "✅" if completed_at != "0" else "TODO"
            
            due_info = ""
            if item.get("due"):
                ts = int(item.get("due").get("timestamp", 0)) / 1000
                dt = datetime.fromtimestamp(ts)
                due_info = f" (截止: {dt.strftime('%Y-%m-%d %H:%M')})"
                
            print(f"[{status}] {guid} - {summary}{due_info}")
        return True
    else:
        print(f"❌ 获取列表失败: {result}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="列出飞书任务")
    parser.add_argument("limit", type=int, nargs="?", default=20, help="显示数量 (默认 20)")
    parser.add_argument("--type", help="任务类型 (created/assigned/completed/deleted/followed)", default=None)
    
    args = parser.parse_args()
    
    list_tasks(args.limit, args.type)
