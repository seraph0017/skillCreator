---
name: "feishu-drive"
description: "飞书云文档(Drive)助手。提供文档(Docs)、电子表格(Sheets)、文件上传/下载、文件夹管理、内容写入及权限管理等功能。"
---

# Feishu Drive (飞书云文档助手)

此 Skill 旨在辅助开发飞书云文档（Drive）应用，提供了一套便捷的文档和文件管理工具。
本 Skill 提供了一个封装好的 Python 客户端 `feishu_drive_client.py`，位于 Skill 根目录下。

## 核心功能

1.  **自动初始化与配置管理**
    -   配置默认保存至 `~/.feishu_drive_config.json`。
    -   支持从其他飞书 Skill (如 `feishu-calendar`) 迁移配置。
2.  **云文档管理 (Docs/Drive)**
    -   **创建**：支持创建文档 (Docx)、电子表格 (Sheet)、文件夹 (Folder)。
    -   **上传**：支持上传本地文件（图片、视频、普通文件）到云空间。
    -   **查询**：列出云空间文件、搜索文件。
    -   **下载**：下载云空间文件。
    -   **删除**：删除云空间文件。
    -   **修改**：重命名或移动文件。
3.  **高级功能**
    -   **内容写入**：向 Docx 文档追加文本内容。
    -   **权限管理**：添加协作者并精细控制权限 (阅读/编辑/管理)。

## 前置要求 (权限配置)

为了正常使用本 Skill，请确保您的飞书应用 (自建应用) 已开通以下权限：

1.  **云文档 (Drive)**:
    -   `drive:drive` (管理云文档) - **推荐开启，覆盖绝大多数功能**
    -   `drive:drive:readonly` (只读云文档) - 如果仅需查询

2.  **细分业务权限 (必须开启以使用对应功能)**:
    -   **Docs (新版文档)**: `docx:document` 或 `docx:document:create` (创建/编辑文档)
    -   **Sheets (电子表格)**: `sheets:spreadsheet` (创建/编辑表格)
    -   **Bitable (多维表格)**: `bitable:app` (创建/编辑多维表格)

3.  **其他具体权限**:
    -   `space:folder:create` (创建文件夹)
    -   `drive:file:create` (创建文件)
    -   `drive:file:edit` (编辑/移动/重命名文件)
    -   `drive:file:delete` (删除文件)

## 使用指南

### 1. 引入客户端

```python
import sys
import os

sys.path.append(os.path.abspath(".trae/skills/feishu-drive"))
from feishu_drive_client import FeishuDrive

client = FeishuDrive()
```

### 2. 命令行工具集

#### 2.1 创建资源 (`create.py`)
创建文档、表格或文件夹。
```bash
# 创建文档
python3 create.py doc "需求文档"

# 创建表格 (Sheet)
python3 create.py sheet "项目排期"

# 创建多维表格 (Bitable)
python3 create.py bitable "任务追踪"

# 创建文件夹
python3 create.py folder "项目资料"

# 在指定文件夹下创建 (需提供 folder_token)
python3 create.py doc "子文档" --folder_token "fldxxxxxx"
```

#### 2.2 上传文件 (`upload.py`)
上传本地文件。
```bash
python3 upload.py /path/to/image.png --parent_token "fldxxxxxx"
```

#### 2.3 列出文件 (`list.py`)
列出根目录或指定文件夹下的文件。
```bash
python3 list.py [folder_token]
```

#### 2.4 修改文件 (`modify.py`)
重命名文件或移动文件到其他文件夹。
```bash
python3 modify.py FILE_TOKEN [--name "新名称"] [--folder_token "目标文件夹Token"]
```
示例：
```bash
# 重命名
python3 modify.py boxcnxxxxxx --name "新文件名" --type file

# 移动
python3 modify.py boxcnxxxxxx --folder_token "fldxxxxxx"
```

#### 2.5 删除文件 (`delete.py`)
删除指定文件或文件夹。
```bash
# 删除普通文件 (上传的文件)
python3 delete.py FILE_TOKEN

# 删除特定类型 (如文件夹、表格、文档)
python3 delete.py FOLDER_TOKEN --type folder
python3 delete.py SHEET_TOKEN --type sheet
python3 delete.py DOC_TOKEN --type docx
```

#### 2.6 写入文档内容 (`write_doc.py`)
向已存在的 Docx 文档追加文本内容。
```bash
python3 write_doc.py DOC_TOKEN "要写入的文本内容"
```

#### 2.7 权限管理 (`share.py`)
为文档、表格或文件夹添加协作者。
```bash
# 默认授予管理权限 (full_access) 给指定 OpenID 用户
python3 share.py TOKEN MEMBER_ID

# 指定权限、类型和用户ID类型
# 支持角色: view (阅读), edit (编辑), full_access (管理)
# 支持资源类型: docx, sheet, bitable, folder, file
python3 share.py TOKEN EMAIL_ADDRESS --role edit --type sheet --member_type email
```

## 客户端 API 参考

`FeishuDrive` 类提供了以下核心方法：

- `create_folder(name, parent_token)`
- `create_doc(name, parent_token)`
- `create_sheet(name, parent_token)`
- `create_bitable(name, parent_token)`
- `upload_file(file_path, parent_token)`
- `list_files(folder_token)`
- `delete_file(file_token, type)`
- `rename_file(file_token, new_name, type)`
- `move_file(file_token, folder_token, type)`
- `add_docx_content(document_id, content)`: 向文档追加文本块
- `add_member_permission(token, member_id, member_type, role, type)`: 添加协作者
