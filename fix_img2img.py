"""
图生图API修复补丁
解决图片生成后与原图相同的问题

问题分析：
1. ❌ 缺少重绘幅度参数（strength/denoising_strength）
2. ❌ Prompt中没有明确要求图生图任务
3. ⚠️ Base64 MIME类型硬编码为jpeg

修复方案：
- ���加strength参数（0.75-0.85）
- 增强prompt，明确图生图要求
- 动态检测图片格式
"""

# ============== 修复1：增强Prompt ==============
IMPROVED_PROMPT_TEMPLATE = """你是一个专业的AI换装助手。请执行以下操作：

【任务目标】这是一张图生图（Image-to-Image）任务。你必须根据提供的参考图片，为人物更换服装和背景，生成一张全新的肖像照。

【人物要求】
- 保持人物的面部特征和发型完全一致
- 保持人物的性别和年龄特征
- 可以调整肤色光影，使整体更专业
- {beauty_desc}

【服装要求】
- {clothing}
- 必须为人物穿上这套服装
- 服装要贴合身形，看起来真实自然

【背景要求】
- {bg_desc}
- 完全替换原背景
- 背景要专业、干净

【风格要求】
- 美式专业职场风格，{angle_desc}
- 如军人般挺拔{pose_desc}
- 超高清，2K分辨率，清晰对焦
- 3:4比例，确保输出分辨率为2048x2730像素
- 影棚级布光，构图优雅

【关键要求 - 必须遵守】
⚠️ 这是一次图生图重绘任务，重绘幅度（strength）应设置为0.75-0.85
⚠️ 你不能简单复制原图或只做滤镜处理
⚠️ 你必须重新生成一张新图片，确保服装、背景、光影都与原图有明显差异
⚠️ 生成的图片应该看起来像是在摄影棚重新拍摄的效果

【验证标准】生成的图片必须与原图有明显差异：
1. 服装完全不同（从原图服装换成{clothing}）
2. 背景完全不同（从{bg_desc}）
3. 光影效果更专业（影棚级布光）

【禁止事项】
- ❌ 禁止直接返回原图
- ❌ 禁止只做简单滤镜/颜色调整
- ❌ 禁止复制原图像素
- ✅ 必须使用AI重新生成图片
"""

# ============== 修复2：添加重绘幅度参数 ==============
def get_fixed_payload(api_format, model_name, prompt_text, image_data, mime_type, random_seed):
    """返回修复后的payload，包含重绘幅度参数"""

    if api_format == 'gemini':
        # Gemini原生格式
        return {
            "contents": [{
                "parts": [
                    {"text": prompt_text},
                    {"inline_data": {"mime_type": mime_type, "data": image_data}}
                ]
            }],
            "generationConfig": {
                "temperature": 0.9,
                "topP": 0.95,
                "responseModalities": ["IMAGE"],
                "imageFormat": "PNG",
                # 添加重绘幅度控制
                "sampleCount": 1,
                "aspectRatio": "3:4"
            }
        }
    else:
        # OpenAI兼容格式 - 关键修复！
        return {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}}
                    ]
                }
            ],
            "temperature": 0.9,
            "top_p": 0.95,
            "seed": random_seed,
            "max_tokens": 4096,
            # ==================== 关键修复：添加重绘幅度参数 ====================
            # 注意：不同的API提供商可能使用不同的参数名
            # 以下是常见的参数名称，你需要根据你的API文档调整
            "extra_body": {
                # 方案1：常见的重绘幅度参数
                "strength": 0.75,  # 重绘幅度：0.0-1.0，越高变化越大

                # 方案2：如果上面的不生效，尝试这些参数：
                # "denoising_strength": 0.75,  # Stable Diffusion风格
                # "init_image_strength": 0.25,  # 有些API用这个（1-strength）

                # 引导参数
                "guidance_scale": 7.5,  # 引导强度：控制对prompt的遵循程度
                "image_guidance_scale": 1.5  # 图像引导强度：控制对原图的保留程度
            }
        }

# ============== 修复3：MIME类型动态检测 ==============
def get_mime_type(image_path):
    """动态检测图片的MIME类型"""
    from PIL import Image
    img_format = Image.open(image_path).format
    return f"image/{img_format.lower()}" if img_format else "image/jpeg"

# ============== 使用说明 ==============
"""
在 app.py 的 call_nanobanana_api 函数中应用修复：

1. 替换prompt构建部分（第519-551行）：
   使用 IMPROVED_PROMPT_TEMPLATE 模板

2. 在读取图片后添加MIME类型检测（第464行之后）：
   mime_type = get_mime_type(image_path)

3. 替换payload构建部分（第571-606行）：
   使用 get_fixed_payload() 函数

4. 如果extra_body不生效，尝试这些方案：

   方案A：将参数放在payload根级别
   payload["strength"] = 0.75
   payload["guidance_scale"] = 7.5

   方案B：某些API使用不同的参数名
   payload["denoising_strength"] = 0.75
   payload["cfg_scale"] = 7.5

   方案C：联系API提供商确认图生图参数名
"""

# ============== 调试步骤 ==============
"""
1. 先打印payload，确认参数已添加：
   print(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}")

2. 检查API文档，确认正确的参数名：
   - OpenAI API: 通常不支持图生图
   - Stability AI: 使用 `strength`
   - Replicate: 使用 `strength`
   - 12ai.org: 需要查看他们的文档

3. 如果API不支持图生图，考虑：
   - 更换为专门的图生图模型
   - 使用Stable Diffusion的img2img端点
   - 使用Replicate或RunPod的图生图API
"""

if __name__ == "__main__":
    print(__doc__)
    print("\n" + "="*70)
    print("请按照上述步骤在app.py中应用修复")
    print("="*70)
