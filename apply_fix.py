#!/usr/bin/env python3
"""
自动应用图生图修复补丁
运行此脚本将自动修复 app.py 中的图生图问题
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """备份文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ 已备份原文件到: {backup_path}")
    return backup_path

def apply_fix():
    """应用修复补丁"""
    app_py_path = "app.py"
    fixed_py_path = "app_fixed.py"

    # 检查文件是否存在
    if not os.path.exists(app_py_path):
        print(f"❌ 错误: 找不到 {app_py_path}")
        return False

    if not os.path.exists(fixed_py_path):
        print(f"❌ 错误: 找不到 {fixed_py_path}")
        print(f"   请确保 {fixed_py_path} 文件在当前目录")
        return False

    print("=" * 70)
    print("🔧 开始应用图生图修复补丁...")
    print("=" * 70)

    # 1. 备份原文件
    print("\n[步骤1] 备份原文件...")
    backup_path = backup_file(app_py_path)

    # 2. 读取修复版函数
    print("\n[步骤2] 读取修复版函数...")
    with open(fixed_py_path, 'r', encoding='utf-8') as f:
        fixed_content = f.read()

    # 3. 读取原文件
    print("\n[步骤3] 读取原文件...")
    with open(app_py_path, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # 4. 替换函数
    print("\n[步骤4] 替换 call_nanobanana_api 函数...")

    # 查找函数开始和结束位置
    import re

    # 匹配函数定义
    pattern = r'def call_nanobanana_api\([^)]+\):'
    match = re.search(pattern, original_content)

    if not match:
        print("❌ 错误: 在原文件中找不到 call_nanobanana_api 函数")
        return False

    func_start = match.start()

    # 查找函数结束（下一个def或文件末尾）
    next_def = re.search(r'\ndef [a-z_]', original_content[func_start + 100:])

    if next_def:
        func_end = func_start + 100 + next_def.start()
    else:
        func_end = len(original_content)

    print(f"   找到函数位置: {func_start} - {func_end}")

    # 从修复文件中提取函数
    fixed_match = re.search(r'def call_nanobanana_api_fixed.*', fixed_content, re.DOTALL)

    if not fixed_match:
        print("❌ 错误: 在修复文件中找不到 call_nanobanana_api_fixed 函数")
        return False

    fixed_function = fixed_match.group(0)

    # 替换函数名
    fixed_function = fixed_function.replace('call_nanobanana_api_fixed', 'call_nanobanana_api')

    # 构建新内容
    new_content = original_content[:func_start] + fixed_function + "\n\n" + original_content[func_end:]

    # 5. 写入修复后的文件
    print("\n[步骤5] 写入修复后的文件...")
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ 已成功应用修复补丁到 {app_py_path}")

    # 6. 验证修复
    print("\n[步骤6] 验证修复...")
    with open(app_py_path, 'r', encoding='utf-8') as f:
        verify_content = f.read()

    # 检查是否包含关键修复
    checks = {
        "strength参数": '"strength": 0.75' in verify_content,
        "guidance_scale参数": '"guidance_scale": 7.5' in verify_content,
        "增强的prompt": '图生图重绘任务' in verify_content,
        "MIME类型检测": 'mime_type' in verify_content,
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
        print("\n🎉 修复完成！现在你可以：")
        print("   1. 运行 'python app.py' 启动服务")
        print("   2. 测试图片生成功能")
        print("   3. 如果还有问题，查看日志调试")
        print("\n📝 备份文件位置:", backup_path)
        print("\n💡 如果需要恢复原版本:")
        print(f"   cp {backup_path} {app_py_path}")
        print("=" * 70)
        return True
    else:
        print("\n⚠️ 部分修复检查未通过，请手动检查")
        return False

if __name__ == "__main__":
    os.chdir("C:\\Users\\Terrt\\Downloads\\剧情\\haimati")
    success = apply_fix()

    if not success:
        print("\n❌ 修复失败，请手动应用修复")
        print("   参考 IMAGE_TO_IMAGE_FIX_REPORT.md 中的手动修复步骤")
