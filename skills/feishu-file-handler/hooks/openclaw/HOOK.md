# Feishu File Handler - OpenClaw Hook

## Hook 说明

此 hook 可用于 OpenClaw 平台，在特定事件触发时自动处理飞书文件。

## 可用 Hook

### UserPromptSubmit Hook

在用户提交提示后自动检查是否有飞书文件需要处理。

**触发条件**: 检测到用户上传了文件
**操作**: 提示用户可以使用 `fetch_feishu_files.py` 获取文件

## 配置方法

1. 复制 hook 到 OpenClaw hooks 目录：
```bash
cp -r skills/feishu-file-handler/hooks/openclaw ~/.openclaw/hooks/feishu-file-handler
```

2. 在 OpenClaw 配置中启用：
```bash
openclaw hooks enable feishu-file-handler
```

## 当前状态

此 hook 为可选配置，默认不启用。需要时手动配置即可。
