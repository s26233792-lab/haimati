"""
英文版Instructional Prompting生成器
符合AI图像生成的最佳实践
"""

def generate_english_prompt(clothing='business_suit', angle='front',
                           background='textured', bg_color='white',
                           beautify='no'):
    """
    生成符合Instructional Prompting规范的英文Prompt

    Instructional Prompting原则：
    1. 使用祈使句（动词开头）
    2. 清晰、简洁、具体
    3. 按重要性排序
    4. 避免模糊表述
    5. 包含技术规格
    """

    # 服装映射（英文）
    clothing_map = {
        'business_suit': 'professional business suit',
        'formal_dress': 'formal dress attire',
        'casual_shirt': 'casual button-down shirt',
        'turtleneck': 'elegant turtleneck sweater',
        'tshirt': 'simple minimalist t-shirt',
        'keep_original': 'original clothing'
    }

    # 背景映射（英文）
    background_map = {
        'textured': 'textured studio background with soft natural lighting, subtle depth of field, professional atmosphere',
        'solid': 'clean solid color background, uniform color, minimal and clean'
    }

    # 背景色映射（英文）
    bg_color_map = {
        'white': 'white',
        'gray': 'gray',
        'blue': 'soft blue',
        'black': 'dark charcoal',
        'warm': 'warm cream'
    }

    # 角度映射（英文）
    angle_map = {
        'front': 'front-facing portrait, looking directly at camera',
        'slight_tilt': 'slight tilt angle, body slightly turned, face toward camera'
    }

    # 美颜映射（英文）
    beautify_map = {
        'yes': 'SUBTLE BEAUTIFICATION: natural skin brightening, refined skin texture, maintain realistic facial proportions',
        'no': 'NO RETOUCHING: preserve authentic appearance without beauty enhancements'
    }

    # 构建描述
    clothing_desc = clothing_map.get(clothing, 'professional business suit')
    color_desc = bg_color_map.get(bg_color, 'white')
    angle_desc = angle_map.get(angle, 'front-facing portrait')
    beautify_desc = beautify_map.get(beautify, 'NO RETOUCHING: preserve authentic appearance')

    # 背景描述
    if background == 'solid':
        bg_desc = f"clean solid {color_desc} background, uniform color tone"
    else:
        bg_desc = f"textured studio background in {color_desc} tones, soft professional lighting, subtle bokeh effect"

    # 生成英文Instructional Prompt
    prompt = f"""GENERATE A PROFESSIONAL PORTRAIT PHOTO USING THE FOLLOWING INSTRUCTIONS:

TASK: Image-to-Image Transformation
Create a new professional portrait by changing the subject's clothing and background while preserving facial identity and features.

SUBJECT REQUIREMENTS:
- MAINTAIN exact facial features and hairstyle from reference image
- PRESERVE subject's gender and age characteristics
- OPTIMIZE skin tone lighting for professional appearance
- {beautify_desc}

CLOTHING INSTRUCTIONS:
- DRESS subject in {clothing_desc}
- ENSURE proper fit with natural draping
- CREATE realistic appearance with appropriate folds and textures

BACKGROUND INSTRUCTIONS:
- REPLACE original background completely
- USE {bg_desc}
- MAINTAIN clean and professional aesthetic

COMPOSITION AND STYLE:
- COMPOSE professional American-style portrait
- POSITION subject in {angle_desc}
- DIRECT subject to stand tall with military-grade posture
- SET ultra-high 2K resolution with sharp focus
- FRAME at 3:4 aspect ratio (2048x2730 pixels)
- LIGHT with studio-grade lighting setup
- CREATE elegant and balanced composition

CRITICAL CONSTRAINTS:
- DO NOT return the original image
- DO NOT apply simple filters or color adjustments
- MUST generate a completely new image
- MUST visibly differ from original: different clothing, different background, different lighting

QUALITY VERIFICATION:
Generated image MUST show clear differences from original:
1. Completely different clothing ({clothing_desc})
2. Completely different background ({bg_desc})
3. Professional studio-quality lighting

TECHNICAL SPECIFICATIONS:
- Resolution: 2048x2730 pixels (2K)
- Aspect Ratio: 3:4
- Format: Portrait photography
- Style: Professional corporate headshot
- Lighting: Studio setup with softbox and rim light"""

    return prompt

def get_prompt_summary():
    """返回Prompt使用说明"""
    return {
        "title": "Instructional Prompting最佳实践",
        "principles": [
            "使用祈使句（动词开头）",
            "清晰、简洁、具体",
            "按重要性排序",
            "避免模糊表述",
            "包含技术规格"
        ],
        "structure": {
            "1. TASK": "任务描述",
            "2. SUBJECT REQUIREMENTS": "主体要求",
            "3. CLOTHING INSTRUCTIONS": "服装指令",
            "4. BACKGROUND INSTRUCTIONS": "背景指令",
            "5. COMPOSITION AND STYLE": "构图与风格",
            "6. CRITICAL CONSTRAINTS": "关键约束",
            "7. QUALITY VERIFICATION": "质量验证",
            "8. TECHNICAL SPECIFICATIONS": "技术规格"
        },
        "examples": {
            "good": "DRESS subject in professional business suit",
            "bad": "Make them wear some nice clothes",
            "reason": "祈使句更明确，AI更容易理解"
        }
    }

if __name__ == "__main__":
    # 测试生成prompt
    print("=" * 70)
    print("英文Instructional Prompting示例：")
    print("=" * 70)

    prompt = generate_english_prompt(
        clothing='business_suit',
        angle='front',
        background='textured',
        bg_color='white',
        beautify='yes'
    )

    print(prompt)
    print("\n" + "=" * 70)
    print("Prompt长度:", len(prompt), "字符")
    print("=" * 70)
