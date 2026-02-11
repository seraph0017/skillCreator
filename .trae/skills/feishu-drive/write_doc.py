import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from feishu_drive_client import FeishuDrive

def write_content(doc_token, content):
    client = FeishuDrive()
    result = client.add_docx_content(doc_token, content)
    
    if result and result.get("code") == 0:
        print(f"✅ 内容写入成功")
        # print(f"Response: {result}")
    else:
        print(f"❌ 写入失败: {result}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 write_doc.py DOC_TOKEN CONTENT")
        sys.exit(1)
        
    doc_token = sys.argv[1]
    content = sys.argv[2]
    
    write_content(doc_token, content)
