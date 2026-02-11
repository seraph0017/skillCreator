import argparse
import sys
import os

# 获取当前脚本所在目录并添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from feishu_drive_client import FeishuDrive

def create_resource(type, name, parent_token=""):
    client = FeishuDrive()
    if not client.app_id:
        print("❌ 未配置，请先运行: python3 feishu_drive_client.py")
        return

    result = None
    if type == "doc":
        result = client.create_doc(name, parent_token)
    elif type == "sheet":
        result = client.create_sheet(name, parent_token)
    elif type == "bitable":
        result = client.create_bitable(name, parent_token)
    elif type == "folder":
        result = client.create_folder(name, parent_token)
    else:
        print(f"Unknown type: {type}")
        return

    if result and result.get("code") == 0:
        # 统一处理返回结果
        data = result.get("data", {})
        
        # Docx: data: { document: { document_id, url, ... } }
        # Sheet: data: { spreadsheet: { spreadsheet_token, url, ... } }
        # Bitable: data: { app: { app_token, url, ... } }
        # Folder: data: { token, url, ... }
        
        token = ""
        url = ""
        
        if type == "doc": # Docx
            doc = data.get("document", {})
            token = doc.get("document_id")
            url = doc.get("url")
            # 如果 API 返回的 url 是 None，我们尝试手动构造
            if not url and token:
                url = f"https://feishu.cn/docx/{token}"
        elif type == "sheet":
            sheet = data.get("spreadsheet", {})
            token = sheet.get("spreadsheet_token")
            url = sheet.get("url")
            if not url and token:
                url = f"https://feishu.cn/sheets/{token}"
        elif type == "bitable":
            app = data.get("app", {})
            token = app.get("app_token")
            url = app.get("url")
            if not url and token:
                url = f"https://feishu.cn/base/{token}"
        elif type == "folder":
            token = data.get("token")
            url = data.get("url")
            if not url and token:
                url = f"https://feishu.cn/drive/folder/{token}"
        else:
            # Fallback
            token = data.get("token") or data.get("file", {}).get("token")
            url = data.get("url") or data.get("file", {}).get("url")
            
        print(f"✅ 创建成功: {name}")
        print(f"🔗 URL: {url}")
        print(f"🔑 Token: {token}")
    else:
        print(f"❌ 创建失败: {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="创建飞书云文档资源")
    parser.add_argument("type", choices=["doc", "sheet", "bitable", "folder"], help="资源类型")
    parser.add_argument("name", help="资源名称")
    parser.add_argument("--folder_token", help="父文件夹 Token", default="")
    
    args = parser.parse_args()
    
    create_resource(args.type, args.name, args.folder_token)
