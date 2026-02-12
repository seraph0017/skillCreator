# Skill Creator Project

This project is used to manage and create Trae Skills.

## Skills

The skills are located in `.trae/skills/`.

### Available Skills

- **[openclaw](.trae/skills/openclaw/SKILL.md)**: 专用于 OpenClaw 项目的开发助手。
- **[feishu-calendar](.trae/skills/feishu-calendar/SKILL.md)**: 飞书日历助手，专注于日程管理。支持自动初始化配置、默认发日程给自己等特性。
- **[feishu-tasks](.trae/skills/feishu-tasks/SKILL.md)**: 飞书任务助手，专注于任务管理。支持创建、查询、完成任务等功能。
- **[feishu-drive](.trae/skills/feishu-drive/SKILL.md)**: 飞书云文档助手，支持文档/表格/文件夹的创建、管理、上传、内容写入及权限共享。
- **[feishu-cards](.trae/skills/feishu-cards/SKILL.md)**: 飞书消息卡片助手，支持构建和发送富文本 (Markdown) 卡片消息。
- **[volcengine-vision](.trae/skills/volcengine-vision/SKILL.md)**: 火山引擎视觉模型助手，支持调用 Doubao Vision 模型进行图片内容理解。

## Usage

To create a new skill, create a directory in `.trae/skills/<skill-name>/` and add a `SKILL.md` file.

## Tests

Tests are located in the `test/` directory.

- `test/test_lark_calendar.py`: Tests for the Lark Assistant skill.
# skillCreator
