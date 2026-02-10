---
name: "feishu-assistant"
description: "飞书开发助手，专注于日程(Calendar)和任务(Task)管理。当用户需要创建、查询飞书日程或任务，或进行飞书 API 开发时调用。"
---

# Feishu Assistant (飞书开发助手)

此 Skill 旨在辅助开发飞书相关应用，特别是日程（Calendar）和任务（Task）管理功能。
本 Skill 提供了一个封装好的 Python 客户端 `feishu_client.py`，位于 Skill 根目录下。

## 核心功能

1.  **自动初始化与配置管理**
    -   支持通过命令行交互输入 `App ID`, `App Secret`, `手机号`。
    -   自动通过手机号获取 `User ID (Open ID)`。
    -   配置默认保存至 `~/.feishu_assistant_config.json`。
2.  **智能日程管理 (Calendar)**
    -   **默认参与人**：若未指定参与人，默认将日程发送给当前配置的用户（自己）。
    -   **智能内容生成**：若未提供详细描述，根据会议主题自动生成默认描述。
    -   创建日程、查询日程。

## 使用指南

### 1. 引入客户端

推荐直接使用 Skill 提供的 `FeishuAssistant` 类，而不是从头编写 HTTP 请求。

```python
import sys
import os

# 假设当前脚本在项目根目录，Skill 位于 .trae/skills/feishu-assistant
# 实际使用时请根据路径调整
sys.path.append(os.path.abspath(".trae/skills/feishu-assistant"))

from feishu_client import FeishuAssistant

assistant = FeishuAssistant()
```

### 2. 初始化配置

在使用任何功能前，检查是否已配置。若未配置，调用 `initialize()` 进行交互式设置。

```python
if not assistant.app_id:
    print("首次使用需初始化配置...")
    if assistant.initialize():
        print("初始化成功！")
    else:
        print("初始化失败，请检查输入。")
        exit(1)
```

### 3. 创建日程

调用 `create_event` 方法。

```python
summary = "项目周会"
start_time = 1715000000 # 秒级时间戳
end_time = 1715003600

# 场景 1: 默认给自己发，内容自动生成
# 注意：如果不指定 calendar_id，客户端会自动尝试使用应用的默认日历
assistant.create_event(summary, start_time, end_time)

# 场景 2: 指定参与人和内容
attendees = ["ou_xxxxxx", "ou_yyyyyy"]
description = "本周主要议题：\n1. 进度同步\n2. 风险评估"
assistant.create_event(summary, start_time, end_time, attendees=attendees, description=description)
```

## 客户端代码说明 (`feishu_client.py`)

该客户端封装了以下逻辑：
-   **Token 管理**：自动获取并缓存 `tenant_access_token`。
-   **ID 转换**：通过手机号查询 Open ID。
-   **配置持久化**：JSON 文件存储凭证。
-   **日历 ID 自动探测**：
    -   使用 `tenant_access_token` 时，无法直接使用 `primary` 关键字创建日程。
    -   客户端会自动调用 `List Calendars` 接口获取应用（Bot）的主日历 ID，并在该日历上创建日程。
-   **默认行为**：
    -   `attendees` 为空 -> `[self.open_id]`（将自己添加为参与人）
    -   `description` 为空 -> 自动生成
