---
name: "feishu-tasks"
description: "飞书任务助手，专注于飞书任务(Task)管理。提供创建、查询、修改、删除任务的便捷工具。"
---

# Feishu Task (飞书任务助手)

此 Skill 旨在辅助开发飞书任务应用，提供了一套便捷的任务（Task）管理工具。
本 Skill 提供了一个封装好的 Python 客户端 `feishu_task_client.py`，位于 Skill 根目录下。

## 核心功能

1.  **自动初始化与配置管理**
    -   支持通过命令行交互输入 `App ID`, `App Secret`, `手机号`。
    -   自动通过手机号获取 `User ID (Open ID)`。
    -   配置默认保存至 `~/.feishu_task_config.json`。
2.  **任务管理 (Task)**
    -   创建任务（支持标题、描述、截止时间、负责人）。
    -   查询任务列表。
    -   完成任务。
    -   删除任务。

## 使用指南

### 1. 引入客户端

推荐直接使用 Skill 提供的 `FeishuTask` 类。

```python
import sys
import os

# 假设当前脚本在项目根目录，Skill 位于 .trae/skills/feishu-tasks
sys.path.append(os.path.abspath(".trae/skills/feishu-tasks"))

from feishu_task_client import FeishuTask

assistant = FeishuTask()
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

### 3. 创建任务

调用 `create_task` 方法。

```python
summary = "完成项目报告"
description = "包含Q1季度总结"
# 截止时间戳 (毫秒级)
import time
due_time = int(time.time() * 1000) + 86400 * 1000 # 明天

# 创建任务（默认负责人为自己）
result = assistant.create_task(summary, description=description, due_timestamp=due_time)
print(result)
```

### 4. 列出任务

```python
tasks = assistant.list_tasks()
if tasks.get("code") == 0:
    for task in tasks.get("data", {}).get("items", []):
        print(f"Task: {task.get('summary')} (ID: {task.get('guid')})")
```

### 5. 完成任务

```python
task_guid = "xxxx-xxxx-xxxx"
assistant.complete_task(task_guid)
```

## 客户端代码说明 (`feishu_task_client.py`)

该客户端封装了以下逻辑：
-   **Token 管理**：自动获取并缓存 `tenant_access_token`。
-   **配置持久化**：JSON 文件存储凭证。
-   **API 封装**：对接飞书 Task V2 API。
