# Feishu File Handler 📥

从飞书媒体目录获取文件到 nanobot workspace。

## 背景

由于 nanobot 的 `restrictToWorkspace` 安全限制，所有文件操作（`read_file`、`write_file`、`list_dir` 等）都被限制在 workspace 目录内。飞书接收的文件自动下载到 `~/.nanobot/media/feishu/` 目录，但无法直接访问。

本 skill 通过 Python 脚本作为"桥梁"，将外部文件复制到 workspace，然后使用常规工具处理。

## 功能

- ✅ 列出飞书媒体目录中的所有文件
- ✅ 按文件类型筛选（图片、文档、HTML 等）
- ✅ 获取最新文件
- ✅ 复制指定文件到 workspace
- ✅ 显示文件详细信息（大小、修改时间）
- ✅ 指定输出目录

## 快速开始

### 1. 本地测试

```bash
# 列出所有文件
python skills/feishu-file-handler/scripts/fetch_feishu_files.py --list

# 获取最新文件
python skills/feishu-file-handler/scripts/fetch_feishu_files.py --latest

# 获取指定文件
python skills/feishu-file-handler/scripts/fetch_feishu_files.py filename.docx
```

### 2. 在 nanobot 中使用

```python
# 示例：列出飞书文件
exec("python skills/feishu-file-handler/scripts/fetch_feishu_files.py --list")

# 示例：获取最新文件
exec("python skills/feishu-file-handler/scripts/fetch_feishu_files.py --latest")
```

## 使用方法

### 列出文件

```bash
# 列出所有文件
python scripts/fetch_feishu_files.py --list

# 只列出文档文件
python scripts/fetch_feishu_files.py --list --type doc

# 只列出图片文件
python scripts/fetch_feishu_files.py --list --type image
```

支持的文件类型：
- `all`: 所有文件（默认）
- `image`: 图片文件（png, jpg, jpeg, gif, webp, bmp, svg）
- `doc`: 文档文件（doc, docx, pdf, txt, md, xlsx, pptx）
- `pdf`: PDF 文件
- `text`: 文本文件（txt, md, py, js, html, css, json）

### 获取文件

```bash
# 获取最新文件
python scripts/fetch_feishu_files.py --latest

# 获取最新文档
python scripts/fetch_feishu_files.py --latest --type doc

# 获取指定文件
python scripts/fetch_feishu_files.py filename.docx

# 指定输出目录
python scripts/fetch_feishu_files.py filename.docx --output ./downloads/
```

### 输出示例

**列出文件：**
```
📁 飞书媒体目录: C:\Users\Administrator\.nanobot\media\feishu
   找到 3 个文件

    1. 仓储合同.docx                              23.8 KB  2026-03-13 16:18:32
    2. 四次展期协议书.docx                        20.8 KB  2026-03-09 14:37:08
    3. image_v3_02vm_6ca3.jpg                     127.9 KB  2026-03-11 17:12:11
```

**获取文件：**
```
✅ 已复制: 仓储合同.docx
   来源: C:\Users\Administrator\.nanobot\media\feishu\仓储合同.docx
   目标: C:\Users\Administrator\.nanobot\workspace-legal\仓储合同.docx
   大小: 23.8 KB
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
├── SKILL.md                      # nanobot skill 元数据
├── README.md                     # 项目说明（本文件）
├── .gitignore
├── scripts/
│   └── fetch_feishu_files.py     # 主脚本（新版）
├── feishu_file_handler.py        # [已弃用] 旧版实现
└── config.json                   # [已弃用] 旧版配置
```

## 技术栈

- Python 3
- 标准库：`shutil`, `pathlib`, `sys`, `argparse`, `datetime`

## 依赖

无需额外依赖，仅使用 Python 标准库。

## 版本历史

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

## 常见问题

### Q: 为什么需要这个 skill？

A: nanobot 的安全限制禁止访问 workspace 之外的文件。飞书接收的文件保存在 `~/.nanobot/media/feishu/`，需要通过此脚本复制到 workspace 后才能正常处理。

### Q: 文件会被移动还是复制？

A: 文件会被**复制**到 workspace，原始文件保留在飞书媒体目录。

### Q: 支持哪些文件类型？

A: 支持图片、文档、HTML、文本等常见文件类型。使用 `--list --type all` 查看所有文件。

### Q: 如何与旧版兼容？

A: 旧版的 `feishu_file_handler.py` 和 `config.json` 仍然保留在目录中，但建议使用新的 `fetch_feishu_files.py`。

### Q: 如何在 nanobot 配置中启用？

A: 本 skill 已通过 `SKILL.md` 自动注册，无需额外配置。

## 许可证

MIT License

## 作者

[nanobot](https://github.com/windmonk) - nanobot AI 助手框架

## 相关链接

- [nanobot](https://github.com/windmonk/nanobot) - nanobot AI 助手框架
- [feishu-fetcher](https://github.com/windmonk/feishu-fetcher) - 简洁的飞书文件获取工具
- [Feishu Open Platform](https://open.feishu.cn/) - 飞书开放平台
