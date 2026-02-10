#!/usr/bin/env python3
"""
列出飞书日程
用法: python3 list.py [days]
"""

import sys
import os
import time
import requests
from datetime import datetime

# 获取当前脚本所在目录并添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from feishu_client import FeishuAssistant

def list_events(days=7):
    """列出未来几天的日程"""
    assistant = FeishuAssistant()
    
    if not assistant.app_id:
        print("❌ 未配置，请先运行: python3 feishu_client.py")
        return False
    
    try:
        token = assistant._get_tenant_access_token()
        
        # 获取日历信息
        calendars = assistant.list_calendars()
        if calendars.get("code") != 0:
            print(f"❌ 获取日历失败")
            return False
            
        calendar_list = calendars.get("data", {}).get("calendar_list", [])
        if not calendar_list:
            print("❌ 没有找到日历")
            return False
            
        calendar_id = calendar_list[0].get("calendar_id")
        calendar_name = calendar_list[0].get("summary", "默认日历")
        
        print(f"📅 日历: {calendar_name}")
        print(f"📆 未来 {days} 天日程:")
        print("-" * 70)
        
        # 获取时间范围
        now = int(time.time())
        future = now + (days * 24 * 3600)
        
        # 获取日程列表
        url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events?start_time={now}&end_time={future}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        response = requests.get(url, headers=headers)
        resp_json = response.json()
        
        if resp_json.get("code") != 0:
            print(f"❌ 获取日程失败: {resp_json.get('msg', '未知错误')}")
            return False
            
        events = resp_json.get("data", {}).get("event_list", [])
        
        if not events:
            print("📭 暂无日程")
            return True
            
        # 按时间排序
        events.sort(key=lambda x: int(x.get("start_time", {}).get("timestamp", 0)))
        
        for i, event in enumerate(events, 1):
            event_id = event.get("event_id")
            summary = event.get("summary", "无标题")
            start_ts = int(event.get("start_time", {}).get("timestamp", 0))
            end_ts = int(event.get("end_time", {}).get("timestamp", 0))
            description = event.get("description", "")
            
            start_dt = datetime.fromtimestamp(start_ts)
            end_dt = datetime.fromtimestamp(end_ts)
            
            # 标记周末
            is_weekend = "🏖️ " if start_dt.weekday() >= 5 else ""
            
            print(f"{is_weekend}{i:2d}. 📝 {summary}")
            print(f"    📅 {start_dt.strftime('%m月%d日 %H:%M')} - {end_dt.strftime('%H:%M')}")
            print(f"    🆔 {event_id}")
            if description:
                print(f"    📋 {description[:50]}{'...' if len(description) > 50 else ''}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    success = list_events(days)
    sys.exit(0 if success else 1)