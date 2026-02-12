import json
import os
import time
import requests

CONFIG_FILE = os.path.expanduser("~/.feishu_card_config.json")
DRIVE_CONFIG_FILE = os.path.expanduser("~/.feishu_drive_config.json")
CALENDAR_CONFIG_FILE = os.path.expanduser("~/.feishu_calendar_config.json")
TASK_CONFIG_FILE = os.path.expanduser("~/.feishu_task_config.json")

class FeishuCard:
    def __init__(self):
        self.config = self._load_config()
        self.app_id = self.config.get("app_id")
        self.app_secret = self.config.get("app_secret")
        self.open_id = self.config.get("open_id")
        self.tenant_access_token = None
        self.token_expire_time = 0

    def _load_config(self):
        # 1. 尝试读取 card 配置
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        
        # 2. 尝试迁移其他 skill 配置 (优先 drive, 然后 calendar, task)
        for path in [DRIVE_CONFIG_FILE, CALENDAR_CONFIG_FILE, TASK_CONFIG_FILE]:
            if os.path.exists(path):
                try:
                    print(f"Detecting existing configuration from {path}...")
                    with open(path, "r") as f:
                        config = json.load(f)
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
        print("Initializing Feishu Card...")
        app_id = input("Enter App ID: ").strip()
        app_secret = input("Enter App Secret: ").strip()
        phone = input("Enter Phone Number: ").strip()

        try:
            token = self._get_tenant_access_token(app_id, app_secret)
            
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

    def send_card(self, title, content, receive_id=None, receive_id_type="open_id", card_config=None):
        """
        发送富文本卡片消息
        :param title: 卡片标题
        :param content: Markdown 内容
        :param receive_id: 接收者 ID (默认使用配置中的 open_id)
        :param receive_id_type: 接收者 ID 类型 (open_id, user_id, union_id, email, chat_id)
        :param card_config: 卡片配置 (字典)
        """
        if not self.app_id:
            print("Configuration missing.")
            return

        target_id = receive_id or self.open_id
        if not target_id:
            print("Target ID (receive_id) is missing.")
            return

        token = self._get_tenant_access_token()
        
        # 构造 Card JSON V2
        card_content = {
            "schema": "2.0",
            "header": {
                "title": {
                    "content": title,
                    "tag": "plain_text"
                },
                "template": "blue" # 默认蓝色主题
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
        
        if card_config:
            card_content["config"] = card_config

        url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        payload = {
            "receive_id": target_id,
            "msg_type": "interactive",
            "content": json.dumps(card_content) # content 必须是 JSON 字符串
        }
        
        response = requests.post(url, headers=headers, json=payload)
        return response.json()

if __name__ == "__main__":
    client = FeishuCard()
    if not client.app_id:
        client.initialize()
    else:
        print("Feishu Card is configured.")
