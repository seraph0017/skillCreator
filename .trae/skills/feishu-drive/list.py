import argparse
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from feishu_drive_client import FeishuDrive

def list_files(folder_token=""):
    client = FeishuDrive()
    if not client.app_id:
        print("❌ 未配置，请先运行: python3 feishu_drive_client.py")
        return

    result = client.list_files(folder_token)
    
    if result and result.get("code") == 0:
        files = result.get("data", {}).get("files", [])
        if not files:
            print("📭 文件夹为空")
            return
            
        print(f"📋 找到 {len(files)} 个文件:")
        for f in files:
            name = f.get("name")
            token = f.get("token")
            type = f.get("type")
            print(f"[{type}] {name} (Token: {token})")
    else:
        print(f"❌ 获取列表失败: {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="列出飞书云空间文件")
    parser.add_argument("folder_token", nargs="?", default="", help="文件夹 Token (默认根目录)")
    
    args = parser.parse_args()
    
    list_files(args.folder_token)
