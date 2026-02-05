"""
生成展示对比图 - 使用NanoBanana API
"""
import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('NANOBANANA_API_KEY', '')
API_MODEL = os.getenv('NANOBANANA_API_MODEL', 'gemini-3-pro-image-preview-2k')
API_URL = f"https://cdn.12ai.org/v1beta/models/{API_MODEL}:generateContent"

# 生成对比图的prompt
prompt = """
Create a comparison image showing the same person's portrait transformation.

Left side (50% of image): Original casual photo
- A person's face in casual lighting
- Gray/dull background
- Flat, unprofessional look
- Text label at bottom: "原图"

Right side (50% of image): Professional portrait
- Same person's face
- Professional studio lighting
- Purple gradient background
- Wearing a business suit
- Enhanced, polished look
- Text label at bottom: "生成后"

Middle: An arrow pointing from left to right

Style: Clean, modern comparison image, 400x200 pixels ratio.
"""

def generate_comparison_image():
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 32,
            "topP": 0.95,
            "candidateCount": 1
        }
    }

    if not API_KEY:
        print("错误: NANOBANANA_API_KEY 未配置")
        return None

    try:
        print("正在调用 NanoBanana API 生成对比图...")
        request_url = f"{API_URL}?key={API_KEY}"
        headers = {'Content-Type': 'application/json'}

        response = requests.post(request_url, json=payload, headers=headers, timeout=120)

        print(f"响应状态码: {response.status_code}")

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
                            output_path = 'uploads/showcase_comparison.png'
                            os.makedirs('uploads', exist_ok=True)
                            with open(output_path, 'wb') as f:
                                f.write(image_data)
                            print(f"✓ 对比图生成成功: {output_path}")
                            return output_path

            # 检查其他格式
            if 'image' in result:
                image_data = base64.b64decode(result['image'])
                output_path = 'uploads/showcase_comparison.png'
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                print(f"✓ 对比图生成成功: {output_path}")
                return output_path

            print("⚠ 未知响应格式")
        else:
            print(f"✗ API 调用失败: {response.status_code}")
            print(f"错误内容: {response.text[:500]}")

    except Exception as e:
        print(f"✗ 生成失败: {e}")

    return None

if __name__ == '__main__':
    generate_comparison_image()
