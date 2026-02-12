---
name: "volcengine-vision"
description: "火山引擎(Volcengine)视觉模型助手。调用 Doubao-seed-1.6-vision 模型进行图片内容理解和描述。"
---

# Volcengine Vision (火山引擎视觉助手)

此 Skill 旨在调用火山引擎方舟平台 (Volcengine ARK) 的视觉大模型 API，实现图片内容的自动识别与理解。
本 Skill 封装了一个 Python 客户端 `volcengine_client.py`，并提供命令行工具 `analyze_image.py`。

## 核心功能

1.  **自动初始化与配置管理**
    -   配置默认保存至 `~/.volcengine_config.json`。
    -   首次运行时会提示输入 `ARK_API_KEY`。
2.  **图片理解与描述**
    -   **图片分析**: 输入图片 URL 和提示词 (Prompt)，获取模型对图片的详细描述。
    -   **模型支持**: 默认使用 `doubao-seed-1-6-vision-250815` 模型。

## 前置要求

为了正常使用本 Skill，请确保您已在火山引擎控制台获取 API Key：
1.  注册并登录 [火山引擎控制台](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint)。
2.  开通模型推理服务，并创建 API Key。
3.  确保您的账户有足够的额度调用 API。

## 使用指南

### 1. 引入客户端

```python
import sys
import os

sys.path.append(os.path.abspath(".trae/skills/volcengine-vision"))
from volcengine_client import VolcengineVision

client = VolcengineVision()
```

### 2. 命令行工具集

#### 2.1 图片理解 (`analyze_image.py`)
输入图片 URL，获取 AI 对图片的描述。

```bash
# 基本用法 (默认提示词: "图片主要讲了什么?")
python3 analyze_image.py "https://ark-project.tos-cn-beijing.volces.com/images/view.jpeg"

# 自定义提示词
python3 analyze_image.py "https://ark-project.tos-cn-beijing.volces.com/images/view.jpeg" --prompt "请详细描述这张图片中的颜色和物体"

# 指定模型 (如果需要更换模型版本)
python3 analyze_image.py "https://example.com/image.jpg" --model "doubao-seed-1-6-vision-250815"
```

## 客户端 API 参考

`VolcengineVision` 类提供了以下核心方法：

- `analyze_image(image_url, prompt="图片主要讲了什么?", model="doubao-seed-1-6-vision-250815")`: 分析图片内容
  - `image_url`: 图片的公网 URL 地址
  - `prompt`: 对模型的提问 (默认: "图片主要讲了什么?")
  - `model`: 使用的模型版本 (默认: `doubao-seed-1-6-vision-250815`)

## API 调用示例 (Python)

```python
response = client.analyze_image(
    image_url="https://ark-project.tos-cn-beijing.volces.com/images/view.jpeg",
    prompt="这张图里有几个人?"
)
print(response)
```
