"""
配置检查脚本 - 检查当前环境和配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("Environment Configuration Check")
print("=" * 70)

# API 配置
api_key = os.getenv('NANOBANANA_API_KEY', '')
api_provider = os.getenv('API_PROVIDER', 'apicore')
model_name = os.getenv('MODEL_NAME', 'gemini-3-pro-image-preview')

print(f"\n[+] API Provider: {api_provider}")
print(f"[+] Model Name: {model_name}")
if api_key:
    print(f"[+] API Key: Configured ({len(api_key)} chars)")
else:
    print(f"[!] API Key: NOT configured")

# 计算 API URL
api_base_urls = {
    'apicore': 'https://api.apicore.ai/v1',
    'laozhang': 'https://api.laozhang.ai/v1',
    '12ai': 'https://ismaque.org/v1'
}

base_url = api_base_urls.get(api_provider, api_base_urls['apicore'])
is_gemini = model_name.startswith('gemini-')

if api_provider == '12ai' and is_gemini:
    api_url = f"{base_url}/models/{model_name}:generateContent"
    api_format = "Gemini 原生"
else:
    api_url = f"{base_url}/chat/completions"
    api_format = "OpenAI 兼容"

print(f"[+] API Format: {api_format}")
print(f"[+] API URL: {api_url}")

print("\n" + "=" * 70)
print("CORRECT CONFIGURATION SHOULD BE:")
print("=" * 70)
print("API_PROVIDER=apicore")
print("MODEL_NAME=gemini-3-pro-image-preview")
print("NANOBANANA_API_KEY=your_apicore_api_key")
print("\nAPI URL should be: https://api.apicore.ai/v1/chat/completions")
print("=" * 70)
