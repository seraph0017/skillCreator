---
name: "feishu-cards"
description: "飞书消息卡片(Message Card)助手。提供构建和发送富文本卡片消息的功能。支持Card JSON 2.0规范，用于在对话中输出结构化、富文本内容。"
---

# Feishu Cards (飞书消息卡片助手)

此 Skill 旨在帮助用户构建和发送飞书富文本消息卡片 (Card JSON V2)。
本 Skill 提供了一个封装好的 Python 客户端 `feishu_card_client.py`，位于 Skill 根目录下。

## 核心功能

1.  **自动初始化与配置管理**
    -   配置默认保存至 `~/.feishu_card_config.json`。
    -   支持从其他飞书 Skill (如 `feishu-calendar`, `feishu-drive`) 迁移配置。
2.  **发送卡片消息**
    -   **发送富文本卡片**: 支持 Markdown 语法的卡片消息。
    -   **预览/调试**: 可以在终端生成卡片 JSON 结构。

## 前置要求 (权限配置)

为了正常使用本 Skill，请确保您的飞书应用 (自建应用) 已开通以下权限：

1.  **消息 (Message)**:
    -   `im:message` 或 `im:message:send_as_bot` (以应用身份发送消息) - **必须开启**
    -   `im:chat` (获取群组信息，如果需要发送到群)

2.  **通讯录 (Contact)**:
    -   `contact:user.id:readonly` (获取用户 ID，用于发送消息给特定用户)

## 使用指南

### 1. 引入客户端

```python
import sys
import os

sys.path.append(os.path.abspath(".trae/skills/feishu-cards"))
from feishu_card_client import FeishuCard

client = FeishuCard()
```

### 2. 命令行工具集

#### 2.1 发送卡片 (`send_card.py`)
发送包含 Markdown 内容的富文本卡片。

```bash
# 发送给默认配置的用户 (OpenID)
python3 send_card.py "这是一个标题" "**加粗内容**\n*斜体内容*\n[链接](https://feishu.cn)"

# 指定接收者 (OpenID)
python3 send_card.py "标题" "内容" --receive_id "ou_xxxxxx"

# 指定接收者类型 (默认为 open_id, 支持 user_id, union_id, email, chat_id)
python3 send_card.py "标题" "内容" --receive_id "xxx@example.com" --receive_id_type email
```

## 客户端 API 参考

`FeishuCard` 类提供了以下核心方法：

- `send_card(title, content, receive_id, receive_id_type, card_config)`: 发送卡片消息
  - `title`: 卡片标题 (纯文本)
  - `content`: 卡片内容 (支持 Markdown)
  - `receive_id`: 接收者 ID
  - `receive_id_type`: 接收者 ID 类型 (open_id, user_id, union_id, email, chat_id)
  - `card_config`: 卡片配置 (字典)，如 `{"wide_screen_mode": True}`

## Card JSON V2 结构说明

本 Skill 默认生成的卡片结构如下：

```json
{
  "schema": "2.0",
  "header": {
    "title": {
      "content": "标题",
      "tag": "plain_text"
    },
    "template": "blue"
  },
  "body": {
    "elements": [
      {
        "tag": "markdown",
        "content": "Markdown 内容"
      }
    ]
  }
}
```
