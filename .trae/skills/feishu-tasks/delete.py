import argparse
import sys
import os

# 获取当前脚本所在目录并添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from feishu_task_client import FeishuTask

def delete_task(task_guid):
    """删除任务"""
    assistant = FeishuTask()
    
    if not assistant.app_id:
        print("❌ 未配置，请先运行: python3 feishu_task_client.py")
        return False
        
    result = assistant.delete_task(task_guid)
    
    if result and result.get("code") == 0:
        print(f"🗑️ 删除成功: {task_guid}")
        return True
    else:
        print(f"❌ 删除失败: {result}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="删除飞书任务")
    parser.add_argument("guid", help="任务 GUID")
    
    args = parser.parse_args()
    
    delete_task(args.guid)
