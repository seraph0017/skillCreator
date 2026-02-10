import requests
import json
import time
import os
from datetime import datetime

# 复用 skill 中的函数
def get_tenant_access_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json().get("tenant_access_token")
    except Exception as e:
        print(f"获取 Token 异常: {e}")
        return None

def list_lark_calendars(token):
    url = "https://open.feishu.cn/open-apis/calendar/v4/calendars"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        print(f"获取日历列表异常: {e}")
        return None

def create_lark_calendar_event(token, calendar_id, summary, start_time, end_time, description=None):
    url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "summary": summary,
        "start_time": {"timestamp": str(start_time)},
        "end_time": {"timestamp": str(end_time)},
        "need_notification": True
    }
    if description:
        payload["description"] = description
        
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.json()
    except Exception as e:
        print(f"创建日程异常: {e}")
        return {"code": -1, "msg": str(e)}

def add_lark_calendar_attendees(token, calendar_id, event_id, attendees):
    url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events/{event_id}/attendees"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "attendees": attendees,
        "need_notification": True
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.json()
    except Exception as e:
        print(f"添加参与人异常: {e}")
        return {"code": -1, "msg": str(e)}

if __name__ == "__main__":
    APP_ID = os.getenv("LARK_APP_ID")
    APP_SECRET = os.getenv("LARK_APP_SECRET")
    # 你需要提供你的 Open ID 或 User ID
    # 示例: export LARK_USER_OPEN_ID="ou_xxxxxx"
    USER_OPEN_ID = os.getenv("LARK_USER_OPEN_ID") 
    
    if not APP_ID or not APP_SECRET:
        print("请设置 LARK_APP_ID 和 LARK_APP_SECRET 环境变量")
        exit(1)
        
    if not USER_OPEN_ID:
        print("警告: 未设置 LARK_USER_OPEN_ID，将不添加参与人")
        print("示例: export LARK_USER_OPEN_ID='ou_xxxxxx'")
    
    token = get_tenant_access_token(APP_ID, APP_SECRET)
    if not token:
        print("获取 Token 失败")
        exit(1)

    # 获取日历 (逻辑保持不变)
    calendars = list_lark_calendars(token)
    calendar_id = None
    if calendars and calendars.get("code") == 0 and calendars.get("data", {}).get("calendar_list"):
        for cal in calendars["data"]["calendar_list"]:
            if cal.get("type") == "primary":
                calendar_id = cal["calendar_id"]
                break
        if not calendar_id:
             calendar_id = calendars["data"]["calendar_list"][0]["calendar_id"]
    else:
        print("获取日历列表失败")
        exit(1)
    
    print(f"使用日历 ID: {calendar_id}")
    
    # 设置时间 (逻辑保持不变)
    try:
        start_dt = datetime.strptime("2026-02-10 14:00:00", "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime("2026-02-10 17:00:00", "%Y-%m-%d %H:%M:%S")
        start_ts = int(start_dt.timestamp())
        end_ts = int(end_dt.timestamp())
        
        print(f"创建日程: 2026-02-10 下午会议 (14:00-17:00)")
        
        # 1. 创建日程
        result = create_lark_calendar_event(
            token, 
            calendar_id, 
            "下午会议 (带参与人)", 
            start_ts, 
            end_ts, 
            "这是自动创建的下午会议日程，包含参与人"
        )
        
        print(f"创建结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 2. 添加参与人
        if result.get("code") == 0 and USER_OPEN_ID:
            event_id = result["data"]["event"]["event_id"]
            print(f"正在添加参与人: {USER_OPEN_ID}")
            
            attendees = [
                {
                    "type": "user",
                    "user_id_type": "open_id",
                    "user_id": USER_OPEN_ID
                }
            ]
            
            attendee_result = add_lark_calendar_attendees(token, calendar_id, event_id, attendees)
            print(f"添加参与人结果: {json.dumps(attendee_result, indent=2, ensure_ascii=False)}")
            
    except Exception as e:
        print(f"执行出错: {e}")
