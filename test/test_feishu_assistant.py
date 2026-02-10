import sys
import os
import time

# 添加 skill 目录到 path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../.trae/skills/feishu-assistant")))

from feishu_client import FeishuAssistant

def test_feishu_client():
    """
    测试 FeishuAssistant 客户端
    """
    assistant = FeishuAssistant()
    
    # 如果没配置，先运行初始化（这会提示输入）
    if not assistant.app_id:
        print("Starting initialization...")
        if not assistant.initialize():
            print("Initialization failed.")
            return

    # Debug: List calendars
    print("\nListing calendars...")
    calendars_resp = assistant.list_calendars()
    print(f"Calendars: {calendars_resp}")
    
    # 尝试找到一个可用的 calendar_id
    calendar_id = None
    if calendars_resp.get("code") == 0:
        calendar_list = calendars_resp.get("data", {}).get("calendar_list", [])
        if calendar_list:
            # 优先找 primary 或第一个
            for cal in calendar_list:
                if cal.get("type") == "primary":
                    calendar_id = cal.get("calendar_id")
                    break
            if not calendar_id:
                calendar_id = calendar_list[0].get("calendar_id")
            print(f"Using Calendar ID: {calendar_id}")
        else:
            print("No calendars found for this app/tenant.")
    else:
        print("Failed to list calendars.")

    # 测试创建日程
    print("\nTesting event creation...")
    summary = "测试会议-自动生成内容"
    # 设置为当前时间 1 小时后
    start_time = int(time.time()) + 3600
    end_time = start_time + 1800 # 30分钟
    
    # 场景 1: Default attendees and content
    print("Scenario 1: Default attendees and content")
    event_id = assistant.create_event(summary, start_time, end_time, calendar_id=calendar_id)
    
    if event_id:
        print(f"Successfully created event: {event_id}")
    else:
        print("Failed to create event.")

if __name__ == "__main__":
    test_feishu_client()
