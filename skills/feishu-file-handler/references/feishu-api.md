# Feishu API 参考

## 文件下载 API

### 获取文件下载链接

```bash
curl -X GET "https://open.feishu.cn/open-apis/drive/v1/medias/{file_key}/download" \
  -H "Authorization: Bearer {access_token}"
```

### 响应示例

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "url": "https://xxx.feishucdn.com/xxx",
    "token": "xxx",
    "expire_time": 1234567890
  }
}
```

## 相关文档

- [Feishu Open Platform](https://open.feishu.cn/)
- [Media API](https://open.feishu.cn/document/server-docs/drive-v1/media-media/introduction)
