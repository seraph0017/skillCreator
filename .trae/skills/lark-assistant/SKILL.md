---
name: "lark-assistant"
description: "飞书(Lark)开发助手，专注于日程(Calendar)和任务(Task)管理。当用户需要创建、查询飞书日程或任务，或进行飞书 API 开发时调用。"
---

# Lark Assistant (飞书开发助手)

此 Skill 旨在辅助开发飞书（Lark）相关应用，特别是日程（Calendar）和任务（Task）管理功能。

## 核心功能

1.  **日程管理 (Calendar)**
    - 创建日程
    - 查询日程
    - 订阅日程变更
2.  **任务管理 (Task)**
    - 创建任务
    - 更新任务状态
    - 分配任务

## 开发指南

### 1. 认证与授权
在调用飞书 API 之前，请确保已获取 `app_id` 和 `app_secret`。

#### 获取 tenant_access_token (自建应用)

```python
def get_tenant_access_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json().get("tenant_access_token")
```

### 2. API 参考

- **获取日历列表**: `GET /open-apis/calendar/v4/calendars`
  - [官方文档](https://open.feishu.cn/document/server-docs/calendar-v4/calendar/list)
- **创建日程**: `POST /open-apis/calendar/v4/calendars/:calendar_id/events`
  - [官方文档](https://open.feishu.cn/document/server-docs/calendar-v4/calendar-event/create)
- **创建任务**: `POST /open-apis/task/v1/tasks`

## 常用代码片段

### Python (使用 requests)

```python
import requests
import json

def list_lark_calendars(token):
    """
    获取日历列表
    """
    url = "https://open.feishu.cn/open-apis/calendar/v4/calendars"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = requests.get(url, headers=headers)
    return response.json()

def create_lark_calendar_event(token, calendar_id, summary, start_time, end_time, description=None, location=None, need_notification=True, attendees=None):
    """
    创建飞书日程
    
    Args:
        token (str): 访问凭证
        calendar_id (str): 日历 ID
        summary (str): 标题
        start_time (int): 开始时间戳（秒）
        end_time (int): 结束时间戳（秒）
        description (str, optional): 描述
        location (dict, optional): 地点信息
        need_notification (bool, optional): 是否通知参与人
        attendees (list, optional): 参与人列表，例如 [{"user_id_type": "open_id", "user_id": "ou_xxx"}]
    """
    url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "summary": summary,
        "start_time": {"timestamp": str(start_time)}, # 秒级时间戳，需转为字符串
        "end_time": {"timestamp": str(end_time)},
        "need_notification": need_notification
    }
    if description:
        payload["description"] = description
    if location:
        payload["location"] = location
    
    # 飞书创建日程接口通常不直接支持 attendees，而是需要单独调用 '添加日程参与人' 接口
    # 但部分版本可能支持 'attendee_ability' 或类似字段，
    # 官方推荐的做法是：先创建日程拿到 event_id，再调用 POST /calendars/:calendar_id/events/:event_id/attendees
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def add_lark_calendar_attendees(token, calendar_id, event_id, attendees, need_notification=True):
    """
    添加日程参与人
    
    Args:
        attendees: list of dict, e.g. [{"user_id_type": "open_id", "user_id": "ou_xxx"}]
    """
    url = f"https://open.feishu.cn/open-apis/calendar/v4/calendars/{calendar_id}/events/{event_id}/attendees"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "attendees": attendees,
        "need_notification": need_notification
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def get_lark_user_id(token, emails=None, mobiles=None):
    """
    通过邮箱或手机号获取用户 ID (Open ID)
    """
    url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id?user_id_type=open_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {}
    if emails:
        payload["emails"] = emails
    if mobiles:
        payload["mobiles"] = mobiles
        
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

## 注意事项
- 请注意飞书 API 的频率限制。
- 时间戳通常为 10 位（秒级）或 13 位（毫秒级），请参考具体 API 文档。
