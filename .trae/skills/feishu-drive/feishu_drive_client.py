import json
import os
import time
import requests
import mimetypes

CONFIG_FILE = os.path.expanduser("~/.feishu_drive_config.json")
CALENDAR_CONFIG_FILE = os.path.expanduser("~/.feishu_calendar_config.json")

class FeishuDrive:
    def __init__(self):
        self.config = self._load_config()
        self.app_id = self.config.get("app_id")
        self.app_secret = self.config.get("app_secret")
        self.open_id = self.config.get("open_id")
        self.tenant_access_token = None
        self.token_expire_time = 0

    def _load_config(self):
        # 优先读取 drive 配置
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        
        # 如果没有 drive 配置，尝试迁移 calendar 配置
        if os.path.exists(CALENDAR_CONFIG_FILE):
            try:
                print(f"Detecting existing configuration from {CALENDAR_CONFIG_FILE}...")
                with open(CALENDAR_CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    # 自动保存一份到 drive 配置
                    self._save_config_to_file(config)
                    return config
            except Exception:
                pass
                
        return {}

    def _save_config(self, config):
        self._save_config_to_file(config)
        self.config = config
        self.app_id = config.get("app_id")
        self.app_secret = config.get("app_secret")
        self.open_id = config.get("open_id")
        
    def _save_config_to_file(self, config):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

    def initialize(self):
        """初始化配置"""
        print("Initializing Feishu Drive...")
        app_id = input("Enter App ID: ").strip()
        app_secret = input("Enter App Secret: ").strip()
        phone = input("Enter Phone Number: ").strip()

        try:
            token = self._get_tenant_access_token(app_id, app_secret)
            # 这里简化处理，如果不校验 open_id 也可以，但为了保持一致性还是获取一下
            # 如果需要 open_id，可以复用 calendar/task 的逻辑
            # 这里为了简单，先假设能获取 token 就是成功
            
            config = {
                "app_id": app_id,
                "app_secret": app_secret,
                "phone": phone
            }
            # 尝试获取 open_id
            try:
                open_id = self._get_user_id_by_mobile(token, phone)
                if open_id:
                    config["open_id"] = open_id
            except:
                pass

            self._save_config(config)
            print("Initialization successful!")
            return True
        except Exception as e:
            print(f"Initialization failed: {e}")
            return False

    def _get_tenant_access_token(self, app_id=None, app_secret=None):
        if self.tenant_access_token and time.time() < self.token_expire_time:
            return self.tenant_access_token

        app_id = app_id or self.app_id
        app_secret = app_secret or self.app_secret
        
        if not app_id or not app_secret:
            raise ValueError("App ID and App Secret are required.")

        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        payload = {
            "app_id": app_id,
            "app_secret": app_secret
        }
        response = requests.post(url, headers=headers, json=payload)
        resp_json = response.json()
        
        if resp_json.get("code") != 0:
            raise Exception(f"Get token failed: {resp_json}")
            
        self.tenant_access_token = resp_json.get("tenant_access_token")
        self.token_expire_time = time.time() + resp_json.get("expire", 7200) - 60
        return self.tenant_access_token

    def _get_user_id_by_mobile(self, token, mobile):
        url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id?user_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {"mobiles": [mobile]}
        response = requests.post(url, headers=headers, json=payload)
        resp_json = response.json()
        if resp_json.get("code") == 0:
            user_list = resp_json.get("data", {}).get("user_list", [])
            if user_list:
                return user_list[0].get("user_id")
        return None

    # --- Drive API ---

    def create_folder(self, name, parent_token=""):
        """创建文件夹"""
        return self._create_node(name, "folder", parent_token)

    def create_doc(self, name, parent_token=""):
        """创建文档 (docx)"""
        return self._create_node(name, "docx", parent_token)

    def create_sheet(self, name, parent_token=""):
        """创建电子表格"""
        return self._create_node(name, "sheet", parent_token)

    def create_bitable(self, name, parent_token=""):
        """创建多维表格"""
        return self._create_node(name, "bitable", parent_token)

    def _create_node(self, name, type, parent_token=""):
        """
        通用创建节点
        type: folder, docx, sheet, bitable
        """
        if not self.app_id:
            print("Configuration missing.")
            return

        token = self._get_tenant_access_token()
        # 创建文件和创建文件夹接口 URL 不同
        # 创建文件夹: POST /drive/v1/files/create_folder
        # 创建文件: POST /drive/v1/files (文档说是这个，但实际上可能是 /open-apis/drive/v1/files)
        
        # 修正: 创建文件的接口通常是 /drive/v1/files，但需要检查是否是 create_folder
        # 实际上 Drive API V1 中创建文件是 POST /drive/v1/files
        # 但是之前测试 docx 返回 404 page not found，说明 URL 不对或者环境问题
        # 查阅最新文档: 
        # 创建文件夹: POST https://open.feishu.cn/open-apis/drive/v1/files/create_folder
        # 创建导入任务: POST https://open.feishu.cn/open-apis/drive/v1/import_tasks
        # 实际上直接创建空文档可能需要用 Explorer API 或 Space API?
        # 重新确认 Drive V1 Create File 接口
        # Drive V1 确实有一个 POST /open-apis/drive/v1/files 接口用于创建文件，但可能需要 file_content? 不，那是 upload
        # 正确的创建空文档接口:
        # 飞书云文档 2.0 之后，推荐使用 Space 节点管理
        # 尝试使用 POST https://open.feishu.cn/open-apis/drive/v1/files
        # 如果这个 404，可能是 path 不对。
        # 再次核对文档: POST /open-apis/drive/v1/files 确实存在。
        # 也许是因为 type 参数的值不对? type: docx, sheet, bitable, mindnote
        # 之前的 payload: {"name": ..., "folder_token": ..., "type": "docx"}
        # 
        # 另一种可能性：URL 末尾有斜杠问题？
        
        url = "https://open.feishu.cn/open-apis/drive/v1/files/create_folder" if type == "folder" else "https://open.feishu.cn/open-apis/drive/v1/files"
        
        # 尝试去掉 create_folder 的特殊判断，因为 create_folder 是专属接口
        # 但 create doc 用的 url 返回 404，说明 https://open.feishu.cn/open-apis/drive/v1/files 这个 endpoint 不存在或方法不对?
        # 
        # 修正：根据经验，创建云文档有时用 POST /open-apis/docx/v1/documents (Docx 专属)
        # 或者 POST /open-apis/sheets/v3/spreadsheets (Sheets 专属)
        # Drive V1 的 files 接口可能已经废弃或变更?
        # 
        # 让我们尝试使用 Drive Explorer V2 (旧版) 或各个业务线的 V1/V2 接口
        # 
        # 方案 B: 使用各个业务线的创建接口
        # Docx: POST https://open.feishu.cn/open-apis/docx/v1/documents
        # Sheet: POST https://open.feishu.cn/open-apis/sheets/v3/spreadsheets
        # Bitable: POST https://open.feishu.cn/open-apis/bitable/v1/apps
        
        # 让我们先试试 Docx 的专用接口
        if type == "docx":
            url = "https://open.feishu.cn/open-apis/docx/v1/documents"
            payload = {
                "folder_token": parent_token if parent_token else "",
                "title": name # Docx 使用 title 而不是 name
            }
        elif type == "sheet":
             # Sheets V3
             url = "https://open.feishu.cn/open-apis/sheets/v3/spreadsheets"
             payload = {
                 "title": name,
                 "folder_token": parent_token if parent_token else ""
             }
        elif type == "bitable":
             # Bitable V1
             url = "https://open.feishu.cn/open-apis/bitable/v1/apps"
             payload = {
                 "name": name,
                 "folder_token": parent_token if parent_token else ""
             }
        elif type == "folder":
             url = "https://open.feishu.cn/open-apis/drive/v1/files/create_folder"
             payload = {
                "name": name,
                "folder_token": parent_token if parent_token else ""
            }
        else:
             # Fallback to drive v1 files (if it works for other types)
             url = "https://open.feishu.cn/open-apis/drive/v1/files"
             payload = {
                "name": name,
                "folder_token": parent_token if parent_token else "",
                "type": type
            }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # Log request for debugging
        # print(f"DEBUG: POST {url} payload={payload}")
        
        response = requests.post(url, headers=headers, json=payload)
        try:
            return response.json()
        except Exception as e:
            print(f"Error decoding JSON: {e}")
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text}")
            return {"code": -1, "msg": f"JSON Decode Error: {str(e)}", "raw": response.text}

    def upload_file(self, file_path, parent_token=""):
        """上传文件"""
        if not self.app_id:
            print("Configuration missing.")
            return

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        token = self._get_tenant_access_token()
        url = "https://open.feishu.cn/open-apis/drive/v1/files/upload_all"
        
        headers = {
            "Authorization": f"Bearer {token}",
        }
        
        # multipart/form-data
        data = {
            "file_name": file_name,
            "parent_type": "explorer",
            "parent_node": parent_token if parent_token else "", # 根目录需留空或指定
            "size": str(file_size)
        }
        
        files = {
            "file": open(file_path, "rb")
        }
        
        response = requests.post(url, headers=headers, data=data, files=files)
        return response.json()

    def list_files(self, folder_token=""):
        """列出文件"""
        if not self.app_id:
            print("Configuration missing.")
            return

        token = self._get_tenant_access_token()
        url = "https://open.feishu.cn/open-apis/drive/v1/files"
        
        headers = {
            "Authorization": f"Bearer {token}",
        }
        
        params = {
            "folder_token": folder_token if folder_token else ""
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def delete_file(self, file_token, type="file"):
        """删除文件"""
        if not self.app_id:
            print("Configuration missing.")
            return

        token = self._get_tenant_access_token()
        url = f"https://open.feishu.cn/open-apis/drive/v1/files/{file_token}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        params = {
            "type": type # file, docx, sheet, folder 等
        }
        
        response = requests.delete(url, headers=headers, params=params)
        return response.json()

    def rename_file(self, file_token, new_name, type="file"):
        """重命名文件"""
        if not self.app_id:
            print("Configuration missing.")
            return
            
        # Drive V1 并没有直接的 rename 接口，通常是通过 update 接口或者 copy/move 接口?
        # 查阅文档: Drive V1 Update File 接口可以修改 name
        # PATCH /open-apis/drive/v1/files/:file_token
        
        token = self._get_tenant_access_token()
        url = f"https://open.feishu.cn/open-apis/drive/v1/files/{file_token}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # 某些类型可能需要特定接口，但 Drive V1 通用接口应该支持基础类型
        # 注意：folder 的重命名也是这个接口吗？
        # 这是一个通用接口，支持 folder, file, docx 等
        
        payload = {
            "name": new_name,
            "type": type
        }
        
        response = requests.patch(url, headers=headers, json=payload)
        return response.json()

    def move_file(self, file_token, folder_token, type="file"):
        """移动文件"""
        if not self.app_id:
            print("Configuration missing.")
            return
            
        # POST /open-apis/drive/v1/files/:file_token/move
        token = self._get_tenant_access_token()
        url = f"https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/move"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        payload = {
            "type": type,
            "folder_token": folder_token
        }
        
        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    def add_docx_content(self, document_id, content):
        """
        向 Docx 文档末尾追加文本内容
        :param document_id: 文档 Token
        :param content: 文本内容
        """
        if not self.app_id:
            print("Configuration missing.")
            return
            
        token = self._get_tenant_access_token()
        # 1. 获取文档的基本信息，确认文档存在 (可选)
        
        # 2. 向文档添加块 (Block)
        # POST /open-apis/docx/v1/documents/:document_id/blocks/:block_id/children
        # 如果 block_id 使用 document_id，通常表示添加到文档末尾
        
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # 构造文本 Block
        # block_type 2 代表 Text
        payload = {
            "children": [
                {
                    "block_type": 2, 
                    "text": {
                        "elements": [
                            {
                                "text_run": {
                                    "content": content
                                }
                            }
                        ]
                    }
                }
            ],
            "index": -1 # -1 表示添加到末尾
        }
        
        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    def add_member_permission(self, token, member_id, member_type="openid", role="full_access", type="file"):
        """
        增加协作者权限
        :param token: 文件/文档 Token
        :param member_id: 用户 ID (open_id, user_id, union_id, email, mobile)
        :param member_type: 用户类型 (openid, userid, unionid, email, mobile, chatid, departmentid)
        :param role: 权限角色 (view, edit, full_access)
        :param type: 资源类型 (file, docx, sheet, bitable, folder)
        """
        if not self.app_id:
            print("Configuration missing.")
            return

        access_token = self._get_tenant_access_token()
        
        # Drive V1 Permission API: POST /open-apis/drive/v1/permissions/:token/members
        # 注意：不同类型的资源可能需要不同的 type 参数，但 V1 Permission 接口通常是通用的，通过 type 参数指定资源类型
        
        url = f"https://open.feishu.cn/open-apis/drive/v1/permissions/{token}/members"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        payload = {
            "member_type": member_type,
            "member_id": member_id,
            "perm": role
        }
        
        response = requests.post(url, headers=headers, json=payload, params={"type": type})
        return response.json()

if __name__ == "__main__":
    client = FeishuDrive()
    if not client.app_id:
        client.initialize()
    else:
        print("Feishu Drive is configured.")
