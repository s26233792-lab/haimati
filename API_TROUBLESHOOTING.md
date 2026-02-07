# API 图片生成问题排查指南

## 🚨 问题描述
上传图片并生成后，返回的还是原来的图片（或只有简单背景替换），API 显示已消耗。

## 🔍 问题原因分析

### 1. 模型不支持图像生成
某些模型只支持文本输出，不支持图像生成。

**检查方法：**
```bash
python debug_api.py
```

**解决方案：**
- 使用支持图像生成的模型：
  - ✅ `gemini-3-pro-image-preview` (推荐)
  - ✅ `gemini-2.0-flash-exp`
  - ✅ `gpt-4o` (如果 API 支持)

### 2. API 格式不匹配
不同的 API 提供商使用不同的请求/响应格式。

**配置检查：**
```bash
# 查看当前配置
curl http://localhost:5000/debug/config

# 查看最后一次 API 调用
curl http://localhost:5000/debug/api
```

**正确的配置组合：**

| API 提供商 | 支持的模型 | API 格式 |
|-----------|-----------|---------|
| apicore | gemini-3-pro-image-preview | OpenAI 兼容 |
| 12ai | gemini-* | Gemini 原生 |
| laozhang | gpt-4o, gemini-* | OpenAI 兼容 |

### 3. Prompt 问题
某些 API 对 prompt 的格式要求很严格。

**已修复：**
- 代码中已移除了可能无效的 `strength` 和 `guidance_scale` 参数
- 添加了更强的 prompt 指令，明确要求生成新图片

### 4. API 返回文本而非图片
某些情况下，API 会返回解释性文本而不是图片。

**检测方法：**
查看日志中是否有 `[API] ⚠️ API 返回了文本而不是图片！` 的提示。

## 🛠️ 修复步骤

### 步骤1：运行诊断工具
```bash
python debug_api.py
```

这将检查：
- API Key 是否配置正确
- 模型是否支持图像生成
- 测试图片生成是否正常

### 步骤2：检查 API 配置
```bash
# 本地开发
export NANOBANANA_API_KEY=你的API密钥
export API_PROVIDER=apicore  # 或 12ai, laozhang
export MODEL_NAME=gemini-3-pro-image-preview

# 检查配置
curl http://localhost:5000/debug/config
```

### 步骤3：检查日志
```bash
# 如果使用 Docker
docker-compose logs -f app

# 如果直接运行
python app.py 2>&1 | grep "\[API\]"
```

重点关注：
- `Content 类型: <class 'str'>` - 确认返回的是字符串
- `Content 预览:` - 查看返回内容的格式
- `API 返回了文本而不是图片！` - API 返回格式问题

### 步骤4：尝试不同的 API 提供商

如果 apicore 不工作，尝试切换到 12ai：

```bash
export API_PROVIDER=12ai
export MODEL_NAME=gemini-3-pro-image-preview
```

12ai 使用 Gemini 原生 API 格式，可能更稳定。

## 📝 已应用的修复

### 修复1：移除无效参数
```python
# 移除的代码
"strength": 0.75,
"guidance_scale": 7.5,

# 原因：OpenAI 兼容格式可能不支持这些参数
```

### 修复2：增强 Prompt
```python
# 添加的关键约束
CRITICAL CONSTRAINTS:
- DO NOT return the original image
- DO NOT apply simple filters or color adjustments
- MUST generate a completely new image
```

### 修复3：检测文本响应
```python
# 新增检测
if content.strip().startswith(('你好', '您好', 'Hello')):
    print(f"[API] ⚠️ API 返回了文本而不是图片！")
```

## 🔧 手动测试

### 测试1：直接调用 API
```bash
curl -X POST https://api.apicore.ai/v1/chat/completions \
  -H "Authorization: Bearer $NANOBANANA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro-image-preview",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "Generate a professional portrait"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
      ]
    }]
  }'
```

### 测试2：检查响应
如果响应包含：
- ✅ `data:image/png;base64,...` - 正常，是图片
- ❌ 纯文本说明 - API 不支持图像生成
- ❌ 错误信息 - 配置有问题

## 🆘 如果问题仍然存在

1. **更换模型**
   ```bash
   export MODEL_NAME=gemini-2.0-flash-exp
   ```

2. **更换 API 提供商**
   ```bash
   export API_PROVIDER=12ai
   export API_BASE_URL=https://ismaque.org/v1
   ```

3. **检查 API 文档**
   - 联系 API 提供商确认模型是否支持图像生成
   - 确认正确的请求格式

4. **使用模拟模式**
   如果 API 实在无法工作，代码会自动回退到模拟模式（简单背景替换）。

## 📊 预期结果

修复后，成功的情况：
```
[API] Content 长度: 15234
[API] Content 预览: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
[API] 原图大小: 52345 bytes
[API] 生成图片大小: 38421 bytes
[API] ✓ OpenAI 图片生成成功: uploads/xxx_result.png
```

失败的情况：
```
[API] Content 长度: 156
[API] Content 预览: 你好，我是一个AI助手，我可以帮你...
[API] ⚠️ API 返回了文本而不是图片！
[模拟模式] 开始处理图片
```

## 🔗 相关端点

- `GET /debug/config` - 查看配置
- `GET /debug/api` - 查看最后一次 API 调用
- `GET /debug/health` - 健康检查
- `GET /result/<filename>` - 查看生成的图片

## 💡 最佳实践

1. **使用稳定的 API 提供商**：apicore 或 12ai
2. **使用推荐的模型**：`gemini-3-pro-image-preview`
3. **监控日志**：定期查看 `/debug/api` 确认 API 调用正常
4. **设置告警**：如果 API 连续失败，及时切换提供商
