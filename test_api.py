"""
测试 NanoBanana API 调用
使用方法: python test_api.py --image /path/to/image.jpg --style haima
"""

import argparse
import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

NANOBANANA_API_URL = os.getenv('NANOBANANA_API_URL', 'https://api.nanobanana.com/v1/generate')
NANOBANANA_API_KEY = os.getenv('NANOBANANA_API_KEY', '')


def test_api_with_file(image_path, style):
    """使用文件上传方式测试 API"""

    print(f"🧪 测试 NanoBanana API 调用")
    print(f"📁 图片路径: {image_path}")
    print(f"🎨 风格: {style}")
    print(f"🔑 API URL: {NANOBANANA_API_URL}")
    print(f"🔑 API Key: {'已设置' if NANOBANANA_API_KEY else '未设置 - 使用 .env 配置'}")
    print()

    if not NANOBANANA_API_KEY or NANOBANANA_API_KEY == 'your-api-key-here':
        print("⚠️  警告: NANOBANANA_API_KEY 未设置")
        print("请在 .env 文件中配置有效的 API Key")
        return

    if not os.path.exists(image_path):
        print(f"❌ 错误: 文件不存在 - {image_path}")
        return

    try:
        # 方式1: Base64 编码
        print("📤 使用 Base64 编码方式发送请求...")

        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()

        payload = {
            'image': image_data,
            'style': style
        }

        headers = {
            'Authorization': f'Bearer {NANOBANANA_API_KEY}',
            'Content-Type': 'application/json'
        }

        response = requests.post(
            NANOBANANA_API_URL,
            json=payload,
            headers=headers,
            timeout=60
        )

        print(f"📊 状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ API 调用成功!")
            print(f"📦 响应数据: {result}")

            # 如果返回图片数据，保存
            if 'image' in result:
                output_path = image_path.replace('.', '_result.')
                with open(output_path, 'wb') as f:
                    f.write(base64.b64decode(result['image']))
                print(f"💾 结果已保存: {output_path}")

            # 如果返回 URL
            if 'image_url' in result or 'result_url' in result:
                url = result.get('image_url') or result.get('result_url')
                print(f"🔗 图片 URL: {url}")

        else:
            print(f"❌ API 调用失败")
            print(f"📦 响应内容: {response.text}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_api_with_multipart(image_path, style):
    """使用 multipart/form-data 方式测试 API"""

    print(f"🧪 测试 NanoBanana API 调用 (Multipart)")
    print(f"📁 图片路径: {image_path}")
    print(f"🎨 风格: {style}")
    print()

    if not NANOBANANA_API_KEY or NANOBANANA_API_KEY == 'your-api-key-here':
        print("⚠️  警告: NANOBANANA_API_KEY 未设置")
        print("请在 .env 文件中配置有效的 API Key")
        return

    if not os.path.exists(image_path):
        print(f"❌ 错误: 文件不存在 - {image_path}")
        return

    try:
        print("📤 使用 Multipart 方式发送请求...")

        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {
                'style': style
            }
            headers = {
                'Authorization': f'Bearer {NANOBANANA_API_KEY}'
            }

            response = requests.post(
                NANOBANANA_API_URL,
                files=files,
                data=data,
                headers=headers,
                timeout=60
            )

        print(f"📊 状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ API 调用成功!")
            print(f"📦 响应数据: {result}")
        else:
            print(f"❌ API 调用失败")
            print(f"📦 响应内容: {response.text}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def main():
    parser = argparse.ArgumentParser(description='测试 NanoBanana API')
    parser.add_argument('--image', type=str, help='图片路径')
    parser.add_argument('--style', type=str, default='haima',
                       choices=['haima', 'portrait'], help='生成风格')
    parser.add_argument('--method', type=str, default='base64',
                       choices=['base64', 'multipart'], help='请求方式')

    args = parser.parse_args()

    # 如果没有指定图片，使用测试图片
    if not args.image:
        print("📝 请提供测试图片路径")
        print("使用方法: python test_api.py --image /path/to/image.jpg --style haima")
        return

    if args.method == 'base64':
        test_api_with_file(args.image, args.style)
    else:
        test_api_with_multipart(args.image, args.style)


if __name__ == '__main__':
    main()
