# Feishu File Handler Skill

## 概述

自动处理从飞书发送的文件，将其复制到 workspace 并触发后续工作流。

## 功能

- ✅ 检测飞书文件发送消息（`msg_type == 'file'`）
- ✅ 自动将文件从 `~/.nanobot/media/feishu/` 复制到 `vault/contracts/original/`
- ✅ 在对话框中提供用户反馈
- ✅ 可选：自动触发合同审查流程
- ✅ 避免重复处理同一文件

## 使用方式

### 方式一：直接调用

```python
from skills.feishu_file_handler import FeishuFileHandler

handler = FeishuFileHandler()

# 处理飞书文件消息
result = handler.handle_file_message({
    'msg_type': 'file',
    'message_id': 'om_xxxxx',
    'content': {
        'file_key': 'v3_xxxxx',
        'filename': '合同.txt'
    },
    'sender': {
        'sender_id': 'ou_xxxxx',
        'sender_type': 'user'
    },
    'create_time': '1773113696'
})
```

### 方式二：集成到消息处理流程

```python
# 在消息处理回调中
if message.get('msg_type') == 'file':
    handler = FeishuFileHandler()
    result = handler.handle_file_message(message)
    # 发送反馈给用户
    send_message(result['user_message'])
```

## 配置

编辑 `config.json`：

```json
{
  "source_dir": "~/.nanobot/media/feishu/",
  "target_dir": "vault/contracts/original/",
  "auto_trigger_review": true,
  "supported_filetypes": [".txt", ".docx", ".pdf", ".doc"],
  "create_backup": true,
  "processed_messages_file": "memory/processed_feishu_messages.json"
}
```

## 工作流程

```
用户发送文件
    ↓
飞书组件自动下载到 ~/.nanobot/media/feishu/
    ↓
检测文件消息 (msg_type == 'file')
    ↓
提取 file_key 和 filename
    ↓
定位并复制文件到 workspace/vault/contracts/original/
    ↓
发送用户反馈
    ↓
[可选] 触发合同审查流程
```

## 输出信息

处理成功后返回：

```python
{
    'success': True,
    'message': '文件已处理',
    'source_file': 'C:/Users/Administrator/.nanobot/media/feishu/合同.txt',
    'target_file': 'vault/contracts/original/合同.txt',
    'user_message': '✅ 已收到文件【合同.txt】，已存档至 workspace',
    'trigger_review': True
}
```

## 依赖

- Python 3.8+
- 标准库（无需额外安装）

## 注意事项

1. **文件来源**: 假设飞书组件已自动将文件下载到 `~/.nanobot/media/feishu/`
2. **重复处理**: 通过记录已处理的 `message_id` 避免重复
3. **文件冲突**: 如果目标文件已存在，会添加时间戳后缀
4. **自动审查**: 仅当文件名包含"合同"、"协议"、"条款"等关键词时才触发

## 示例场景

### 场景 1: 用户发送合同文件

```
用户: [上传: 四次展期协议书.txt]
    ↓
系统: ✅ 已收到文件【四次展期协议书.txt】，已存档至 workspace
系统: 📋 正在开始合同审查...
```

### 场景 2: 文件已处理

```
用户: [重新发送: 同一份文件]
    ↓
系统: ℹ️ 该文件已在之前处理过
```

## 调试

```python
handler = FeishuFileHandler()
handler.debug = True
result = handler.handle_file_message(message)
# 输出详细处理日志
```
