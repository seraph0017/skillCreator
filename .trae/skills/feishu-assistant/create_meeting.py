#!/usr/bin/env python3
"""
飞书日程创建工具 - 通用版本
用于快速创建飞书日程事件
"""

import sys
import os
import time
import argparse
from datetime import datetime, timedelta

# 添加feishu-assistant技能路径
sys.path.append('/Users/xunan/.openclaw/workspace/skills/feishu-assistant')

from feishu_client import FeishuAssistant

def create_meeting(summary, day_offset=1, hour=9, minute=0, duration=60, description=None):
    """
    创建飞书日程
    
    Args:
        summary: 会议主题
        day_offset: 从今天起的偏移天数（默认1=明天）
        hour: 小时（24小时制）
        minute: 分钟
        duration: 会议时长（分钟，默认60）
        description: 会议描述（可选）
    """
    # 创建助手实例
    assistant = FeishuAssistant()
    
    # 检查是否已配置
    if not assistant.app_id:
        print("❌ 飞书助手未配置，请先运行初始化")
        print("使用方法：python3 feishu_client.py")
        return False
    
    # 计算会议时间
    target_day = datetime.now() + timedelta(days=day_offset)
    target_time = target_day.replace(hour=hour, minute=minute, second=0, microsecond=0)
    start_time = int(target_time.timestamp())
    end_time = start_time + (duration * 60)  # 转换为秒
    
    # 格式化显示时间
    time_str = target_time.strftime('%Y-%m-%d %H:%M')
    end_time_str = (target_time + timedelta(minutes=duration)).strftime('%H:%M')
    
    print(f"📅 创建日程：{time_str} - {end_time_str}")
    print(f"📝 会议主题：{summary}")
    print(f"⏰ 会议时长：{duration}分钟")
    
    # 创建日程
    try:
        event_id = assistant.create_event(
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            attendees=None,  # 默认只包含自己
            description=description
        )
        
        if event_id:
            print(f"✅ 日程创建成功！事件ID: {event_id}")
            print("📱 请检查您的飞书应用，日程已添加到您的日历中")
            return True
        else:
            print("❌ 日程创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 创建日程时出错: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='飞书日程创建工具')
    parser.add_argument('summary', help='会议主题')
    parser.add_argument('--day', type=int, default=1, help='从今天起的偏移天数（默认1=明天）')
    parser.add_argument('--hour', type=int, default=9, help='小时（24小时制，默认9）')
    parser.add_argument('--minute', type=int, default=0, help='分钟（默认0）')
    parser.add_argument('--duration', type=int, default=60, help='会议时长（分钟，默认60）')
    parser.add_argument('--desc', help='会议描述')
    
    args = parser.parse_args()
    
    success = create_meeting(
        summary=args.summary,
        day_offset=args.day,
        hour=args.hour,
        minute=args.minute,
        duration=args.duration,
        description=args.desc
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        print("飞书日程创建工具")
        print("使用方法:")
        print("  python3 create_meeting.py '会议主题' [选项]")
        print("")
        print("示例:")
        print("  python3 create_meeting.py '团队会议'")
        print("  python3 create_meeting.py '和客户通话' --hour 14 --duration 30")
        print("  python3 create_meeting.py '项目评审' --day 0 --hour 16 --desc '本周项目进展评审'")
        print("")
        print("选项:")
        print("  --day DAY        偏移天数（默认1=明天）")
        print("  --hour HOUR      小时（24小时制，默认9）")
        print("  --minute MINUTE  分钟（默认0）")
        print("  --duration MIN   会议时长（分钟，默认60）")
        print("  --desc DESC      会议描述")
    else:
        main()