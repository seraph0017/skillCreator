import argparse
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from feishu_drive_client import FeishuDrive

def modify_file(file_token, name=None, folder_token=None, type="file"):
    client = FeishuDrive()
    if not client.app_id:
        print("❌ 未配置，请先运行: python3 feishu_drive_client.py")
        return

    if name:
        print(f"Renaming to '{name}'...")
        result = client.rename_file(file_token, name, type)
        if result and result.get("code") == 0:
            print(f"✅ 重命名成功")
        else:
            print(f"❌ 重命名失败: {result}")

    if folder_token:
        print(f"Moving to folder '{folder_token}'...")
        result = client.move_file(file_token, folder_token, type)
        if result and result.get("code") == 0:
            print(f"✅ 移动成功")
            # 移动成功后通常会返回新的 task_id (异步) 或直接成功
            # v1 move 接口是同步还是异步？文档说是同步返回结果
        else:
            print(f"❌ 移动失败: {result}")

    if not name and not folder_token:
        print("⚠️ 未指定任何修改操作 (使用 --name 或 --folder_token)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="修改飞书云空间文件 (重命名/移动)")
    parser.add_argument("token", help="文件/文件夹 Token")
    parser.add_argument("--name", help="新名称", default=None)
    parser.add_argument("--folder_token", help="移动到的目标文件夹 Token", default=None)
    parser.add_argument("--type", help="文件类型 (file/docx/sheet/folder)", default="file")
    
    args = parser.parse_args()
    
    modify_file(args.token, args.name, args.folder_token, args.type)
