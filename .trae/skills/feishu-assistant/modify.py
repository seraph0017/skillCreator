#!/usr/bin/env python3
"""
修改飞书日程
用法: python3 modify.py <event_id> --summary "新主题" --time "YYYY-MM-DD HH:MM" --duration 60 --desc "新描述"
"""

import sys
import os
import time
import requests
from datetime import datetime, timedelta

# 获取当前脚本所在目录并添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from feishu_client import FeishuAssistant

def modify_event(event_id, summary=None, date_time=None, duration=None, description=None):
    """修改日程事件"""
    assistant = FeishuAssistant()
    
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
        
        # 先获取当前日程信息
        get_url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events/{event_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        get_resp = requests.get(get_url, headers=headers)
        current_event = get_resp.json()
        
        if current_event.get("code") != 0:
            print(f"❌ 获取当前日程失败: {current_event.get('msg', '未知错误')}")
            return False
        
        event_data = current_event.get("data", {}).get("event", {})
        
        # 构建更新数据
        update_data = {}
        
        if summary:
            update_data["summary"] = summary
        
        if description:
            update_data["description"] = description
        
        if date_time:
            dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
            start_time = int(dt.timestamp())
            duration_min = duration or 60
            end_time = start_time + (duration_min * 60)
            
            update_data["start_time"] = {"timestamp": str(start_time)}
            update_data["end_time"] = {"timestamp": str(end_time)}
        elif duration:
            # 只修改时长，保持原时间
            start_ts = int(event_data.get("start_time", {}).get("timestamp", 0))
            end_time = start_ts + (duration * 60)
            update_data["end_time"] = {"timestamp": str(end_time)}
        
        # 更新日程
        update_url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events/{event_id}"
        response = requests.patch(update_url, headers=headers, json=update_data)
        resp_json = response.json()
        
        if resp_json.get("code") != 0:
            print(f"❌ 修改失败: {resp_json.get('msg', '未知错误')}")
            return False
            
        print(f"✅ 修改成功: {event_id}")
        
        # 显示修改后的信息
        if summary:
            print(f"📝 主题: {summary}")
        if date_time:
            dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
            duration_min = duration or 60
            end_dt = dt + timedelta(minutes=duration_min)
            print(f"📅 时间: {dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%H:%M')}")
        elif duration:
            print(f"⏰ 时长: {duration}分钟")
        if description:
            print(f"📋 描述: {description}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def print_usage():
    print("用法: python3 modify.py <event_id> [选项]")
    print("选项:")
    print("  --summary TEXT     新的会议主题")
    print("  --time DATETIME    新的时间 (格式: YYYY-MM-DD HH:MM)")
    print("  --duration MIN     新的会议时长 (分钟)")
    print("  --desc TEXT        新的会议描述")
    print()
    print("示例:")
    print("  python3 modify.py f905157c-962b-426f-bf03-65a7d4bbe8d3_0 --summary \"新主题\"")
    print("  python3 modify.py EVENT_ID --time \"2026-02-11 14:00\" --duration 90")
    print("  python3 modify.py EVENT_ID --desc \"新的会议描述\"")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    event_id = sys.argv[1]
    
    # 解析参数
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("event_id")
    parser.add_argument("--summary", help="新的会议主题")
    parser.add_argument("--time", help="新的时间 (格式: YYYY-MM-DD HH:MM)")
    parser.add_argument("--duration", type=int, help="新的会议时长 (分钟)")
    parser.add_argument("--desc", help="新的会议描述")
    
    args = parser.parse_args()
    
    if not any([args.summary, args.time, args.duration, args.desc]):
        print("❌ 请至少指定一个要修改的选项")
        print_usage()
        sys.exit(1)
    
    success = modify_event(event_id, args.summary, args.time, args.duration, args.desc)
    sys.exit(0 if success else 1)