import argparse
import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from feishu_card_client import FeishuCard

def preview_card_json(title, content, config=None):
    card_content = {
        "schema": "2.0",
        "header": {
            "title": {
                "content": title,
                "tag": "plain_text"
            },
            "template": "blue"
        },
        "body": {
            "elements": [
                {
                    "tag": "markdown",
                    "content": content
                }
            ]
        }
    }
    
    if config:
        card_content["config"] = config
        
    print(json.dumps(card_content, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="预览飞书富文本卡片 JSON 结构")
    parser.add_argument("title", help="卡片标题")
    parser.add_argument("content", help="卡片内容 (Markdown)")
    parser.add_argument("--wide_screen_mode", help="开启宽屏模式", action="store_true")
    
    args = parser.parse_args()
    
    card_config = {}
    if args.wide_screen_mode:
        card_config["wide_screen_mode"] = True
    
    preview_card_json(args.title, args.content, card_config)
