#!/usr/bin/env python3
"""
快速检查 API 响应格式
用于确定哪个 API 能正常工作
"""

import os
import base64
import json
import requests
from PIL import Image

def quick_test():
    print("=" * 70)
    print("🔍 API 响应格式快速检查")
    print("=" * 70)
    
    # 创建一个简单的测试图
    print("\n创建测试图片...")
    img = Image.new('RGB', (400, 400), color='lightblue')
    img.save('quick_test.jpg')
    
    with open('quick_test.jpg', 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    print(f"测试图片大小: {len(image_data)} bytes (base64)\n")
    
    # 测试 apicore
    print("-" * 70)
    print("测试 1: apicore.ai (OpenAI 格式)")
    print("-" * 70)
    
    apicore_key = os.getenv('NANOBANANA_API_KEY', '')
    if not apicore_key:
        apicore_key = input("请输入 apicore.ai API Key (回车跳过): ").strip()
    
    if apicore_key:
        try:
            response = requests.post(
                "https://api.apicore.ai/v1/chat/completions",
                headers={'Authorization': f'Bearer {apicore_key}', 'Content-Type': 'application/json'},
                json={
                    "model": "gemini-3-pro-image-preview",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Convert this to a professional portrait with black suit and gray background"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                        ]
                    }],
                    "temperature": 0.9
                },
                timeout=60
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                print(f"响应类型: {type(content)}")
                print(f"响应长度: {len(content)}")
                print(f"前100字符: {content[:100]}...")
                
                if content.startswith('data:image') and 'base64' in content:
                    print("✅ apicore 返回了正确的图片格式！")
                    
                    # 保存图片
                    base64_data = content.split('base64,')[-1]
                    img_data = base64.b64decode(base64_data)
                    with open('apicore_result.png', 'wb') as f:
                        f.write(img_data)
                    print(f"✅ 图片已保存: apicore_result.png ({len(img_data)} bytes)")
                else:
                    print("⚠️ apicore 返回了文本而不是图片")
                    print(f"内容: {content[:200]}...")
            else:
                print(f"❌ 请求失败: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
    else:
        print("跳过 apicore 测试")
    
    # 测试 12ai
    print("\n" + "-" * 70)
    print("测试 2: ismaque.org (Gemini 格式)")
    print("-" * 70)
    
    ai12_key = os.getenv('12AI_API_KEY', '')
    if not ai12_key:
        ai12_key = input("请输入 ismaque.org API Key (回车跳过): ").strip()
    
    if ai12_key:
        try:
            response = requests.post(
                "https://ismaque.org/v1/models/gemini-3-pro-image-preview:generateContent",
                headers={'Authorization': f'Bearer {ai12_key}', 'Content-Type': 'application/json'},
                json={
                    "contents": [{
                        "parts": [
                            {"text": "Convert this to a professional portrait with black suit and gray background"},
                            {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}
                        ]
                    }],
                    "generationConfig": {
                        "temperature": 0.9,
                        "responseModalities": ["IMAGE"]
                    }
                },
                timeout=60
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result:
                    found_image = False
                    for candidate in result['candidates']:
                        if 'content' in candidate and 'parts' in candidate['content']:
                            for part in candidate['content']['parts']:
                                inline_data = part.get('inlineData') or part.get('inline_data')
                                if inline_data and 'data' in inline_data:
                                    found_image = True
                                    img_data = base64.b64decode(inline_data['data'])
                                    
                                    print("✅ 12ai 返回了正确的图片格式！")
                                    with open('12ai_result.png', 'wb') as f:
                                        f.write(img_data)
                                    print(f"✅ 图片已保存: 12ai_result.png ({len(img_data)} bytes)")
                    
                    if not found_image:
                        print("⚠️ 12ai 响应中没有找到图片数据")
                        print(f"响应: {json.dumps(result, indent=2)[:500]}")
                else:
                    print("⚠️ 12ai 返回了未知格式")
                    print(f"响应: {json.dumps(result, indent=2)[:500]}")
            else:
                print(f"❌ 请求失败: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
    else:
        print("跳过 12ai 测试")
    
    # 清理
    print("\n" + "=" * 70)
    print("清理测试文件...")
    if os.path.exists('quick_test.jpg'):
        os.remove('quick_test.jpg')
    
    print("\n结果查看:")
    if os.path.exists('apicore_result.png'):
        print("  apicore: open apicore_result.png")
    if os.path.exists('12ai_result.png'):
        print("  12ai: open 12ai_result.png")

if __name__ == '__main__':
    quick_test()
