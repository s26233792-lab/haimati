# 🔧 图生图API修复报告

## 📋 问题诊断总结

经过详细代码审查，发现了**3个关键问题**导致API返回原图：

---

## ❌ 问题1：缺少重绘幅度参数（最关键！）

**位置**：`app.py` 第571-606行

**问题描述**：
- 你的payload中**完全没有设置重绘幅度参数**
- 缺少的关键参数：
  - `strength`：重绘幅度（0.0-1.0）
  - `denoising_strength`：去噪强度
  - `guidance_scale`：引导强度

**影响**：
- API可能默认 `strength=0`，导致直接返回原图
- 即使API返回200，积分被扣除，但图片没有任何变化

**修复方案**：
```python
# OpenAI兼容格式payload需要添加：
payload = {
    "model": MODEL_NAME,
    "messages": [...],
    "temperature": 0.9,
    "top_p": 0.95,
    "seed": random_seed,
    "max_tokens": 4096,

    # 🔧 添加重绘幅度参数
    "strength": 0.75,  # 重绘幅度：0.0-1.0，越高变化越大
    "guidance_scale": 7.5,  # 引导强度
}
```

---

## ⚠️ 问题2：Prompt没有明确图生图要求

**位置**：`app.py` 第519-551行

**问题描述**：
- 原prompt说"根据参考图片生成"，但没有明确要求"重新生成"
- 模型可能理解为"基于这张图"，导致返回原图

**修复方案**：
```python
prompt_text = f"""
【任务目标】这是一张图生图（Image-to-Image）任务。你必须根据提供的参考图片，为人物更换服装和背景，生成一张全新的肖像照。

【关键要求 - 必须遵守】
⚠️ 这是一次图生图重绘任务，重绘幅度（strength）应设置为0.75-0.85
⚠️ 你不能简单复制原图或只做滤镜处理
⚠️ 你必须重新生成一张新图片，确保服装、背景、光影都与原图有明显差异

【禁止事项】
- ❌ 禁止直接返回原图
- ❌ 禁止只做简单滤镜/颜色调整
- ✅ 必须使用AI重新生成图片
"""
```

---

## ⚠️ 问题3：MIME类型硬编码

**位置**：`app.py` 第575行和第596行

**问题描述**：
```python
{"inline_data": {"mime_type": "image/jpeg", "data": image_data}}  # 硬编码为jpeg
{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}  # 硬编码为jpeg
```

**影响**：
- 如果用户上传PNG或WebP，API可能无法正确识别

**修复方案**：
```python
# 动态检测图片格式
from PIL import Image
img = Image.open(image_path)
img_format = img.format if img.format else 'JPEG'
mime_type = f"image/{img_format.lower()}"

# 使用动态mime_type
{"inline_data": {"mime_type": mime_type, "data": image_data}}
{"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}}
```

---

## 📦 修复文件说明

我为你创建了3个文件：

### 1. `fix_img2img.py`
- 包含修复建议和代码模板
- 详细的参数说明
- 调试步骤指南

### 2. `app_fixed.py`
- 完整的修复版 `call_nanobanana_api` 函数
- 包含所有3个修复
- 可以直接替换原函数

### 3. `IMAGE_TO_IMAGE_FIX_REPORT.md` (本文件)
- 完整的问题诊断报告
- 修复方案说明
- 使用指南

---

## 🚀 快速修复步骤

### 方案A：使用修复版函数（推荐）

1. **备份原文件**：
```bash
cp app.py app_backup.py
```

2. **提取修复函数**：
从 `app_fixed.py` 复制 `call_nanobanana_api_fixed` 函数

3. **替换原函数**：
在 `app.py` 中找到第448行的 `call_nanobanana_api` 函数，替换为修复版

4. **测试**：
```bash
python app.py
```

### 方案B：手动修改（如果方案A不生效）

**步骤1：修改payload构建（第589-606行）**

找到这部分代码：
```python
payload = {
    "model": MODEL_NAME,
    "messages": [...],
    "temperature": 0.9,
    "top_p": 0.95,
    "seed": random_seed,
    "max_tokens": 4096
}
```

修改为：
```python
payload = {
    "model": MODEL_NAME,
    "messages": [...],
    "temperature": 0.9,
    "top_p": 0.95,
    "seed": random_seed,
    "max_tokens": 4096,

    # 🔧 添加重绘幅度参数
    "strength": 0.75,
    "guidance_scale": 7.5,
}
```

**步骤2：增强prompt（第519-551行）**

参考 `fix_img2img.py` 中的 `IMPROVED_PROMPT_TEMPLATE`

**步骤3：添加MIME类型检测（第464行后）**

```python
# 动态检测图片格式
from PIL import Image
img = Image.open(image_path)
img_format = img.format if img.format else 'JPEG'
mime_type = f"image/{img_format.lower()}"
```

---

## ⚠️ 重要提醒

### 如果修复后仍然返回原图...

**可能原因1：API不支持strength参数**
- OpenAI的chat/completions API可能不支持图生图
- 需要查看你的API提供商文档

**解决方案**：
- 联系API提供商确认正确的参数名
- 尝试使用专门的图生图端点（如 `/v1/images/edits`）
- 考虑切换到支持图生图的API：
  - Stability AI (img2img)
  - Replicate
  - RunPod

**可能原因2：模型不支持图生图**
- `gemini-3-pro-image-preview` 可能是文生图模型
- 需要专门的img2img模型

**解决方案**：
- 尝试使用 `gemini-3-pro-image-editing`（如果有）
- 切换到Stable Diffusion的img2img模型
- 使用Midjourney的inpainting功能

**可能原因3：参数格式错误**
- 不同的API使用不同的参数格式

**常见的参数名**：
```python
# 方案A
"strength": 0.75

# 方案B
"denoising_strength": 0.75

# 方案C
"init_image_strength": 0.25  # 1 - strength

# 方案D（放在extra_body中）
"extra_body": {
    "strength": 0.75
}
```

---

## 🔍 调试技巧

### 1. 打印payload
```python
print(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}")
```

### 2. 检查响应
```python
print(f"[DEBUG] Response keys: {result.keys()}")
print(f"[DEBUG] Response: {json.dumps(result, indent=2)[:500]}")
```

### 3. 对比图片大小
```python
original_size = os.path.getsize(image_path)
generated_size = os.path.getsize(result_path)
print(f"[DEBUG] 原图: {original_size} bytes, 生成图: {generated_size} bytes")
```

### 4. 访问调试端点
```
http://localhost:5000/debug/config
http://localhost:5000/debug/api
```

---

## 📚 参考文档

### OpenAI兼容API图生图格式
通常使用以下格式之一：
```python
# 格式1：参数在payload根级别
{
    "model": "model-name",
    "prompt": "...",
    "init_images": ["base64..."],
    "strength": 0.75
}

# 格式2：使用image字段
{
    "model": "model-name",
    "messages": [...],
    "image": "base64...",
    "strength": 0.75
}

# 格式3：Stable Diffusion API格式
{
    "init_images": ["base64..."],
    "denoising_strength": 0.75,
    "text_prompts": [{"text": "..."}]
}
```

---

## 📞 需要进一步帮助？

如果以上修复都不生效，请提供：
1. API提供商名称和文档链接
2. 完整的API请求日志（payload）
3. 完整的API响应日志
4. 使用的模型名称

我会帮你进一步分析。

---

*修复报告生成时间：2026-02-07*
*Claude Code - AI Assistant*
