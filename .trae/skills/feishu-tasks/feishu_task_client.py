import json
import os
import time
import requests

CONFIG_FILE = os.path.expanduser("~/.feishu_task_config.json")

class FeishuTask:
    def __init__(self):
        self.config = self._load_config()
        self.app_id = self.config.get("app_id")
        self.app_secret = self.config.get("app_secret")
        self.open_id = self.config.get("open_id")
        self.tenant_access_token = None
        self.token_expire_time = 0

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_config(self, config):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        self.config = config
        self.app_id = config.get("app_id")
        self.app_secret = config.get("app_secret")
        self.open_id = config.get("open_id")

    def initialize(self):
        """
        初始化配置：输入 App ID, App Secret, 手机号
        """
        print("Initializing Feishu Task...")
        app_id = input("Enter App ID: ").strip()
        app_secret = input("Enter App Secret: ").strip()
        phone = input("Enter Phone Number: ").strip()

        # 验证并获取 open_id
        try:
            token = self._get_tenant_access_token(app_id, app_secret)
            open_id = self._get_user_id_by_mobile(token, phone)
            
            if not open_id:
                print("Failed to get Open ID. Please check the phone number.")
                return False

            config = {
                "app_id": app_id,
                "app_secret": app_secret,
                "phone": phone,
                "open_id": open_id
            }
            self._save_config(config)
            print(f"Initialization successful! Open ID: {open_id}")
            return True
        except Exception as e:
            print(f"Initialization failed: {e}")
            return False

    def _get_tenant_access_token(self, app_id=None, app_secret=None):
        # 如果有缓存且未过期，直接返回
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
        self.token_expire_time = time.time() + resp_json.get("expire", 7200) - 60 # 提前60秒过期
        return self.tenant_access_token

    def _get_user_id_by_mobile(self, token, mobile):
        url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id?user_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "mobiles": [mobile]
        }
        response = requests.post(url, headers=headers, json=payload)
        resp_json = response.json()
        
        if resp_json.get("code") != 0:
            raise Exception(f"Get user id failed: {resp_json}")
            
        user_list = resp_json.get("data", {}).get("user_list", [])
        if user_list and user_list[0].get("user_id"):
            return user_list[0].get("user_id")
        return None

    def create_task(self, summary, description=None, due_timestamp=None, members=None):
        """
        创建任务
        :param summary: 任务标题
        :param description: 任务描述
        :param due_timestamp: 截止时间戳（毫秒级 int 或 str）
        :param members: 成员列表 [{"id": "ou_xxx", "type": "user"}]
        """
        if not self.app_id:
            print("Configuration missing. Please run initialize() first.")
            return

        token = self._get_tenant_access_token()
        url = "https://open.feishu.cn/open-apis/task/v2/tasks"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        payload = {
            "summary": summary
        }
        
        if description:
            payload["description"] = description
            
        if due_timestamp:
            payload["due"] = {
                "timestamp": str(due_timestamp),
                "is_all_day": False
            }
            
        # 如果没有指定成员，默认添加自己为负责人
        if not members:
            members = [{"id": self.open_id, "type": "user", "role": "assignee"}]
        
        if members:
            payload["members"] = members

        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    def list_tasks(self, page_size=20, page_token=None, task_list_type=None):
        """
        列出任务 (默认列出当前用户负责的任务)
        :param task_list_type: 任务类型，如 "created", "assigned" 等
        """
        if not self.app_id:
            print("Configuration missing. Please run initialize() first.")
            return

        token = self._get_tenant_access_token()
        url = "https://open.feishu.cn/open-apis/task/v2/tasks"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        params = {
            "page_size": page_size,
            "user_id_type": "open_id"
        }
        if page_token:
            params["page_token"] = page_token
            
        if task_list_type:
            params["type"] = task_list_type
            
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def get_task(self, task_guid):
        """
        获取任务详情
        """
        if not self.app_id:
            return
            
        token = self._get_tenant_access_token()
        url = f"https://open.feishu.cn/open-apis/task/v2/tasks/{task_guid}"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def complete_task(self, task_guid):
        """
        完成任务
        """
        if not self.app_id:
            return
            
        token = self._get_tenant_access_token()
        url = f"https://open.feishu.cn/open-apis/task/v2/tasks/{task_guid}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # completed_at 设为当前时间戳(毫秒)
        current_ts = int(time.time() * 1000)
        payload = {
            "task": {
                "completed_at": str(current_ts)
            },
            "update_fields": ["completed_at"]
        }
        
        response = requests.patch(url, headers=headers, json=payload)
        return response.json()

    def update_task(self, task_guid, summary=None, description=None, due_timestamp=None):
        """
        更新任务信息
        """
        if not self.app_id:
            return
            
        token = self._get_tenant_access_token()
        url = f"https://open.feishu.cn/open-apis/task/v2/tasks/{task_guid}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        task_data = {}
        update_fields = []
        
        if summary:
            task_data["summary"] = summary
            update_fields.append("summary")
            
        if description:
            task_data["description"] = description
            update_fields.append("description")
            
        if due_timestamp:
            task_data["due"] = {
                "timestamp": str(due_timestamp),
                "is_all_day": False
            }
            update_fields.append("due")
            
        if not update_fields:
            return None
            
        payload = {
            "task": task_data,
            "update_fields": update_fields
        }
        
        response = requests.patch(url, headers=headers, json=payload)
        return response.json()


    def delete_task(self, task_guid):
        """
        删除任务
        """
        if not self.app_id:
            return

        token = self._get_tenant_access_token()
        url = f"https://open.feishu.cn/open-apis/task/v2/tasks/{task_guid}"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        response = requests.delete(url, headers=headers)
        return response.json()

if __name__ == "__main__":
    assistant = FeishuTask()
    if not assistant.app_id:
        assistant.initialize()
    else:
        print("Feishu Task is configured.")
