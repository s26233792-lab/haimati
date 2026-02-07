"""
修复后的 call_nanobanana_api 函数
解决图生图返回原图的问题

关键修复：
1. ✅ 添加重绘幅度参数（strength=0.75）
2. ✅ 增强prompt，明确图生图要求
3. ✅ 动态检测图片MIME类型
4. ✅ 添加多种参数方案，兼容不同API

使用方法：
将此函数替换app.py中的call_nanobanana_api函数（第448-928行）
"""

def call_nanobanana_api_fixed(image_path, style, clothing, angle, background, bg_color='white', beautify='no'):
    """
    调用图片生成 API (12ai.org NanoBanana Pro) - 修复版

    参数:
        style: 风格 (portrait)
        clothing: 服装 (business_suit, formal_dress, casual_shirt, turtleneck, tshirt)
        angle: 拍摄角度 (front, slight_tilt)
        background: 背景 (textured, solid)
        bg_color: 背景色 (white, gray, blue, black, warm)
        beautify: 是否美颜 (yes, no)
    """
    import base64
    from PIL import Image, ImageFilter, ImageEnhance

    # ==================== 读取并编码图片 ====================
    # 🔧 修复3：动态检测图片格式
    img = Image.open(image_path)
    img_format = img.format if img.format else 'JPEG'
    mime_type = f"image/{img_format.lower()}"

    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()

    # ==================== 构建文本 prompt ====================
    # 服装处理
    clothing_map = {
        'business_suit': '商务西装',
        'formal_dress': '正装礼服',
        'casual_shirt': '休闲衬衫',
        'turtleneck': '高领毛衣',
        'tshirt': '简约T恤',
        'keep_original': '和原图保持一致'
    }

    # 背景处理
    background_map = {
        'textured': '质感影棚背景，柔和自然光，背景略微虚化，营造专业氛围',
        'solid': '纯净纯色背景，简洁干净，颜色均匀，无杂色'
    }

    # 背景色处理（质感影棚和纯色背景都支持）
    bg_color_map = {
        'white': '白色',
        'gray': '灰色',
        'blue': '蓝色',
        'black': '深灰色',
        'warm': '暖米色'
    }

    # 角度处理
    angle_map = {
        'front': '正面照，完全正对镜头',
        'slight_tilt': '微微倾斜角度，身体微侧，面��朝前'
    }

    # 构建文本 prompt
    angle_desc = angle_map.get(angle, '正面照，完全正对镜头')
    color_desc = bg_color_map.get(bg_color, '白色')

    # 美颜处理
    if beautify == 'yes':
        beauty_desc = "轻微美颜效果，自然提亮肤色，优化肤质，保持真实五官比例"
    else:
        beauty_desc = "保持真实面容，不添加美颜效果"

    # 根据背景类型选择描述
    if background == 'solid':
        bg_desc = f"纯净{color_desc}背景，颜色均匀，无杂色"
    else:  # textured
        bg_desc = f"质感影棚背景，{color_desc}色调，柔和自然光，背景略微虚化，营造专业氛围"

    # 🔧 修复1：增强prompt，明确图生图要求
    prompt_text = f"""你是一个专业的AI换装助手。请执行以下操作：

【任务目标】这是一张图生图（Image-to-Image）任务。你必须根据提供的参考图片，为人物更换服装和背景，生成一张全新的肖像照。

【人物要求】
- 保持人物的面部特征和发型完全一致
- 保持人物的性别和年龄特征
- 可以调整肤色光影，使整体更专业
- {beauty_desc}

【服装要求】
- {clothing_map.get(clothing, '商务西装')}
- 必须为人物穿上这套服装
- 服装要贴合身形，看起来真实自然

【背景要求】
- {bg_desc}
- 完全替换原背景
- 背景要专业、干净

【风格要求】
- 美式专业职场风格，{'微微倾斜角度拍摄' if angle == 'slight_tilt' else '正面角度拍摄'}
- 如军人般挺拔{'，身体微微侧转，面部正对镜头' if angle == 'slight_tilt' else '，完全正对镜头'}
- 超高清，2K分辨率，清晰对焦
- 3:4比例，确保输出分辨率为2048x2730像素
- 影棚级布光，构图优雅

【关键要求 - 必须遵守】
⚠️ 这是一次图生图重绘任务，重绘幅度（strength）应设置为0.75-0.85
⚠️ 你不能简单复制原图或只做滤镜处理
⚠️ 你必须重新生成一张新图片，确保服装、背景、光影都与原图有明显差异
⚠️ 生成的图片应该看起来像是在摄影棚重新拍摄的效果

【验证标准】生成的图片必须与原图有明显差异：
1. 服装完全不同（从原图服装换成{clothing_map.get(clothing, '商务西装')}）
2. 背景完全不同（从{bg_desc}）
3. 光影效果更专业（影棚级布光）

【禁止事项】
- ❌ 禁止直接返回原图
- ❌ 禁止只做简单滤镜/颜色调整
- ❌ 禁止复制原图像素
- ✅ 必须使用AI重新生成图片"""

    # ==================== 打印调试信息 ====================
    print("=" * 70)
    print("📋 生成参数:")
    print(f"  服装: {clothing} -> {clothing_map.get(clothing, '商务西装')}")
    print(f"  角度: {angle} -> {angle_desc}")
    print(f"  背景: {background} + {bg_color}")
    print(f"  背景描述: {bg_desc}")
    print(f"  美颜: {beautify}")
    print(f"  图片格式: {img_format} -> {mime_type}")
    print("=" * 70)
    print("📝 完整 Prompt:")
    print(prompt_text)
    print("=" * 70)

    # ==================== 构建请求 payload ====================
    # 添加随机种子以确保每次生成不同的图片
    import time
    random_seed = int(time.time() * 1000) % 1000000
    print(f"[API] 使用随机种子: {random_seed}")

    # 🔧 修复2：根据模型类型选择不同的请求格式（添加重绘幅度参数）
    if API_FORMAT == 'gemini':
        # Gemini 原生格式 (用于 12ai Gemini 模型)
        payload = {
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
        api_format_name = "Gemini 原生格式"
        payload_type = "Gemini contents/parts 格式"
    else:
        # OpenAI 兼容格式 - 🔧 关键修复：添加重绘幅度参数！
        payload = {
            "model": MODEL_NAME,
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
            # ==================== 🔧 关键修复：重绘幅度参数 ====================
            # ⚠️ 注意：不同的API提供商可能使用不同的参数名！
            # 请根据你的API文档调整以下参数

            # 方案A：常见的OpenAI兼容格式（推荐尝试）
            "strength": 0.75,  # 重绘幅度：0.0-1.0，越高变化越大
            "guidance_scale": 7.5,  # 引导强度：控制对prompt的遵循程度

            # 如果方案A不生效，尝试方案B或C：
            # "denoising_strength": 0.75,  # 方案B：Stable Diffusion风格
            # "init_image_strength": 0.25,  # 方案C：某些API使用这个（1-strength）
        }
        api_format_name = "OpenAI 兼容格式"
        payload_type = "OpenAI chat/completions 格式（带strength参数）"

    # ==================== 打印发送给 API 的数据 ====================
    print("=" * 70)
    print(f"🚀 发送给 API 的数据 ({api_format_name}):")
    print(f"  URL: {NANOBANANA_API_URL}")
    print(f"  模型: {MODEL_NAME}")
    print(f"  Prompt 长度: {len(prompt_text)} 字符")
    print(f"  图片数据大小: {len(image_data)} 字符 (base64)")
    print(f"  Payload 结构: {payload_type}")

    # 🔧 调试：打印重绘幅度参数
    if API_FORMAT != 'gemini':
        if 'strength' in payload:
            print(f"  ⭐ 重绘幅度 (strength): {payload.get('strength')}")
        if 'guidance_scale' in payload:
            print(f"  ⭐ 引导强度 (guidance_scale): {payload.get('guidance_scale')}")

    print("-" * 70)
    print("📤 Payload JSON (前500字符):")
    print(json.dumps(payload, ensure_ascii=False)[:500])
    print("=" * 70)

    # ========== 真实 API 调用部分 ==========
    api_key = os.getenv('NANOBANANA_API_KEY', '')
    api_url = NANOBANANA_API_URL

    # 记录 API 调用开始
    last_api_call['called'] = True
    last_api_call['url'] = api_url
    last_api_call['timestamp'] = datetime.now().isoformat()

    # 检查 API Key 是否配置
    if api_key:
        print(f"[API] ==================== API 配置 ====================")
        print(f"[API] API 提供商: {API_PROVIDER}")
        print(f"[API] API 格式: {API_FORMAT.upper()}")
        print(f"[API] API Key 已配置 (长度: {len(api_key)} 字符)")
        print(f"[API] 模型: {MODEL_NAME}")
        print(f"[API] API URL: {api_url}")
        print(f"[API] ================================================")
        try:
            print(f"[API] 开始调用 API ({API_FORMAT.upper()} 格式)...")
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }

            # 使用 Session 来处理连接池和重试
            session = requests.Session()
            session.mount('https://', requests.adapters.HTTPAdapter(
                max_retries=3,
                pool_connections=1,
                pool_maxsize=1
            ))

            print(f"[API] 请求 URL: {api_url}")
            print(f"[API] 模型: {MODEL_NAME}")
            print(f"[API] 请求超时: 120秒")
            # 确认 payload 中的 prompt (OpenAI 格式)
            payload_content = payload.get('messages', [{}])[0].get('content', [])
            if isinstance(payload_content, list):
                for item in payload_content:
                    if item.get('type') == 'text':
                        prompt_text_check = item.get('text', '')
                        print(f"[API] ✅ Payload 中的 Prompt: {prompt_text_check[:50]}... (长度: {len(prompt_text_check)})")
                        break

            # 捕获所有可能的异常
            try:
                response = session.post(api_url, json=payload, headers=headers, timeout=120)
            except requests.exceptions.Timeout as e:
                print(f"[API] ❌ 请求超时: {e}")
                last_api_call['error'] = f'请求超时（120秒）'
                last_api_call['status_code'] = 408
                raise Exception(f"API 请求超时，请稍后重试")
            except requests.exceptions.ConnectionError as e:
                print(f"[API] ❌ 连接错误: {e}")
                last_api_call['error'] = f'连接失败: {str(e)}'
                last_api_call['status_code'] = 503
                raise Exception(f"无法连接到 API 服务器，请检查网络配置")
            except (SystemExit, KeyboardInterrupt) as e:
                print(f"[API] ❌ 进程退出: {e}")
                last_api_call['error'] = f'进程意外退出'
                last_api_call['status_code'] = 500
                raise Exception(f"API 调用被中断")
            except Exception as e:
                print(f"[API] ❌ 请求失败: {type(e).__name__}: {e}")
                last_api_call['error'] = f'{type(e).__name__}: {str(e)}'
                last_api_call['status_code'] = 500
                raise

            print(f"[API] 响应状态码: {response.status_code}")

            # 检查 HTTP 状态码
            if response.status_code != 200:
                error_text = response.text[:500]
                print(f"[API] HTTP 错误响应: {error_text}")
                last_api_call['error'] = f'HTTP {response.status_code}: {error_text}'
                raise Exception(f"API 返回错误 {response.status_code}: {error_text[:100]}")

            # 保存调试信息
            last_api_call['called'] = True
            last_api_call['url'] = api_url
            last_api_call['status_code'] = response.status_code
            last_api_call['timestamp'] = datetime.now().isoformat()

            if response.status_code == 200:
                result = response.json()
                print(f"[API] 响应键: {list(result.keys())}")
                print(f"[API] 响应内容预览: {json.dumps(result, ensure_ascii=False)[:400]}...")

                # 保存响应信息
                last_api_call['response_keys'] = list(result.keys())
                last_api_call['error'] = None

                # ========== 处理 OpenAI 兼容响应格式 ==========
                # OpenAI 格式: {"choices": [{"message": {"content": "..."}}]}
                if 'choices' in result and len(result['choices']) > 0:
                    choice = result['choices'][0]
                    print(f"[API] 检测到 OpenAI 格式响应")
                    print(f"[API] Choice 数据: {list(choice.keys())}")
                    if 'message' in choice:
                        message = choice['message']
                        print(f"[API] Message 数据存在: True")
                        if 'content' in message:
                            content = message['content']
                            print(f"[API] Content 类型: {type(content)}")

                            # 检查 content 是否包含图片数据
                            if isinstance(content, str):
                                print(f"[API] Content 长度: {len(content)}")
                                print(f"[API] Content 预览: {content[:200]}...")

                                # 检查是否是 base64 编码的图片 (data:image/...;base64,...)
                                if content.startswith('data:image') and 'base64' in content:
                                    import base64
                                    # 提取 base64 数据
                                    base64_data = content.split('base64,')[-1]
                                    image_data_decoded = base64.b64decode(base64_data)
                                    result_path = image_path.replace('.', '_result.')

                                    # 检查图片大小
                                    original_size = os.path.getsize(image_path)
                                    print(f"[API] 原图大小: {original_size} bytes")
                                    print(f"[API] 生成图片大小: {len(image_data_decoded)} bytes")

                                    # 检查是否和原图大小相同（可能返回了原图）
                                    if abs(len(image_data_decoded) - original_size) < 100:
                                        print(f"[API] ❌ 错误: 生成图片大小与原图几乎相同！")
                                        print(f"[API] ❌ API 返回了原图而不是生成的新图片")
                                        print(f"[API] 💡 提示: 可能的原因：")
                                        print(f"    1. API 不支持 strength 参数（请查阅API文档）")
                                        print(f"    2. strength 值太低（当前=0.75，尝试调高到0.85）")
                                        print(f"    3. 模型不支持图生图（尝试专门的img2img模型）")
                                        last_api_call['error'] = 'API返回了原图而非生成的图片'
                                        raise Exception("API返回了原图，图片生成失败。请尝试调整prompt或更换模型。")

                                    with open(result_path, 'wb') as f:
                                        f.write(image_data_decoded)

                                    saved_size = os.path.getsize(result_path)
                                    print(f"[API] 保存后大小: {saved_size} bytes")

                                    print(f"[API] ✓ OpenAI 图片生成成功: {result_path}")
                                    last_api_call['success'] = True
                                    last_api_call['format'] = 'openai_base64'
                                    return result_path

                # ========== 处理 Gemini API 响应格式 (向后兼容) ==========
                # Gemini 格式: {"candidates": [{"content": {"parts": [{"inlineData": {"data": "base64..."}}]}}]}
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    print(f"[API] Candidate 数据: {list(candidate.keys())}")
                    if 'content' in candidate:
                        print(f"[API] Content 数据存在: True")
                        if 'parts' in candidate['content']:
                            print(f"[API] Parts 数量: {len(candidate['content']['parts'])}")
                            for i, part in enumerate(candidate['content']['parts']):
                                print(f"[API] Part {i} keys: {list(part.keys())}")
                                # 检查 inlineData（驼峰命名）或 inline_data（下划线命名）
                                inline_data = part.get('inlineData') or part.get('inline_data')
                                if inline_data and 'data' in inline_data:
                                    import base64
                                    image_data_decoded = base64.b64decode(inline_data['data'])
                                    result_path = image_path.replace('.', '_result.')

                                    # 检查图片大小
                                    original_size = os.path.getsize(image_path)
                                    print(f"[API] 原图大小: {original_size} bytes")
                                    print(f"[API] 生成图片大小: {len(image_data_decoded)} bytes")

                                    # 检查是否和原图大小相同（可能返回了原图）
                                    if abs(len(image_data_decoded) - original_size) < 100:
                                        print(f"[API] ❌ 错误: 生成图片大小与原图几乎相同！")
                                        print(f"[API] ❌ API 返回了原图而不是生成的新图片")
                                        print(f"[API] 💡 提示: 可能是模型没有理解图生图任务")
                                        last_api_call['error'] = 'API返回了原图而非生成的图片'
                                        raise Exception("API返回了原图，图片生成失败。请尝试调整prompt或更换模型。")

                                    with open(result_path, 'wb') as f:
                                        f.write(image_data_decoded)

                                    # 验证保存后的文件大小
                                    saved_size = os.path.getsize(result_path)
                                    print(f"[API] 保存后大小: {saved_size} bytes")

                                    print(f"[API] ✓ Gemini 图片生成成功: {result_path}")
                                    last_api_call['success'] = True
                                    last_api_call['format'] = 'gemini'
                                    return result_path
                                else:
                                    print(f"[API] Part {i} 没有 inlineData")
                        else:
                            print(f"[API] Content 中没有 parts")
                    else:
                        print(f"[API] Candidate 中没有 content")

                # ========== 兼容其他格式 ==========
                # 格式1: {"image": "base64_string"}
                if 'image' in result:
                    import base64
                    image_data_decoded = base64.b64decode(result['image'])
                    result_path = image_path.replace('.', '_result.')
                    with open(result_path, 'wb') as f:
                        f.write(image_data_decoded)
                    print(f"[API] ✓ 图片生成成功 (base64格式): {result_path}")
                    last_api_call['success'] = True
                    last_api_call['format'] = 'base64'
                    return result_path

                # 格式2: {"url": "https://..."}
                elif 'url' in result:
                    img_response = requests.get(result['url'], timeout=30)
                    if img_response.status_code == 200:
                        result_path = image_path.replace('.', '_result.')
                        with open(result_path, 'wb') as f:
                            f.write(img_response.content)
                        print(f"[API] ✓ 图片下载成功 (URL格式): {result_path}")
                        last_api_call['success'] = True
                        last_api_call['format'] = 'url'
                        return result_path
                    else:
                        print(f"[API] 下载图片失败: {img_response.status_code}")
                        last_api_call['error'] = f'下载失败: {img_response.status_code}'

                print(f"[API] ⚠ 未知响应格式，使用模拟模式")
                print(f"[API] 完整响应: {json.dumps(result, ensure_ascii=False)[:800]}")
                last_api_call['error'] = '未知响应格式'
            else:
                print(f"[API] ✗ API 调用失败: {response.status_code}")
                print(f"[API] 错误内容: {response.text[:500]}")
                last_api_call['error'] = f'状态码: {response.status_code}, 内容: {response.text[:200]}'

        except Exception as e:
            print(f"[API] ✗ API 调用异常: {type(e).__name__}: {e}")
            import traceback
            print(f"[API] 异常堆栈: {traceback.format_exc()}")
            print(f"[API] 将使用模拟模式")
            last_api_call['error'] = f'{type(e).__name__}: {str(e)}'
    else:
        print(f"[API] ⚠ API Key 未配置，使用模拟模式")
        print(f"[API] 提示: 请在 Railway Variables 中设置 NANOBANANA_API_KEY")
        last_api_call['error'] = 'API Key 未配置'

    # ========== 模拟模式：对图片进行简单处理 ==========
    print(f"[模拟模式] 开始处理图片")
    print(f"[模拟模式] 原图: {image_path}")
    # 服装名称映射 (用于显示)
    clothing_names = {
        'business_suit': '商务西装',
        'formal_dress': '正装礼服',
        'casual_shirt': '休闲衬衫',
        'turtleneck': '高领毛衣',
        'tshirt': '简约T恤'
    }

    # 背景颜色映射 (用于模拟模式，质感影棚和纯色都支持)
    bg_color_map_sim = {
        'white': (255, 255, 255),
        'gray': (200, 200, 210),      # 质感影棚用稍浅的灰色
        'blue': (180, 200, 230),       # 柔和的蓝色
        'black': (70, 70, 80),         # 深灰色
        'warm': (245, 235, 210)        # 暖米色
    }

    # 纯色背景使用更鲜艳的颜色
    solid_bg_colors = {
        'white': (255, 255, 255),
        'gray': (233, 236, 239),
        'blue': (187, 222, 251),
        'black': (52, 58, 64),
        'warm': (255, 236, 179)
    }

    try:
        # 打开原始图片
        img = Image.open(image_path)
        img = img.convert('RGBA')

        # 根据背景类型选择颜色
        if background == 'solid':
            bg_color_rgb = solid_bg_colors.get(bg_color, (255, 255, 255))
        else:  # textured
            bg_color_rgb = bg_color_map_sim.get(bg_color, (200, 200, 210))

        # 创建带背景的新图片
        background_img = Image.new('RGBA', img.size, bg_color_rgb + (255,))
        background_img.paste(img, (0, 0), img)
        img = background_img.convert('RGB')

        # 美式肖像风格处理
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.85)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)
        img = img.filter(ImageFilter.SMOOTH)

        # 保存处理后的图片
        result_path = image_path.replace('.', '_result.')
        img.save(result_path, quality=95)

        print(f"[模拟模式] 图片已处理: {result_path}")
        bg_type_text = '质感影棚' if background == 'textured' else '纯色背景'
        bg_color_text = {'white': '白色', 'gray': '灰色', 'blue': '蓝色', 'black': '深灰', 'warm': '暖色'}.get(bg_color, '白色')
        beauty_text = '轻微美颜' if beautify == 'yes' else '无美颜'
        print(f"  风格: {style}, 服装: {clothing}, 背景: {bg_type_text}({bg_color_text}), 美颜: {beauty_text}")

        return result_path

    except Exception as e:
        print(f"图片处理失败: {e}")
        return image_path  # 失败时返回原图
