#!/usr/bin/env python3
"""
测试两个 API 的图像生成功能
对比 apicore.ai 和 ismaque.org 的效果
"""

import os
import sys
import base64
import json
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_status(message, status="info"):
    """打印带颜色的状态信息"""
    if status == "success":
        print(f"{Colors.GREEN}✓{Colors.END} {message}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠{Colors.END} {message}")
    elif status == "error":
        print(f"{Colors.RED}✗{Colors.END} {message}")
    elif status == "info":
        print(f"{Colors.BLUE}ℹ{Colors.END} {message}")
    else:
        print(f"{Colors.CYAN}●{Colors.END} {message}")

def create_test_image():
    """创建一个测试图片"""
    print("\n" + "="*70)
    print("🎨 创建测试图片")
    print("="*70)
    
    # 创建一个简单的人像照片模拟图
    img = Image.new('RGB', (512, 680), color='#FFE4C4')  # 肤色背景
    draw = ImageDraw.Draw(img)
    
    # 画一个简单的"人像"轮廓
    # 头
    draw.ellipse([156, 100, 356, 300], fill='#FDBCB4', outline='#E8A598', width=2)
    # 身体
    draw.rectangle([156, 300, 356, 600], fill='#6495ED', outline='#4169E1', width=2)
    
    # 添加文字说明
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((120, 620), "Test Portrait Photo", fill='#333333', font=font)
    
    test_path = "test_portrait.jpg"
    img.save(test_path, "JPEG", quality=95)
    
    print_status(f"测试图片已创建: {test_path} ({os.path.getsize(test_path)} bytes)", "success")
    return test_path

def test_apicore(image_path, api_key):
    """测试 apicore.ai API"""
    print("\n" + "="*70)
    print("🧪 测试 apicore.ai")
    print("="*70)
    
    if not api_key:
        print_status("未提供 apicore API Key，跳过测试", "warning")
        return None
    
    # 读取图片
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    url = "https://api.apicore.ai/v1/chat/completions"
    
    # OpenAI 格式的 prompt
    prompt = """Transform this portrait photo into a professional business portrait.

Requirements:
1. Change the blue shirt to a professional black business suit with white shirt
2. Replace the background with a clean professional gray studio background
3. Keep the person's face and hairstyle exactly as in the original
4. Add professional studio lighting
5. High quality, 3:4 aspect ratio

IMPORTANT: Generate a completely NEW image with the above changes. Do NOT return the original image."""
    
    payload = {
        "model": "gemini-3-pro-image-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]
            }
        ],
        "temperature": 0.9,
        "max_tokens": 4096
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print_status(f"发送请求到: {url}", "info")
    print_status(f"模型: gemini-3-pro-image-preview", "info")
    print_status(f"图片大小: {len(image_data)} bytes (base64)", "info")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        
        print_status(f"响应状态码: {response.status_code}", 
                    "success" if response.status_code == 200 else "error")
        
        if response.status_code != 200:
            print_status(f"错误: {response.text[:500]}", "error")
            return None
        
        result = response.json()
        
        # 检查响应格式
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            
            print_status(f"响应内容类型: {type(content)}", "info")
            print_status(f"响应内容长度: {len(content)}", "info")
            print_status(f"响应内容前100字符: {content[:100]}...", "info")
            
            # 检查是否是图片
            if isinstance(content, str) and content.startswith('data:image') and 'base64' in content:
                # 提取并保存图片
                base64_data = content.split('base64,')[-1]
                image_bytes = base64.b64decode(base64_data)
                
                output_path = "test_apicore_result.png"
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
                
                print_status(f"✅ 图片生成成功！", "success")
                print_status(f"输出文件: {output_path} ({len(image_bytes)} bytes)", "success")
                
                return {
                    'success': True,
                    'output': output_path,
                    'size': len(image_bytes),
                    'format': 'openai_base64'
                }
            else:
                print_status(f"⚠️ API 返回了文本而不是图片！", "warning")
                print_status(f"内容: {content[:300]}...", "warning")
                return {
                    'success': False,
                    'error': '返回文本而非图片',
                    'content_preview': content[:200]
                }
        else:
            print_status(f"未知响应格式: {list(result.keys())}", "error")
            return None
            
    except Exception as e:
        print_status(f"请求失败: {e}", "error")
        return None

def test_12ai(image_path, api_key):
    """测试 ismaque.org (12ai) API"""
    print("\n" + "="*70)
    print("🧪 测试 ismaque.org (12ai)")
    print("="*70)
    
    if not api_key:
        print_status("未提供 12ai API Key，跳过测试", "warning")
        return None
    
    # 读取图片
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    model = "gemini-3-pro-image-preview"
    url = f"https://ismaque.org/v1/models/{model}:generateContent"
    
    # Gemini 格式的 prompt
    prompt = """Transform this portrait photo into a professional business portrait.

Requirements:
1. Change the blue shirt to a professional black business suit with white shirt
2. Replace the background with a clean professional gray studio background
3. Keep the person's face and hairstyle exactly as in the original
4. Add professional studio lighting
5. High quality, 3:4 aspect ratio

IMPORTANT: Generate a completely NEW image with the above changes. Do NOT return the original image."""
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}
            ]
        }],
        "generationConfig": {
            "temperature": 0.9,
            "responseModalities": ["IMAGE"],
            "aspectRatio": "3:4"
        }
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print_status(f"发送请求到: {url}", "info")
    print_status(f"模型: {model}", "info")
    print_status(f"图片大小: {len(image_data)} bytes (base64)", "info")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        
        print_status(f"响应状态码: {response.status_code}", 
                    "success" if response.status_code == 200 else "error")
        
        if response.status_code != 200:
            print_status(f"错误: {response.text[:500]}", "error")
            return None
        
        result = response.json()
        
        # 检查响应格式
        if 'candidates' in result:
            for candidate in result['candidates']:
                if 'content' in candidate and 'parts' in candidate['content']:
                    for part in candidate['content']['parts']:
                        inline_data = part.get('inlineData') or part.get('inline_data')
                        if inline_data and 'data' in inline_data:
                            # 提取并保存图片
                            image_bytes = base64.b64decode(inline_data['data'])
                            
                            output_path = "test_12ai_result.png"
                            with open(output_path, 'wb') as f:
                                f.write(image_bytes)
                            
                            print_status(f"✅ 图片生成成功！", "success")
                            print_status(f"输出文件: {output_path} ({len(image_bytes)} bytes)", "success")
                            
                            return {
                                'success': True,
                                'output': output_path,
                                'size': len(image_bytes),
                                'format': 'gemini_inlineData'
                            }
            
            print_status(f"⚠️ 未找到图片数据", "warning")
            print_status(f"响应内容: {json.dumps(result, indent=2)[:500]}", "warning")
            return {
                'success': False,
                'error': '响应中未找到图片数据',
                'response_keys': list(result.keys())
            }
        else:
            print_status(f"未知响应格式: {list(result.keys())}", "error")
            return None
            
    except Exception as e:
        print_status(f"请求失败: {e}", "error")
        import traceback
        print(traceback.format_exc())
        return None

def compare_results(results):
    """对比两个 API 的结果"""
    print("\n" + "="*70)
    print("📊 测试结果对比")
    print("="*70)
    
    for api_name, result in results.items():
        if result is None:
            print(f"\n{api_name}:")
            print_status("未测试", "warning")
        elif result.get('success'):
            print(f"\n{Colors.GREEN}✓ {api_name}{Colors.END}:")
            print(f"  状态: ✅ 成功")
            print(f"  输出文件: {result['output']}")
            print(f"  文件大小: {result['size']} bytes")
            print(f"  响应格式: {result['format']}")
        else:
            print(f"\n{Colors.RED}✗ {api_name}{Colors.END}:")
            print(f"  状态: ❌ 失败")
            print(f"  错误: {result.get('error', '未知错误')}")
            if 'content_preview' in result:
                print(f"  响应预览: {result['content_preview'][:100]}...")

def recommend_config(results):
    """推荐配置"""
    print("\n" + "="*70)
    print("💡 配置建议")
    print("="*70)
    
    apicore_ok = results.get('apicore') and results['apicore'].get('success')
    ai12_ok = results.get('12ai') and results['12ai'].get('success')
    
    if apicore_ok and ai12_ok:
        print_status("两个 API 都工作正常！", "success")
        print("\n推荐使用 apicore（OpenAI 格式更通用）：")
        print("  API_PROVIDER=apicore")
        print("  MODEL_NAME=gemini-3-pro-image-preview")
    elif apicore_ok:
        print_status("apicore 工作正常，12ai 失败或跳过", "success")
        print("\n配置建议：")
        print("  API_PROVIDER=apicore")
        print("  MODEL_NAME=gemini-3-pro-image-preview")
    elif ai12_ok:
        print_status("12ai 工作正常，apicore 失败或跳过", "success")
        print("\n配置建议：")
        print("  API_PROVIDER=12ai")
        print("  MODEL_NAME=gemini-3-pro-image-preview")
    else:
        print_status("两个 API 都未能成功生成图片", "error")
        print("\n可能的原因：")
        print("  1. API Key 无效或过期")
        print("  2. 模型不支持图像生成")
        print("  3. 账户余额不足")
        print("  4. 网络连接问题")
        print("\n建议操作：")
        print("  - 检查 API Key 是否正确")
        print("  - 确认账户有足够余额")
        print("  - 联系 API 提供商确认模型支持")

def main():
    """主函数"""
    print("\n" + "🚀"*35)
    print("  API 图像生成测试工具")
    print("  对比 apicore.ai vs ismaque.org")
    print("🚀"*35)
    
    # 获取 API Keys
    print("\n请输入 API Keys（如果不想测试某个 API，直接回车跳过）：")
    
    apicore_key = input("apicore.ai API Key: ").strip()
    ai12_key = input("ismaque.org API Key: ").strip()
    
    # 创建测试图片
    test_image = create_test_image()
    
    # 测试两个 API
    results = {}
    
    results['apicore'] = test_apicore(test_image, apicore_key)
    results['12ai'] = test_12ai(test_image, ai12_key)
    
    # 对比结果
    compare_results(results)
    
    # 推荐配置
    recommend_config(results)
    
    # 清理
    print("\n" + "="*70)
    print("🧹 清理测试文件")
    print("="*70)
    
    for f in [test_image, "test_apicore_result.png", "test_12ai_result.png"]:
        if os.path.exists(f):
            # 保留生成的结果图片供用户查看
            if "result" in f:
                print_status(f"保留结果图片: {f}", "info")
            else:
                os.remove(f)
                print_status(f"删除: {f}", "info")
    
    print("\n" + "="*70)
    print("测试完成！")
    print("="*70)
    
    # 显示查看结果图片的命令
    if results.get('apicore') and results['apicore'].get('success'):
        print(f"\n查看 apicore 结果: open test_apicore_result.png")
    if results.get('12ai') and results['12ai'].get('success'):
        print(f"查看 12ai 结果: open test_12ai_result.png")

if __name__ == '__main__':
    main()
