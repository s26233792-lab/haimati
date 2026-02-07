# 🔍 API Payload诊断报告

## 📋 问题总结

经过深入分析，发现了**导致API返回原图的根本原因**：

---

## ❌ 关键问题：extra_body字段

### 问题描述
在OpenAI兼容格式的payload中，使用了`extra_body`字段包装strength等参数：

```python
# ❌ 错误的Payload结构
payload = {
    "model": "gemini-3-pro-image-preview",
    "messages": [...],
    "temperature": 0.9,
    "top_p": 0.95,
    "seed": 12345,
    "max_tokens": 4096,
    "extra_body": {  # ❌ 这个字段导致参数被忽略！
        "strength": 0.75,
        "guidance_scale": 7.5,
        "image_guidance_scale": 1.5
    }
}
```

### 为什么会导致返回原图？

1. **API不认识extra_body**
   - OpenAI兼容格式不支持`extra_body`字段
   - API会忽略这个字段及其中的所有参数

2. **strength参数被忽略**
   - `strength: 0.75` 控制重绘幅度
   - 如果被忽略，API默认使用`strength = 0`
   - `strength = 0` 意味着"不做任何改变"，直接返回原图

3. **即使返回200 OK**
   - API成功处理了请求
   - 但因为strength=0，所以返回原图
   - 用户消耗积分，但图片没有变化

---

## ✅ 修复方案

### 修复后的Payload结构

```python
# ✅ 正确的Payload结构
payload = {
    "model": "gemini-3-pro-image-preview",
    "messages": [...],
    "temperature": 0.9,
    "top_p": 0.95,
    "seed": 12345,
    "max_tokens": 4096,
    # 参数直接在根级别（不使用extra_body）
    "strength": 0.75,  # ✅ 正确：API能识别
    "guidance_scale": 7.5,  # ✅ 正确：API能识别
}
```

### 修复说明

1. **移除extra_body包装**
   - 将参数提升到payload根级别
   - API能正确识别这些参数

2. **移除image_guidance_scale**
   - 这个参数可能不被支持
   - 保留最基本的strength和guidance_scale

3. **添加参数验证**
   - 打印payload中的关键参数
   - 如果参数缺失发出警告

---

## 🧪 验证修复

### 1. 查看日志输出

修复后，你应该看到：

```
[验证] Payload关键参数:
  - strength: 0.75 ❗
  - guidance_scale: 7.5
  - temperature: 0.9
  - seed: 12345
```

如果看到：
```
⚠️ 警告: strength参数未设置，可能导致返回原图！
```
说明参数没有正确设置。

### 2. 对比生成的图片

- ✅ 修复前：生成图片 = 原图（完全一样）
- ✅ 修复后：生成图片 ≠ 原图（应该有变化）

### 3. 检查文件大小

```
[API] 原图大小: XXX bytes
[API] 生成图片大小: YYY bytes
```

如果大小完全相同（误差<100字节），可能还是返回了原图。

---

## 📊 修复历史

| 提交 | 描述 | 时间 |
|------|------|------|
| 4d534bc | 修复API Payload结构 - 移除extra_body | 2026-02-07 |
| d3ad19c | 修复验证码扣减逻辑 | 2026-02-07 |
| ae38e1d | 修复图生图API返回原图问题 | 2026-02-07 |

---

## 🔧 其他发现

### Prompt检查

✅ **Prompt中没有debug信息**
- Prompt内容干净，只包含生成指令
- 没有泄露内部变量或参数
- 格式正确，符合API要求

### MIME类型检测

✅ **已修复**
- 动态检测图片格式（JPEG/PNG/WebP）
- 不再硬编码为`image/jpeg`

---

## ⚠️ 如果修复后仍然返回原图...

### 可能原因1：API不支持strength参数

**解决方案**：
- 查看API文档，确认正确的参数名
- 尝试其他参数名：`denoising_strength`, `init_image_strength`
- 联系API提供商确认图生图支持

### 可能原因2：模型不支持图生图

**解决方案**：
- `gemini-3-pro-image-preview`可能是文生图模型
- 切换到专门的图生图模型：
  - `gemini-3-pro-image-editing`
  - `stability-ai/sdxl-img2img`
  - `midjourney-inpainting`

### 可能原因3：需要不同的API端点

**解决方案**：
- 当前使用：`/v1/chat/completions`
- 尝试使用：`/v1/images/edits` 或 `/v1/img2img`
- 查看API文档确认正确的端点

---

## 📚 参考资源

### OpenAI API图生图格式
通常不直接支持图生图，需要使用专门的端点。

### Stable Diffusion API格式
```python
{
    "init_images": ["base64..."],
    "denoising_strength": 0.75,
    "text_prompts": [{"text": "..."}]
}
```

### Replicate API格式
```python
{
    "image": "base64...",
    "prompt": "...",
    "strength": 0.75
}
```

---

## 🎯 下一步行动

1. **测试修复效果**
   - 上传图片生成
   - 查看日志中的参数验证
   - 对比生成结果

2. **如果仍有问题**
   - 记录完整的API请求/响应
   - 查看API文档
   - 联系API提供商

3. **考虑切换API**
   - 如果当前API不支持图生图
   - 切换到Stability AI或Replicate
   - 这些API明确支持img2img功能

---

*诊断报告生成时间：2026-02-07*
*修复提交：4d534bc*
