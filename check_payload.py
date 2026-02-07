"""
检查API Payload结构诊断脚本
"""
import json

# 模拟当前的payload构建逻辑
API_FORMAT = 'openai'  # 假设使用OpenAI格式
MODEL_NAME = 'gemini-3-pro-image-preview'

# 当前代���中的payload
payload = {
    "model": MODEL_NAME,
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "这是测试prompt"},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
            ]
        }
    ],
    "temperature": 0.9,
    "top_p": 0.95,
    "seed": 12345,
    "max_tokens": 4096,
    # 问题可能在这里！
    "extra_body": {
        "strength": 0.75,
        "guidance_scale": 7.5,
        "image_guidance_scale": 1.5
    }
}

print("=" * 70)
print("当前Payload结构：")
print("=" * 70)
print(json.dumps(payload, indent=2, ensure_ascii=False))
print("\n" + "=" * 70)
print("问题分析：")
print("=" * 70)

print("\n❌ 问题1: extra_body字段")
print("   - OpenAI兼容格式通常不使用extra_body")
print("   - extra_body中的参数可能被API忽略")
print("   - 导致strength等参数不生效")

print("\n✅ 正确的格式应该是：")
correct_payload = {
    "model": MODEL_NAME,
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "这是测试prompt"},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
            ]
        }
    ],
    "temperature": 0.9,
    "top_p": 0.95,
    "seed": 12345,
    "max_tokens": 4096,
    # 参数应该直接放在根级别
    "strength": 0.75,
    "guidance_scale": 7.5,
}

print(json.dumps(correct_payload, indent=2, ensure_ascii=False))

print("\n" + "=" * 70)
print("可能的解决方案：")
print("=" * 70)
print("\n方案1: 移除extra_body，将参数提升到根级别")
print("方案2: 根据API文档使用正确的参数名")
print("方案3: 检查API是否支持图生图(img2img)功能")

print("\n" + "=" * 70)
print("推荐修复代码：")
print("=" * 70)
print("""
# 修改前（错误）:
payload = {
    "model": MODEL_NAME,
    "messages": [...],
    "temperature": 0.9,
    "extra_body": {
        "strength": 0.75,
        "guidance_scale": 7.5
    }
}

# 修改后（正确）:
payload = {
    "model": MODEL_NAME,
    "messages": [...],
    "temperature": 0.9,
    "strength": 0.75,  # 直接放在根级别
    "guidance_scale": 7.5,  # 直接放在根级别
}
""")
