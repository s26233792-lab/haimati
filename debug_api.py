#!/usr/bin/env python3
"""
API 调用诊断工具
用于排查图片生成问题
"""

import os
import sys
import base64
import json
import requests
from datetime import datetime

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_status(message, status="info"):
    """打印带颜色的状态信息"""
    if status == "success":
        print(f"{Colors.GREEN}✓{Colors.END} {message}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠{Colors.END} {message}")
    elif status == "error":
        print(f"{Colors.RED}✗{Colors.END} {message}")
    else:
        print(f"{Colors.BLUE}ℹ{Colors.END} {message}")

def check_api_config():
    """检查 API 配置"""
    print("\n" + "="*70)
    print("🔧 检查 API 配置")
    print("="*70)
    
    api_key = os.getenv('NANOBANANA_API_KEY', '')
    api_provider = os.getenv('API_PROVIDER', 'apicore')
    model_name = os.getenv('MODEL_NAME', 'gemini-3-pro-image-preview')
    
    if not api_key:
        print_status("NANOBANANA_API_KEY 未设置！", "error")
        return False
    
    print_status(f"API Key 已设置 (长度: {len(api_key)})", "success")
    print_status(f"API 提供商: {api_provider}", "info")
    print_status(f"模型: {model_name}", "info")
    
    # 检查 API 格式
    API_BASE_URLS = {
        'apicore': 'https://api.apicore.ai/v1',
        'laozhang': 'https://api.laozhang.ai/v1',
        '12ai': 'https://ismaque.org/v1'
    }
    
    base_url = API_BASE_URLS.get(api_provider, API_BASE_URLS['apicore'])
    is_gemini = model_name.startswith('gemini-')
    
    if api_provider == '12ai' and is_gemini:
        api_url = f"{base_url}/models/{model_name}:generateContent"
        api_format = 'gemini'
    else:
        api_url = f"{base_url}/chat/completions"
        api_format = 'openai'
    
    print_status(f"API URL: {api_url}", "info")
    print_status(f"API 格式: {api_format}", "info")
    
    return {
        'api_key': api_key,
        'api_url': api_url,
        'api_format': api_format,
        'model_name': model_name
    }

def test_api_connection(config):
    """测试 API 连接"""
    print("\n" + "="*70)
    print("🌐 测试 API 连接")
    print("="*70)
    
    try:
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        # 简单测试请求
        if config['api_format'] == 'openai':
            test_payload = {
                "model": config['model_name'],
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5
            }
        else:
            test_payload = {
                "contents": [{"parts": [{"text": "Hi"}]}]
            }
        
        print_status(f"发送测试请求到: {config['api_url']}", "info")
        response = requests.post(
            config['api_url'],
            headers=headers,
            json=test_payload,
            timeout=30
        )
        
        print_status(f"响应状态码: {response.status_code}", 
                    "success" if response.status_code == 200 else "error")
        
        if response.status_code != 200:
            print_status(f"错误响应: {response.text[:200]}", "error")
            return False
            
        return True
        
    except Exception as e:
        print_status(f"连接失败: {e}", "error")
        return False

def test_image_generation(config, test_image_path=None):
    """测试图片生成"""
    print("\n" + "="*70)
    print("🖼️ 测试图片生成")
    print("="*70)
    
    # 如果没有提供测试图片，创建一个简单的测试图
    if not test_image_path or not os.path.exists(test_image_path):
        try:
            from PIL import Image
            # 创建一个简单的测试图片
            test_image_path = "test_input.png"
            img = Image.new('RGB', (512, 512), color='red')
            img.save(test_image_path)
            print_status(f"创建测试图片: {test_image_path}", "info")
        except ImportError:
            print_status("PIL 未安装，跳过图片生成测试", "warning")
            return False
    
    # 读取并编码图片
    with open(test_image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    mime_type = "image/png" if test_image_path.endswith('.png') else "image/jpeg"
    
    print_status(f"测试图片: {test_image_path}", "info")
    print_status(f"图片大小: {len(image_data)} bytes (base64)", "info")
    
    # 构建 prompt
    prompt_text = """Transform this portrait photo into a professional business portrait.
    
Requirements:
- Change clothing to a professional business suit
- Replace background with a clean gray studio background
- Maintain the person's face exactly as in the original
- High quality, professional lighting
- 3:4 aspect ratio

IMPORTANT: Generate a completely new image, do not return the original."""
    
    # 构建 payload
    if config['api_format'] == 'gemini':
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt_text},
                    {"inline_data": {"mime_type": mime_type, "data": image_data}}
                ]
            }],
            "generationConfig": {
                "temperature": 0.9,
                "responseModalities": ["IMAGE"],
                "aspectRatio": "3:4"
            }
        }
    else:
        # OpenAI 格式 - 这里可能是问题所在！
        payload = {
            "model": config['model_name'],
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
            "max_tokens": 4096
            # 注意：移除了 strength 参数，因为 OpenAI 格式可能不支持
        }
    
    print_status(f"使用 {config['api_format'].upper()} 格式发送请求", "info")
    
    try:
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        print_status("发送图片生成请求...", "info")
        response = requests.post(
            config['api_url'],
            headers=headers,
            json=payload,
            timeout=120
        )
        
        print_status(f"响应状态码: {response.status_code}", 
                    "success" if response.status_code == 200 else "error")
        
        if response.status_code != 200:
            print_status(f"错误: {response.text[:500]}", "error")
            return False
        
        # 解析响应
        result = response.json()
        print_status(f"响应键: {list(result.keys())}", "info")
        
        # 检查是否是图片数据
        has_image = False
        image_source = None
        
        # 检查 OpenAI 格式
        if 'choices' in result and len(result['choices']) > 0:
            choice = result['choices'][0]
            if 'message' in choice:
                content = choice['message'].get('content', '')
                if isinstance(content, str):
                    print_status(f"Content 长度: {len(content)}", "info")
                    print_status(f"Content 前100字符: {content[:100]}", "info")
                    
                    if content.startswith('data:image') and 'base64' in content:
                        has_image = True
                        image_source = "OpenAI base64"
                        
                        # 保存图片
                        base64_data = content.split('base64,')[-1]
                        image_bytes = base64.b64decode(base64_data)
                        output_path = "test_output.png"
                        with open(output_path, 'wb') as f:
                            f.write(image_bytes)
                        print_status(f"✓ 图片已保存: {output_path} ({len(image_bytes)} bytes)", "success")
                    else:
                        print_status("响应不包含 base64 图片数据", "warning")
                        print_status(f"Content 类型: {content[:50]}...", "warning")
        
        # 检查 Gemini 格式
        elif 'candidates' in result:
            for candidate in result['candidates']:
                if 'content' in candidate and 'parts' in candidate['content']:
                    for part in candidate['content']['parts']:
                        inline_data = part.get('inlineData') or part.get('inline_data')
                        if inline_data and 'data' in inline_data:
                            has_image = True
                            image_source = "Gemini inlineData"
                            
                            image_bytes = base64.b64decode(inline_data['data'])
                            output_path = "test_output.png"
                            with open(output_path, 'wb') as f:
                                f.write(image_bytes)
                            print_status(f"✓ 图片已保存: {output_path} ({len(image_bytes)} bytes)", "success")
        
        if not has_image:
            print_status("未检测到图片数据！", "error")
            print_status(f"完整响应: {json.dumps(result, indent=2)[:1000]}", "warning")
            return False
        
        print_status(f"图片来源: {image_source}", "success")
        return True
        
    except Exception as e:
        print_status(f"测试失败: {e}", "error")
        import traceback
        print(traceback.format_exc())
        return False

def check_model_support(config):
    """检查模型是否支持图像生成"""
    print("\n" + "="*70)
    print("🔍 检查模型支持")
    print("="*70)
    
    model_name = config['model_name']
    
    # 已知的支持图像生成的模型
    supported_models = [
        'gemini-3-pro-image-preview',
        'gemini-3-pro-image-preview-2k',
        'gemini-2.0-flash-exp',
        'gpt-4o',
        'gpt-4o-mini'
    ]
    
    if model_name in supported_models:
        print_status(f"模型 {model_name} 已知支持图像生成", "success")
    else:
        print_status(f"模型 {model_name} 可能不支持图像生成", "warning")
        print_status("建议使用: gemini-3-pro-image-preview", "info")
    
    # 检查 API 提供商和模型的兼容性
    api_provider = os.getenv('API_PROVIDER', 'apicore')
    
    if api_provider == 'apicore' and model_name.startswith('gemini'):
        print_status("apicore + Gemini 模型组合应该支持图像生成", "success")
    elif api_provider == '12ai' and model_name.startswith('gemini'):
        print_status("12ai + Gemini 模型组合，使用原生 Gemini API", "success")
    else:
        print_status(f"{api_provider} + {model_name} 组合的兼容性未知", "warning")

def main():
    """主函数"""
    print("\n" + "🚀"*35)
    print("  API 调用诊断工具")
    print("🚀"*35)
    
    # 1. 检查配置
    config = check_api_config()
    if not config:
        print_status("配置检查失败，请检查环境变量", "error")
        sys.exit(1)
    
    # 2. 测试连接
    if not test_api_connection(config):
        print_status("API 连接测试失败", "error")
        # 继续执行其他测试
    
    # 3. 检查模型支持
    check_model_support(config)
    
    # 4. 测试图片生成
    print("\n是否测试图片生成? (y/n): ", end='')
    choice = input().strip().lower()
    if choice == 'y':
        test_image_generation(config)
    
    print("\n" + "="*70)
    print("诊断完成！")
    print("="*70)
    print("\n常见问题:")
    print("1. 如果 API 返回 200 但没有图片数据，可能是模型不支持图像生成")
    print("2. 如果返回原图，可能是 API 忽略了生成指令")
    print("3. 建议尝试更换模型或 API 提供商")

if __name__ == '__main__':
    main()
