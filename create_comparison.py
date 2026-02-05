"""
使用 NanoBanana API 生成展示对比图
左边：普通纯色证件照
右边：美式专业肖像生成效果
"""
import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('NANOBANANA_API_KEY', '')
API_MODEL = os.getenv('NANOBANANA_API_MODEL', 'gemini-3-pro-image-preview-2k')
API_URL = f"https://cdn.12ai.org/v1beta/models/{API_MODEL}:generateContent"

# 生成对比图的 prompt
prompt = """
Create a side-by-side comparison image (400x200 pixels) showing the SAME Asian person's transformation:

LEFT HALF (50%):
- A professional but plain ID photo style
- Person facing forward, neutral expression
- Solid light gray background (#e5e7eb)
- Wearing simple casual shirt
- Flat lighting, no special effects
- Chinese text at bottom: "原图"

RIGHT HALF (50%):
- Same person in American professional portrait style
- Confident expression, better posture
- Purple gradient studio background (#8b5cf6 to #7c3aed)
- Wearing business suit with visible collar
- Professional studio lighting with subtle rim light
- Skin looks smoother and more polished
- More vibrant and professional appearance
- Chinese text at bottom: "生成后"

MIDDLE: A subtle arrow (→) pointing from left to right

Style: Clean, modern, professional comparison showing clear improvement.
The person should be identical on both sides - same face, same features.
"""

def generate_comparison():
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "candidateCount": 1
        }
    }

    if not API_KEY:
        print("错误: NANOBANANA_API_KEY 未配置")
        print("请在 Railway 环境变量中设置 NANOBANANA_API_KEY")
        return None

    try:
        print("=" * 60)
        print("开始调用 NanoBanana API 生成展示对比图...")
        print(f"API Model: {API_MODEL}")
        print("=" * 60)

        request_url = f"{API_URL}?key={API_KEY}"
        headers = {'Content-Type': 'application/json'}

        response = requests.post(request_url, json=payload, headers=headers, timeout=180)

        print(f"\n响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"响应键: {list(result.keys())}")

            # 处理 Gemini API 响应
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    for part in candidate['content']['parts']:
                        inline_data = part.get('inlineData') or part.get('inline_data')
                        if inline_data and 'data' in inline_data:
                            image_data = base64.b64decode(inline_data['data'])

                            # 保存图片
                            output_path = 'static/images/showcase_comparison.png'
                            os.makedirs('static/images', exist_ok=True)
                            with open(output_path, 'wb') as f:
                                f.write(image_data)
                            print(f"\n✓ 对比图生成成功!")
                            print(f"  保存路径: {output_path}")
                            print(f"  文件大小: {len(image_data)} bytes")
                            return output_path

            # 检查其他格式
            if 'image' in result:
                image_data = base64.b64decode(result['image'])
                output_path = 'static/images/showcase_comparison.png'
                os.makedirs('static/images', exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                print(f"\n✓ 对比图生成成功!")
                print(f"  保存路径: {output_path}")
                return output_path

            print("\n⚠ 未知响应格式")
            print(f"响应内容: {str(result)[:500]}")
        else:
            print(f"\n✗ API 调用失败: {response.status_code}")
            print(f"错误内容: {response.text[:500]}")

    except Exception as e:
        print(f"\n✗ 生成失败: {e}")
        import traceback
        traceback.print_exc()

    return None

if __name__ == '__main__':
    generate_comparison()
