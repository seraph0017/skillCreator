#!/usr/bin/env python3
"""
删除飞书日程
用法: python3 delete.py <event_id>
"""

import sys
import os
import requests

# 获取当前脚本所在目录并添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from feishu_client import FeishuCalendar

def delete_event(event_id):
    """删除日程事件"""
    assistant = FeishuCalendar()
    
    if not assistant.app_id:
        print("❌ 未配置，请先运行: python3 feishu_client.py")
        return False
    
    try:
        token = assistant._get_tenant_access_token()
        
        # 获取日历ID
        calendars = assistant.list_calendars()
        if calendars.get("code") != 0:
            print(f"❌ 获取日历失败")
            return False
            
        calendar_list = calendars.get("data", {}).get("calendar_list", [])
        if not calendar_list:
            print("❌ 没有找到日历")
            return False
            
        calendar_id = calendar_list[0].get("calendar_id")
        
        # 删除日程
        url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events/{event_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        response = requests.delete(url, headers=headers)
        resp_json = response.json()
        
        if resp_json.get("code") != 0:
            print(f"❌ 删除失败: {resp_json.get('msg', '未知错误')}")
            return False
            
        print(f"✅ 删除成功: {event_id}")
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 delete.py <event_id>")
        print("示例: python3 delete.py f905157c-962b-426f-bf03-65a7d4bbe8d3_0")
        sys.exit(1)
    
    event_id = sys.argv[1]
    success = delete_event(event_id)
    sys.exit(0 if success else 1)