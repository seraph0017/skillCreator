import argparse
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from feishu_drive_client import FeishuDrive

def delete_file(file_token, type="file"):
    client = FeishuDrive()
    if not client.app_id:
        print("❌ 未配置，请先运行: python3 feishu_drive_client.py")
        return

    # 尝试自动判断类型或尝试多种类型
    # 如果用户没有指定 type，且 type 默认为 "file"，可能会失败
    # 如果是 folder，必须指定 type="folder"
    # 我们可以尝试先 delete as file，如果失败且报错 not found，再尝试 folder?
    # 不建议自动尝试，比较危险。
    
    result = client.delete_file(file_token, type)
    
    if result and result.get("code") == 0:
        print(f"🗑️ 删除成功: {file_token}")
    else:
        # 尝试提供更友好的错误提示
        msg = result.get("msg", "")
        if "not found" in msg and type == "file":
             print(f"❌ 删除失败: 找不到文件。如果是其他类型(folder/docx/sheet/bitable)，请添加参数 --type <type> (如 --type folder)")
        else:
             print(f"❌ 删除失败: {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="删除飞书云空间文件")
    parser.add_argument("token", help="文件/文件夹 Token")
    parser.add_argument("--type", help="文件类型 (file/docx/sheet/folder)", default="file")
    
    args = parser.parse_args()
    
    delete_file(args.token, args.type)
