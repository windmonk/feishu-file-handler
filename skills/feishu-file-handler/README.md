# Feishu File Handler Skill

自动处理从飞书发送的文件，实现智能归档和工作流触发。

## 功能特性

- 📁 **自动文件归档**: 将飞书文件自动复制到 workspace 工作目录
- 🔄 **避免重复处理**: 通过消息 ID 记录已处理的文件
- 📋 **智能工作流触发**: 根据文件名关键词自动触发合同审查
- 💬 **用户友好反馈**: 在对话框中提供清晰的处理状态提示
- ⚙️ **灵活配置**: 支持自定义源目录、目标目录、文件类型等

## 快速开始

### 1. 基本使用

```python
from skills.feishu_file_handler import handle_feishu_file

# 处理飞书文件消息
result = handle_feishu_file(message)

if result['success']:
    print(result['user_message'])
    # 发送反馈给用户
    if result.get('trigger_review'):
        # 开始合同审查流程
        pass
```

### 2. 高级使用

```python
from skills.feishu_file_handler import FeishuFileHandler

# 创建处理器实例
handler = FeishuFileHandler()
handler.debug = True  # 启用调试模式

# 处理消息
result = handler.handle_file_message(message)
```

## 配置说明

编辑 `config.json` 文件：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `source_dir` | 飞书文件下载目录 | `~/.nanobot/media/feishu/` |
| `target_dir` | workspace 存档目录 | `vault/contracts/original/` |
| `auto_trigger_review` | 是否自动触发审查 | `true` |
| `supported_filetypes` | 支持的文件类型 | `[.txt, .docx, .doc, .pdf]` |
| `create_backup` | 是否创建备份 | `true` |
| `processed_messages_file` | 已处理消息记录文件 | `memory/processed_feishu_messages.json` |

## 工作流程

```
┌─────────────────────────────────────┐
│      用户通过飞书发送文件              │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  飞书组件下载到 ~/.nanobot/media/   │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│   检测文件消息 (msg_type == 'file')  │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│       提取 file_key 和 filename      │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│     查找并复制到 workspace/          │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│         发送用户反馈                  │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│    [可选] 触发合同审查流程            │
└─────────────────────────────────────┘
```

## 触发合同审查的条件

满足以下条件时自动触发合同审查：

1. `auto_trigger_review` 配置为 `true`
2. 文件扩展名在 `supported_filetypes` 列表中
3. 文件名包含以下关键词之一：
   - 合同
   - 协议
   - 条款
   - 补充
   - 约定
   - contract
   - agreement

## 返回结果

### 成功响应

```json
{
  "success": true,
  "message": "文件已处理",
  "source_file": "C:/Users/Administrator/.nanobot/media/feishu/合同.txt",
  "target_file": "vault/contracts/original/合同.txt",
  "filename": "合同.txt",
  "file_key": "v3_xxxxx",
  "message_id": "om_xxxxx",
  "trigger_review": true,
  "user_message": "✅ 已收到文件【合同.txt】，已存档至 workspace\n📋 正在开始合同审查..."
}
```

### 文件已处理

```json
{
  "success": true,
  "message": "文件已在之前处理过",
  "already_processed": true,
  "user_message": "ℹ️ 该文件已在之前处理过"
}
```

### 失败响应

```json
{
  "success": false,
  "message": "未找到文件: 合同.txt",
  "user_message": "❌ 未找到文件【合同.txt】，请确认文件是否已下载"
}
```

## 文件冲突处理

如果目标目录已存在同名文件，系统会自动添加时间戳后缀：

```
原始文件名: 四次展期协议书.txt
冲突后文件名: 四次展期协议书_20260310_121756.txt
```

## 调试

启用调试模式查看详细处理日志：

```python
handler = FeishuFileHandler()
handler.debug = True
result = handler.handle_file_message(message)
```

调试输出示例：

```
[DEBUG] 开始处理文件消息: om_test_123456
[DEBUG] 文件信息: file_key=v3_test_key, filename=测试合同.txt
[DEBUG] 在目录中查找文件: C:/Users/Administrator/.nanobot/media/feishu
[DEBUG] 查找关键词: file_key=v3_test_key, filename=测试合同.txt
[DEBUG] 检查文件: 四次展期协议书.txt
[DEBUG] 找到模糊匹配: C:/Users/Administrator/.nanobot/media/feishu/四次展期协议书.txt
[DEBUG] 文件已复制: .../四次展期协议书.txt -> vault/contracts/original/四次展期协议书.txt
[DEBUG] 已记录处理消息: om_test_123456
[DEBUG] 处理完成: vault/contracts/original/四次展期协议书.txt
```

## 注意事项

1. **依赖飞书组件**: 假设飞书组件已自动将文件下载到配置的源目录
2. **文件命名**: 源文件名可能与上传文件名不完全一致，支持模糊匹配
3. **消息记录**: 已处理的消息 ID 会持久化存储，避免重复处理
4. **工作目录**: 目标目录相对于 workspace 根目录

## 故障排除

### 问题: 未找到文件

**可能原因:**
- 飞书组件未下载文件
- 文件名不匹配
- 源目录配置错误

**解决方法:**
1. 检查 `~/.nanobot/media/feishu/` 目录是否存在
2. 启用调试模式查看详细日志
3. 确认文件是否已成功下载

### 问题: 重复处理同一文件

**预期行为:**
- 系统通过 `message_id` 记录已处理的消息
- 同一消息不会重复处理

**如需重新处理:**
- 删除 `memory/processed_feishu_messages.json` 中的对应记录
- 或使用新的消息发送文件

## 版本历史

- **v1.0.0** (2026-03-10): 初始版本
  - 支持文件自动归档
  - 支持智能工作流触发
  - 支持重复消息过滤
  - 支持文件冲突处理

## 许可证

MIT License
