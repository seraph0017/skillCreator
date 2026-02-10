#!/usr/bin/env python3
"""
创建飞书日程
用法: python3 create.py "会议主题" [YYYY-MM-DD] [HH:MM] [duration_minutes] ["描述"]
"""

import sys
import os
import time
from datetime import datetime

# 获取当前脚本所在目录并添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from feishu_client import FeishuAssistant

def create_event(summary, date_str=None, time_str=None, duration=60, description=None):
    """创建日程事件"""
    assistant = FeishuAssistant()
    
    if not assistant.app_id:
        print("❌ 未配置，请先运行: python3 feishu_client.py")
        return False
    
    # 解析时间
    if date_str and time_str:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    else:
        dt = datetime.now()
        if date_str:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
    
    start_time = int(dt.timestamp())
    end_time = start_time + (duration * 60)
    
    try:
        event_id = assistant.create_event(
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            description=description or f"日程: {summary}"
        )
        
        if event_id:
            print(f"✅ 创建成功: {event_id}")
            print(f"📅 {dt.strftime('%Y-%m-%d %H:%M')} - {(datetime.fromtimestamp(end_time)).strftime('%H:%M')}")
            return True
        else:
            print("❌ 创建失败")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 create.py \"会议主题\" [YYYY-MM-DD] [HH:MM] [duration_minutes] [\"描述\"]")
        print("示例: python3 create.py \"团队会议\" 2026-02-11 09:00 60 \"讨论项目进展\"")
        sys.exit(1)
    
    summary = sys.argv[1]
    date_str = sys.argv[2] if len(sys.argv) > 2 else None
    time_str = sys.argv[3] if len(sys.argv) > 3 else None
    duration = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    description = sys.argv[5] if len(sys.argv) > 5 else None
    
    success = create_event(summary, date_str, time_str, duration, description)
    sys.exit(0 if success else 1)