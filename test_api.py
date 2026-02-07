"""
API 测试脚本 - 验证 12ai.org API 连接
"""

import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

# API 配置
API_KEY = os.getenv('NANOBANANA_API_KEY', '')
API_PROVIDER = os.getenv('API_PROVIDER', '12ai')
MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-3-pro-image-preview-2k')

# API 基础 URL
API_BASE_URLS = {
    'laozhang': 'https://api.laozhang.ai/v1',
    '12ai': 'https://ismaque.org/v1'
}

base_url = API_BASE_URLS.get(API_PROVIDER, API_BASE_URLS['12ai'])

# 判断模型类型
is_gemini = MODEL_NAME.startswith('gemini-')

if is_gemini and API_PROVIDER == '12ai':
    # Gemini 原生格式
    api_url = f"{base_url}/models/{MODEL_NAME}:generateContent"
    api_format = "gemini"
else:
    # OpenAI 兼容格式
    api_url = f"{base_url}/chat/completions"
    api_format = "openai"

print("=" * 70)
print("🧪 12ai.org API 测试")
print("=" * 70)
print(f"API 提供商: {API_PROVIDER}")
print(f"模型名称: {MODEL_NAME}")
print(f"API 格式: {api_format.upper()}")
print(f"API URL: {api_url}")
print(f"API Key: {'已配置 (' + str(len(API_KEY)) + ' 字符)' if API_KEY else '❌ 未配置'}")
print("=" * 70)

if not API_KEY:
    print("\n❌ 错误: NANOBANANA_API_KEY 未配置")
    print("\n请在 Railway 控制台添加环境变量:")
    print("  Settings → Variables → New Variable")
    print("  Name: NANOBANANA_API_KEY")
    print("  Value: 你的_12ai_API_Key")
    exit(1)

# 创建一个简单的测试图片 (1x1 像素的 PNG)
test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

# 构建 payload
if api_format == 'gemini':
    # Gemini 原生格式
    payload = {
        "contents": [{
            "parts": [
                {"text": "测试：生成一张 1x1 红色像素的图片"},
                {"inline_data": {"mime_type": "image/png", "data": test_image_base64}}
            ]
        }],
        "generationConfig": {
            "temperature": 0.9,
            "topP": 0.95,
            "responseModalities": ["IMAGE"],
            "imageFormat": "PNG"
        }
    }
else:
    # OpenAI 兼容格式
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "测试：生成一张 1x1 红色像素的图片"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{test_image_base64}"}}
                ]
            }
        ],
        "temperature": 0.9,
        "max_tokens": 1000
    }

print("\n📤 发送测试请求...")
print(f"请求 URL: {api_url}")
print(f"Payload 格式: {api_format}")

try:
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    response = requests.post(api_url, json=payload, headers=headers, timeout=30)

    print(f"\n📥 响应状态码: {response.status_code}")

    if response.status_code == 200:
        print("✅ API 连接成功！")

        result = response.json()
        print(f"响应键: {list(result.keys())}")

        # 检查响应格式
        if 'candidates' in result:
            print("✅ Gemini 格式响应")
        elif 'choices' in result:
            print("✅ OpenAI 格式响应")
        else:
            print("⚠️  未知响应格式")
            print(f"响应内容: {result}")
    else:
        print(f"❌ API 返回错误: {response.status_code}")
        print(f"错误内容: {response.text[:500]}")

        # 常见错误诊断
        error_text = response.text.lower()
        if '401' in str(response.status_code) or 'unauthorized' in error_text:
            print("\n🔍 诊断: API Key 无效或过期")
            print("   解决方案: 检查 NANOBANANA_API_KEY 是否正确")
        elif '404' in str(response.status_code) or 'not found' in error_text:
            print("\n🔍 诊断: API URL 不正确")
            print(f"   当前 URL: {api_url}")
            print("   解决方案: 检查 API_PROVIDER 和 MODEL_NAME 配置")
        elif '429' in str(response.status_code) or 'quota' in error_text:
            print("\n🔍 诊断: API 额度用完")
            print("   解决方案: 检查 12ai.org 账户余额")
        elif '500' in str(response.status_code):
            print("\n🔍 诊断: 服务器内部错误")
            print("   解决方案: 稍后重试或联系 12ai.org 支持")

except requests.exceptions.Timeout:
    print("❌ 请求超时（30秒）")
    print("   可能原因: 网络连接慢或服务器响应慢")
except requests.exceptions.ConnectionError as e:
    print(f"❌ 连接失败: {e}")
    print("   可能原因: 网络不可达或防火墙阻止")
except Exception as e:
    print(f"❌ 请求失败: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
