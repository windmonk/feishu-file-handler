---
name: feishu-file-handler
description: "从飞书媒体目录（~/.nanobot/media/feishu/）获取文件到 nanobot workspace。由于 restrictToWorkspace 安全限制，此技能提供文件复制功能。"
---

# Feishu File Handler Skill

## 概述

从飞书媒体目录（`~/.nanobot/media/feishu/`）获取文件到 nanobot workspace。

由于 nanobot 的 `restrictToWorkspace` 安全限制，所有文件操作都被限制在 workspace 目录内。本 skill 提供了一个简单工具，将飞书接收的文件复制到 workspace 后正常处理。

## 功能

- ✅ 列出飞书媒体目录中的所有文件
- ✅ 按文件类型筛选（图片、文档、HTML 等）
- ✅ 获取最新文件
- ✅ 获取指定文件
- ✅ 指定输出目录
- ✅ 显示文件详细信息（大小、修改时间）

## 使用方法

### 列出所有文件

```bash
python skills/feishu-file-handler/scripts/fetch_feishu_files.py --list
```

输出示例：
```
📁 飞书媒体目录: C:\Users\Administrator\.nanobot\media\feishu
   找到 3 个文件

    1. 仓储合同.docx                              23.8 KB  2026-03-13 16:18:32
    2. 四次展期协议书.docx                        20.8 KB  2026-03-09 14:37:08
    3. image_v3_02vm_6ca3.jpg                     127.9 KB  2026-03-11 17:12:11
```

### 按类型筛选

**只列出文档文件：**
```bash
python skills/feishu-file-handler/scripts/fetch_feishu_files.py --list --type doc
```

**只列出图片文件：**
```bash
python skills/feishu-file-handler/scripts/fetch_feishu_files.py --list --type image
```

支持的文件类型：
- `all`: 所有文件（默认）
- `image`: 图片文件（png, jpg, jpeg, gif, webp, bmp, svg）
- `doc`: 文档文件（doc, docx, pdf, txt, md, xlsx, pptx）
- `pdf`: PDF 文件
- `text`: 文本文件（txt, md, py, js, html, css, json）

### 获取最新文件

```bash
python skills/feishu-file-handler/scripts/fetch_feishu_files.py --latest
```

输出示例：
```
✅ 已复制: 仓储合同.docx
   来源: C:\Users\Administrator\.nanobot\media\feishu\仓储合同.docx
   目标: C:\Users\Administrator\.nanobot\workspace-legal\仓储合同.docx
   大小: 23.8 KB
```

**获取最新文档文件：**
```bash
python skills/feishu-file-handler/scripts/fetch_feishu_files.py --latest --type doc
```

### 获取指定文件

```bash
python skills/feishu-file-handler/scripts/fetch_feishu_files.py 仓储合同.docx
```

### 指定输出目录

```bash
python skills/feishu-file-handler/scripts/fetch_feishu_files.py 仓储合同.docx --output ./downloads/
```

### 在 Python 中使用

```python
from skills.feishu_file_handler.scripts import fetch_feishu_files

# 列出文件
files = fetch_feishu_files.list_files()
fetch_feishu_files.show_files(files)

# 获取最新文件
fetch_feishu_files.fetch_latest()

# 获取指定文件
fetch_feishu_files.fetch_file("仓储合同.docx")
```

## 工作流程

```
飞书消息 → nanobot 接收 → 下载到 ~/.nanobot/media/feishu/
                           ↓
                    fetch_feishu_files.py
                           ↓
                  复制到 ~/.nanobot/workspace/
                           ↓
                    nanobot 正常处理
```

## 目录结构

```
feishu-file-handler/
├── SKILL.md                      # 本文件（技能元数据）
├── README.md                     # 项目说明
├── .gitignore                    # Git 忽略规则
├── scripts/                      # 脚本文件
│   └── fetch_feishu_files.py     # 主脚本
├── hooks/                        # 钩子脚本
│   └── openclaw/                 # OpenClaw 平台钩子
│       └── HOOK.md
├── assets/                       # 资源文件
│   └── example-config.json       # 示例配置
└── references/                   # 参考文档
    └── feishu-api.md             # Feishu API 参考
```

## 旧版文件（已弃用）

以下文件保留在 git 历史中，但不再使用：
- `feishu_file_handler.py` - v1.0.0 的旧版实现
- `config.json` - v1.0.0 的旧版配置
- `requirements.txt` - v1.0.0 的依赖列表（v2.0.0 使用标准库）

## 技术栈

- Python 3
- 标准库：`shutil`, `pathlib`, `sys`, `argparse`, `datetime`

## 依赖

无需额外依赖，仅使用 Python 标准库。

## 常见问题

### Q: 为什么需要这个 skill？

A: nanobot 的安全限制禁止访问 workspace 之外的文件。飞书接收的文件保存在 `~/.nanobot/media/feishu/`，需要通过此脚本复制到 workspace 后才能正常处理。

### Q: 文件会被移动还是复制？

A: 文件会被**复制**到 workspace，原始文件保留在飞书媒体目录。

### Q: 如何与旧版兼容？

A: 旧版的 `feishu_file_handler.py` 和 `config.json` 仍然保留在目录中，但建议使用新的 `fetch_feishu_files.py`。

### Q: 支持哪些文件类型？

A: 支持图片、文档、HTML、文本等常见文件类型。使用 `--list --type all` 查看所有文件。

## 更新日志

### v2.0.0 (2026-03-13)

- ✨ 重新设计为命令行工具，参考 feishu-fetcher
- 🔧 简化代码，移除复杂的配置和消息处理逻辑
- 📝 更新文档，添加更多使用示例
- ⚠️ 标记旧版实现为已弃用

### v1.0.0 (2026-03-10)

- 🎉 首次发布
- ✅ 自动检测飞书文件消息
- ✅ 消息去重和用户反馈
- ✅ 可选触发合同审查流程

## 许可证

MIT License

## 作者

[nanobot](https://github.com/windmonk) - nanobot AI 助手框架

## 相关链接

- [nanobot](https://github.com/windmonk/nanobot)
- [feishu-fetcher](https://github.com/windmonk/feishu-fetcher)
