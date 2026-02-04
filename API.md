# 肖像照生成网站 - API 文档

## 概述

本文档描述了肖像照生成网站的 API 接口。

## 基础 URL

```
http://localhost:5000   (本地开发)
https://your-domain.com (生产环境)
```

---

## API 端点

### 1. 验证验证码

验证用户输入的验证码是否有效，并返回剩余使用次数。

**请求**
```
POST /api/verify
Content-Type: application/json

{
  "code": "ABC12345"
}
```

**响应**
```json
{
  "success": true,
  "remaining": 3,
  "max_uses": 3
}
```

**错误响应**
```json
{
  "success": false,
  "message": "验证码不存在"
}
```

---

### 2. 上传图片并生成

上传用户照片，调用 NanoBanana API 生成风格化肖像。

**请求**
```
POST /api/upload
Content-Type: multipart/form-data

code: ABC12345
style: haima
image: [文件]
```

**参数说明**
- `code`: 验证码
- `style`: 风格类型
  - `haima`: 海马体风格
  - `portrait`: 美式肖像风格
- `image`: 图片文件 (支持 PNG、JPG、WEBP，最大 16MB)

**响应**
```json
{
  "success": true,
  "result_url": "/result/20240101_120000_photo.jpg",
  "remaining": 2
}
```

**错误响应**
```json
{
  "success": false,
  "message": "验证码使用次数已用完"
}
```

---

### 3. 获取生成的图片

返回生成的图片文件。

**请求**
```
GET /result/<filename>
```

**响应**
```
返回图片文件 (二进制)
```

---

### 4. 获取验证码状态

获取指定验证码的详细信息和生成历史。

**请求**
```
GET /api/status/<code>
```

**响应**
```json
{
  "success": true,
  "remaining": 2,
  "max_uses": 3,
  "history": [
    {
      "style": "haima",
      "time": "2024-01-01 12:00:00",
      "result": "20240101_120000_photo.jpg"
    }
  ]
}
```

---

## 管理后台 API

### 1. 批量生成验证码

**请求**
```
POST /admin/generate_codes
Content-Type: application/json

{
  "count": 100,
  "max_uses": 3
}
```

**响应**
```json
{
  "success": true,
  "codes": ["ABC12345", "DEF67890", ...],
  "count": 100
}
```

---

### 2. 导出验证码

导出所有活跃的验证码到文本文件。

**请求**
```
GET /admin/export_codes
```

**响应**
```
Content-Type: text/plain
Content-Disposition: attachment; filename=verification_codes.txt

ABC12345
DEF67890
...
```

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 常见错误信息

| 错误信息 | 说明 |
|----------|------|
| 验证码不存在 | 输入的验证码不在数据库中 |
| 验证码已失效 | 验证码已被标记为非活跃状态 |
| 验证码使用次数已用完 | 验证码已达到最大使用次数 |
| 请上传图片 | 未检测到上传的图片文件 |
| 只支持 PNG、JPG、JPEG、WEBP 格式 | 上传的文件格式不支持 |
| 图片大小不能超过16MB | 上传的文件过大 |
| 生成失败: ... | NanoBanana API 调用失败 |

---

## 集成示例

### JavaScript (Fetch)

```javascript
// 验证验证码
const verifyCode = async (code) => {
  const response = await fetch('/api/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code })
  });
  return await response.json();
};

// 上传图片
const uploadImage = async (code, style, file) => {
  const formData = new FormData();
  formData.append('code', code);
  formData.append('style', style);
  formData.append('image', file);

  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData
  });
  return await response.json();
};
```

### Python (Requests)

```python
import requests

# 验证验证码
def verify_code(code):
    response = requests.post(
        'http://localhost:5000/api/verify',
        json={'code': code}
    )
    return response.json()

# 上传图片
def upload_image(code, style, image_path):
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {
            'code': code,
            'style': style
        }
        response = requests.post(
            'http://localhost:5000/api/upload',
            files=files,
            data=data
        )
    return response.json()
```

### cURL

```bash
# 验证验证码
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"code": "ABC12345"}'

# 上传图片
curl -X POST http://localhost:5000/api/upload \
  -F "code=ABC12345" \
  -F "style=haima" \
  -F "image=@/path/to/image.jpg"
```
