import argparse
import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from feishu_card_client import FeishuCard

def send_message(title, content, receive_id, receive_id_type, config=None):
    client = FeishuCard()
    
    # 如果没有指定 receive_id，尝试使用配置中的 open_id
    if not receive_id:
        receive_id = client.open_id
        if not receive_id:
            print("Error: No receive_id provided and no default open_id found in config.")
            return

    # 处理命令行输入的换行符转义问题
    # 在 shell 中输入的 "\n" 通常会被作为字面量 "\\n" 传入，需要还原为真正的换行符
    if content:
        content = content.replace("\\n", "\n")

    # 发送卡片
    result = client.send_card(title, content, receive_id, receive_id_type, config)
    
    if result and result.get("code") == 0:
        print(f"✅ 卡片发送成功")
        print(f"Message ID: {result.get('data', {}).get('message_id')}")
    else:
        print(f"❌ 发送失败: {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="发送飞书富文本卡片消息")
    parser.add_argument("title", help="卡片标题")
    parser.add_argument("content", help="卡片内容 (Markdown)")
    parser.add_argument("--receive_id", help="接收者 ID (默认使用配置中的 OpenID)")
    parser.add_argument("--receive_id_type", help="接收者 ID 类型 (open_id, user_id, union_id, email, chat_id)", default="open_id")
    parser.add_argument("--wide_screen_mode", help="开启宽屏模式", action="store_true")
    
    args = parser.parse_args()
    
    card_config = {}
    if args.wide_screen_mode:
        card_config["wide_screen_mode"] = True
    
    send_message(args.title, args.content, args.receive_id, args.receive_id_type, card_config)
