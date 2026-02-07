# API 配置指南

本项目支持两个 API 提供商：

## 1️⃣ apicore.ai (推荐)

**基础 URL:** `https://api.apicore.ai/v1`

**特点：**
- ✅ OpenAI 兼容格式
- ✅ 支持图像生成
- ✅ 稳定性较好
- ✅ 适合生产环境

**支持的模型：**
- `gemini-3-pro-image-preview` (推荐)
- `gemini-2.0-flash-exp`
- `gpt-4o` (如果支持)

**配置方式：**
```bash
API_PROVIDER=apicore
NANOBANANA_API_KEY=your-apicore-api-key
MODEL_NAME=gemini-3-pro-image-preview
```

**API 格式：**
```json
POST https://api.apicore.ai/v1/chat/completions
{
  "model": "gemini-3-pro-image-preview",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "..."},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
      ]
    }
  ]
}
```

---

## 2️⃣ ismaque.org (12ai)

**基础 URL:** `https://ismaque.org/v1`

**特点：**
- ✅ Gemini 原生 API 格式
- ✅ 直接使用 Google Gemini API
- ✅ 支持最新的 Gemini 模型
- ⚠️ 请求/响应格式与 OpenAI 不同

**支持的模型：**
- `gemini-3-pro-image-preview` (推荐)
- `gemini-3-pro-image-preview-2k`
- `gemini-2.0-flash-exp`
- `gemini-1.5-pro-latest`

**配置方式：**
```bash
API_PROVIDER=12ai
NANOBANANA_API_KEY=your-12ai-api-key
MODEL_NAME=gemini-3-pro-image-preview
```

**API 格式：**
```json
POST https://ismaque.org/v1/models/gemini-3-pro-image-preview:generateContent
{
  "contents": [{
    "parts": [
      {"text": "..."},
      {"inline_data": {"mime_type": "image/jpeg", "data": "base64..."}}
    ]
  }],
  "generationConfig": {
    "temperature": 0.9,
    "responseModalities": ["IMAGE"]
  }
}
```

---

## 🔧 快速切换配置

### 切换到 apicore
```bash
# Linux/Mac
export API_PROVIDER=apicore
export NANOBANANA_API_KEY=your-apicore-key
export MODEL_NAME=gemini-3-pro-image-preview

# Windows PowerShell
$env:API_PROVIDER="apicore"
$env:NANOBANANA_API_KEY="your-apicore-key"
$env:MODEL_NAME="gemini-3-pro-image-preview"
```

### 切换到 12ai
```bash
# Linux/Mac
export API_PROVIDER=12ai
export NANOBANANA_API_KEY=your-12ai-key
export MODEL_NAME=gemini-3-pro-image-preview

# Windows PowerShell
$env:API_PROVIDER="12ai"
$env:NANOBANANA_API_KEY="your-12ai-key"
$env:MODEL_NAME="gemini-3-pro-image-preview"
```

---

## 🆚 两个 API 的区别

| 特性 | apicore.ai | ismaque.org (12ai) |
|------|-----------|-------------------|
| **API 格式** | OpenAI 兼容 | Gemini 原生 |
| **端点 URL** | `/v1/chat/completions` | `/v1/models/{model}:generateContent` |
| **图片数据格式** | `data:image/jpeg;base64,...` | `{"mime_type": "...", "data": "base64..."}` |
| **响应格式** | `choices[0].message.content` | `candidates[0].content.parts[].inlineData` |
| **温度参数** | `temperature` | `generationConfig.temperature` |
| **图像输出** | Base64 in text | `inlineData` 对象 |

---

## 🚨 常见问题

### 问题1：apicore 返回原图或文本
**原因：** 某些模型可能不支持图像生成，或 prompt 格式不被识别

**解决：**
1. 尝试切换到 12ai
2. 使用 `gemini-3-pro-image-preview` 模型
3. 查看日志确认 API 返回格式

### 问题2：12ai 返回错误
**原因：** Gemini 原生格式要求更严格

**解决：**
1. 确认使用 Gemini 模型（模型名以 gemini- 开头）
2. 检查图片 base64 编码是否正确
3. 确认 `responseModalities` 包含 `"IMAGE"`

### 问题3：API Key 无效
**解决：**
```bash
# 测试 API Key
curl -H "Authorization: Bearer your-api-key" \
  https://api.apicore.ai/v1/models

# 或
curl -H "Authorization: Bearer your-api-key" \
  https://ismaque.org/v1/models
```

---

## 🧪 测试 API

### 测试 apicore
```bash
curl -X POST https://api.apicore.ai/v1/chat/completions \
  -H "Authorization: Bearer $NANOBANANA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro-image-preview",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### 测试 12ai
```bash
curl -X POST "https://ismaque.org/v1/models/gemini-3-pro-image-preview:generateContent" \
  -H "Authorization: Bearer $NANOBANANA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Hello"}]}]
  }'
```

---

## 💡 推荐配置

### 生产环境（稳定性优先）
```bash
API_PROVIDER=apicore
MODEL_NAME=gemini-3-pro-image-preview
```

### 实验环境（功能最新）
```bash
API_PROVIDER=12ai
MODEL_NAME=gemini-3-pro-image-preview
```

### 备份方案
如果主 API 失败，可以配置环境变量快速切换：
```bash
# 设置两个 API Key
APICORE_KEY=your-apicore-key
12AI_KEY=your-12ai-key

# 主用 apicore，失败时切换到 12ai
API_PROVIDER=apicore
NANOBANANA_API_KEY=$APICORE_KEY
```

---

## 📊 状态监控

查看当前 API 配置：
```bash
curl http://localhost:5000/debug/config
```

查看最后一次 API 调用：
```bash
curl http://localhost:5000/debug/api
```

查看健康状态：
```bash
curl http://localhost:5000/debug/health
```
