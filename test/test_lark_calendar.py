import requests
import json
import time
import os

# 这是一个使用 lark-assistant skill 提供的代码片段生成的测试脚本
# 用于演示如何创建飞书日程

def get_tenant_access_token(app_id, app_secret):
    """
    获取自建应用的 tenant_access_token
    """
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        if data.get("code") == 0:
            return data.get("tenant_access_token")
        else:
            print(f"获取 Token 失败: {data}")
            return None
    except Exception as e:
        print(f"请求 Token 异常: {e}")
        return None

def list_lark_calendars(token):
    """
    获取日历列表
    """
    url = "https://open.feishu.cn/open-apis/calendar/v4/calendars"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        print(f"获取日历列表失败: {e}")
        return {"code": -1, "msg": str(e)}

def create_lark_calendar_event(token, calendar_id, summary, start_time, end_time, description=None, location=None):
    """
    创建飞书日程
    
    Args:
        token (str): 访问凭证 (tenant_access_token)
        calendar_id (str): 日历 ID，通常使用 'primary' 代表用户主日历
        summary (str): 日程标题
        start_time (int): 开始时间戳（秒）
        end_time (int): 结束时间戳（秒）
        description (str, optional): 日程描述
        location (dict, optional): 地点信息，如 {"name": "会议室", "address": "地址"}
        
    Returns:
        dict: API 响应结果
    """
    url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "summary": summary,
        "start_time": {"timestamp": str(start_time)}, # 飞书要求字符串格式的时间戳
        "end_time": {"timestamp": str(end_time)}
    }
    if description:
        payload["description"] = description
    if location:
        payload["location"] = location
    
    print(f"正在创建日程: {summary}")
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return response.json()
    except Exception as e:
        print(f"请求发送失败: {e}")
        return {"code": -1, "msg": str(e)}

if __name__ == "__main__":
    # 获取环境变量
    APP_ID = os.getenv("LARK_APP_ID")
    APP_SECRET = os.getenv("LARK_APP_SECRET")
    
    if not APP_ID or not APP_SECRET:
        print("错误: 请设置环境变量 LARK_APP_ID 和 LARK_APP_SECRET")
        print("示例: export LARK_APP_ID='cli_xxx' && export LARK_APP_SECRET='xxx'")
        exit(1)

    # 1. 获取 Token
    print("正在获取 Tenant Access Token...")
    token = get_tenant_access_token(APP_ID, APP_SECRET)
    
    if token:
        print("获取 Token 成功")
        
        # 2. 获取日历列表，寻找有效的 Calendar ID
        print("正在获取日历列表...")
        calendars_resp = list_lark_calendars(token)
        
        CALENDAR_ID = None
        if calendars_resp.get("code") == 0 and calendars_resp.get("data", {}).get("calendar_list"):
            # 优先使用第一个可用日历
            first_calendar = calendars_resp["data"]["calendar_list"][0]
            CALENDAR_ID = first_calendar["calendar_id"]
            print(f"找到可用日历: {first_calendar.get('summary')} (ID: {CALENDAR_ID})")
        else:
            print(f"无法获取日历列表或列表为空: {calendars_resp}")
            # 如果获取失败，尝试 fallback 到 primary，虽然之前报错了
            CALENDAR_ID = "primary"
            print("尝试回退使用 'primary' 作为 Calendar ID")

        # 3. 创建日程
        current_time = int(time.time())
        start_time = current_time + 3600 # 1小时后
        end_time = current_time + 7200   # 2小时后
        
        result = create_lark_calendar_event(
            token=token,
            calendar_id=CALENDAR_ID,
            summary="测试 Skill 创建的日程",
            start_time=start_time,
            end_time=end_time,
            description="这是一个由 lark-assistant skill 自动生成的测试日程。",
            location={
                "name": "测试地点",
                "address": "测试地址",
                "latitude": 30.0,
                "longitude": 120.0
            }
        )
    else:
        print("无法进行后续测试，请检查 App ID 和 Secret 是否正确。")
