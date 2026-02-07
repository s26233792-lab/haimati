"""
修复验证码扣减逻辑
只有当API真正成功生成图片时，才扣减验证码次数
"""

import re

def fix_api_function():
    """修复call_nanobanana_api函数，返回成功标志"""
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 修改函数签名，添加返回值说明
    old_docstring = '''    """
    调用图片生成 API (12ai.org NanoBanana Pro)

    参数:
        style: 风格 (portrait)
        clothing: 服装 (business_suit, formal_dress, casual_shirt, turtleneck, tshirt)
        angle: 拍摄角度 (front, slight_tilt)
        background: 背景 (textured, solid)
        bg_color: 背景色 (white, gray, blue, black, warm)
        beautify: 是否美颜 (yes, no)
    """'''

    new_docstring = '''    """
    调用图片生成 API (12ai.org NanoBanana Pro)

    参数:
        style: 风格 (portrait)
        clothing: 服装 (business_suit, formal_dress, casual_shirt, turtleneck, tshirt)
        angle: 拍摄角度 (front, slight_tilt)
        background: 背景 (textured, solid)
        bg_color: 背景色 (white, gray, blue, black, warm)
        beautify: 是否美颜 (yes, no)

    返回:
        tuple: (result_path, api_success)
            - result_path: 生成图片的路径
            - api_success: bool, True表示API成功生成，False表示使用了模拟模式
    """'''

    content = content.replace(old_docstring, new_docstring)

    # 2. 在API成功的return语句后添加 (result_path, True)
    # OpenAI格式成功
    content = re.sub(
        r'(return result_path\s*)# (OpenAI 图片生成成功)',
        r'return result_path, True  # \2',
        content
    )

    # Gemini格式成功
    content = re.sub(
        r'(return result_path\s*)# (Gemini 图片生成成功)',
        r'return result_path, True  # \2',
        content
    )

    # base64格式成功
    content = re.sub(
        r'(return result_path\s*)# (图片生成成功 \(base64格式\))',
        r'return result_path, True  # \2',
        content
    )

    # URL格式成功
    content = re.sub(
        r'(return result_path\s*)# (图片下载成功 \(URL格式\))',
        r'return result_path, True  # \2',
        content
    )

    # 3. 在模拟模式return语句后添加 (result_path, False)
    content = re.sub(
        r'return result_path\s*# 失败时返回原图',
        r'return result_path, False  # 模拟模式或失败',
        content
    )

    # 模拟模式成功
    content = re.sub(
        r'(return result_path\s*)\n\s+print\(f"\[模拟模式\]',
        r'return result_path, False\n\n    print(f"[模拟模式]',
        content
    )

    return content

def fix_upload_function():
    """修复upload函数，只有API成功时才扣减次数"""
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到API调用的部分
    old_api_call = '''        result_path = call_nanobanana_api(filepath, style, clothing, angle, background, bg_color, beautify)

        print(f"[Upload] API 调用成功: {result_path}")

        # 扣减使用次数
        use_code(code)

        # 记录日志（包含IP和用户代理）
        log_generation(code, f"{style}_{clothing}_{background}", filename, result_path, client_ip, user_agent)

        return jsonify({
            'success': True,
            'result_url': f'/result/{result_path.split("/")[-1]}',
            'remaining': result['remaining'] - 1
        })'''

    new_api_call = '''        result_path, api_success = call_nanobanana_api(filepath, style, clothing, angle, background, bg_color, beautify)

        print(f"[Upload] API 调用完成: {result_path}")
        print(f"[Upload] API成功标志: {api_success}")

        # 只有API真正成功生成时才扣减使用次数
        if api_success:
            print(f"[Upload] API成功生成，扣减验证码次数")
            use_code(code)
            remaining_count = result['remaining'] - 1
        else:
            print(f"[Upload] API失败或使用模拟模式，不扣减验证码次数")
            remaining_count = result['remaining']

        # 记录日志（包含IP和用户代理）
        log_generation(code, f"{style}_{clothing}_{background}", filename, result_path, client_ip, user_agent)

        return jsonify({
            'success': True,
            'result_url': f'/result/{result_path.split("/")[-1]}',
            'remaining': remaining_count
        })'''

    content = content.replace(old_api_call, new_api_call)

    return content

def apply_fix():
    """应用所有修复"""
    # Windows控制台编码修复
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 70)
    print("开始修复验证码扣减逻辑...")
    print("=" * 70)

    # 备份
    import shutil
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"app.py.backup_counting_{timestamp}"
    shutil.copy2('app.py', backup_path)
    print(f"\n✅ 已备份到: {backup_path}")

    # 修复API函数
    print("\n[步骤1] 修复 call_nanobanana_api 函数...")
    content = fix_api_function()
    print("   ✅ 添加返回值元组 (result_path, api_success)")

    # 修复upload函数
    print("\n[步骤2] 修复 upload 函数...")
    content = fix_upload_function()
    print("   ✅ 添加成功标志检查")

    # 保存修复后的文件
    print("\n[步骤3] 保存修复后的文件...")
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("   ✅ 已保存到 app.py")

    # 验证修复
    print("\n[步骤4] 验证修复...")
    with open('app.py', 'r', encoding='utf-8') as f:
        verify_content = f.read()

    checks = {
        "API函数返回元组": 'return result_path, True' in verify_content,
        "upload函数解包元组": 'result_path, api_success = call_nanobanana_api' in verify_content,
        "条件扣减次数": 'if api_success:' in verify_content,
        "保留原次数": 'remaining_count = result[\'remaining\']' in verify_content,
    }

    all_passed = True
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
        if not result:
            all_passed = False

    if all_passed:
        print("\n" + "=" * 70)
        print("✅ 所有修复检查通过！")
        print("=" * 70)
        print("\n🎉 修复完成！现在的逻辑：")
        print("   ✅ API成功生成 → 扣减次数")
        print("   ✅ API失败/模拟模式 → 不扣减次数")
        print("\n📝 备份文件:", backup_path)
        print("=" * 70)
        return True
    else:
        print("\n⚠️ 部分修复检查未通过")
        return False

if __name__ == "__main__":
    import os
    os.chdir(r"C:\Users\Terrt\Downloads\剧情\haimati")
    apply_fix()
