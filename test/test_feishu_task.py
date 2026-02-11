import sys
import os
import time

# Add skill directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../.trae/skills/feishu-tasks")))

from feishu_task_client import FeishuTask

def test_create_task():
    # Check for config
    config_path = os.path.expanduser("~/.feishu_task_config.json")
    if not os.path.exists(config_path):
        print(f"Skipping test: Config file {config_path} not found.")
        return

    assistant = FeishuTask()
    if not assistant.app_id:
        print("Skipping test: Feishu Task not configured.")
        return

    print("Testing Create Task...")
    summary = f"Test Task {int(time.time())}"
    description = "Created by automated test."
    
    # Due tomorrow
    due_time = int(time.time() * 1000) + 86400 * 1000
    
    result = assistant.create_task(summary, description, due_time)
    print(f"Create result: {result}")
    
    if result.get("code") == 0:
        task = result.get("data", {}).get("task", {})
        guid = task.get("guid")
        print(f"Task created: {guid}")
        
        # Test Get
        print("Testing Get Task...")
        get_res = assistant.get_task(guid)
        print(f"Get result: {get_res}")
        
        # Test Delete
        print("Testing Delete Task...")
        del_res = assistant.delete_task(guid)
        print(f"Delete result: {del_res}")
    else:
        print("Create task failed.")

if __name__ == "__main__":
    test_create_task()
