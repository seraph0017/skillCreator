import argparse
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from feishu_drive_client import FeishuDrive

def upload_file(file_path, parent_token=""):
    client = FeishuDrive()
    if not client.app_id:
        print("❌ 未配置，请先运行: python3 feishu_drive_client.py")
        return

    print(f"Uploading {file_path}...")
    result = client.upload_file(file_path, parent_token)
    
    if result and result.get("code") == 0:
        data = result.get("data", {})
        token = data.get("file_token")
        url = data.get("url")
        print(f"✅ 上传成功")
        print(f"🔗 URL: {url}")
        print(f"🔑 Token: {token}")
    else:
        print(f"❌ 上传失败: {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="上传文件到飞书云空间")
    parser.add_argument("file_path", help="本地文件路径")
    parser.add_argument("--parent_token", help="父文件夹 Token", default="")
    
    args = parser.parse_args()
    
    upload_file(args.file_path, args.parent_token)
