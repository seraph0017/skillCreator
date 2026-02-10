import json
import os
import time
import requests

CONFIG_FILE = os.path.expanduser("~/.feishu_assistant_config.json")

class FeishuAssistant:
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
        print("Initializing Feishu Assistant...")
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

    def list_calendars(self):
        """
        获取日历列表
        """
        token = self._get_tenant_access_token()
        url = "https://open.feishu.cn/open-apis/calendar/v4/calendars"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def create_event(self, summary, start_time, end_time, attendees=None, description=None, calendar_id=None):
        """
        创建日程
        :param summary: 会议主题
        :param start_time: 开始时间戳 (int, 秒)
        :param end_time: 结束时间戳 (int, 秒)
        :param attendees: 参与人 ID 列表 (list of open_id)。如果为空，默认添加自己。
        :param description: 会议描述。如果为空，根据主题生成。
        :param calendar_id: 指定在哪个日历创建。如果不填，尝试获取应用的默认日历。
        """
        if not self.app_id:
            print("Configuration missing. Please run initialize() first.")
            return

        token = self._get_tenant_access_token()
        
        # 1. 默认逻辑：如果没有参与人，添加自己
        if not attendees:
            attendees = [self.open_id]
            print(f"No attendees specified. Defaulting to self ({self.open_id}).")
        
        # 2. 默认逻辑：如果没有描述，生成默认描述
        if not description:
            description = f"会议主题：{summary}\n自动生成的会议日程。"
            
        # 3. 确定 Calendar ID
        if not calendar_id:
            # 尝试获取应用的主日历
            # 注意：使用 tenant_access_token 时，无法直接使用 'primary' 别名，必须指定 ID
            # 同时也无法直接操作用户的 open_id 对应的日历（除非有特定权限且 ID 格式正确）
            # 这里尝试获取应用（Bot）自己的日历列表中的第一个
            calendars = self.list_calendars()
            if calendars.get("code") == 0:
                cal_list = calendars.get("data", {}).get("calendar_list", [])
                if cal_list:
                    calendar_id = cal_list[0].get("calendar_id")
                    print(f"Auto-detected calendar_id: {calendar_id}")
        
        if not calendar_id:
             print("Error: Could not determine calendar_id. Please specify one.")
             return None

        # 创建日程
        url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        payload = {
            "summary": summary,
            "description": description,
            "start_time": {"timestamp": str(start_time)},
            "end_time": {"timestamp": str(end_time)},
            "need_notification": True
        }
        
        response = requests.post(url, headers=headers, json=payload)
        resp_json = response.json()
        
        if resp_json.get("code") != 0:
            print(f"Create event failed: {resp_json}")
            return None
            
        event_id = resp_json.get("data", {}).get("event", {}).get("event_id")
        print(f"Event created successfully! Event ID: {event_id}")
        
        # 添加参与人
        self._add_attendees(token, calendar_id, event_id, attendees)
        
        return event_id

    def _add_attendees(self, token, calendar_id, event_id, attendee_ids):
        if not attendee_ids:
            return
            
        url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events/{event_id}/attendees"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        attendees_payload = []
        for uid in attendee_ids:
            attendees_payload.append({
                "type": "user",
                "user_id_type": "open_id",
                "user_id": uid
            })
            
        payload = {
            "attendees": attendees_payload
        }
        
        response = requests.post(url, headers=headers, json=payload)
        resp_json = response.json()
        
        if resp_json.get("code") != 0:
            print(f"Add attendees failed: {resp_json}")
        else:
            print(f"Added {len(attendee_ids)} attendees.")

if __name__ == "__main__":
    # 简单的命令行交互用于测试/初始化
    assistant = FeishuAssistant()
    if not assistant.app_id:
        assistant.initialize()
    else:
        print("Feishu Assistant is configured.")
