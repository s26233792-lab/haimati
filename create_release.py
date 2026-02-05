#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

# 源目录和目标目录
source_dir = Path(r'C:\Users\Terrt\Desktop\新项目\portrait-app')
target_dir = Path(r'C:\Users\Terrt\Desktop\新项目\portrait-app-release')

# 需要排除的文件和目录
exclude = {
    '.git',
    'uploads',
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '*.db',
    '*.sqlite',
    '*.sqlite3',
    '.env',
    'test_api.py',
    'index.py',
    'vercel.json',
    'start.sh',
}

# 需要排除的文件扩展名
exclude_ext = {
    '.pyc',
    '.pyo',
    '.db',
    '.sqlite',
    '.sqlite3',
}

def should_exclude(name):
    """检查是否应该排除该文件/目录"""
    # 检查完整名称
    if name in exclude:
        return True
    # 检查扩展名
    if Path(name).suffix in exclude_ext:
        return True
    # 检查是否以点开头（隐藏文件）
    if name.startswith('.') and name not in {'.env.example', '.gitignore'}:
        return True
    return False

def copy_directory(src, dst):
    """递归复制目录"""
    os.makedirs(dst, exist_ok=True)

    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if should_exclude(item):
            print(f"跳过: {item}")
            continue

        if os.path.isdir(src_path):
            print(f"复制目录: {item}")
            copy_directory(src_path, dst_path)
        else:
            print(f"复制文件: {item}")
            shutil.copy2(src_path, dst_path)

# 清空并创建目标目录
if target_dir.exists():
    shutil.rmtree(target_dir)
target_dir.mkdir()

# 复制文件
print("开始复制文件...")
copy_directory(source_dir, target_dir)
print(f"\n完成! 文件已复制到: {target_dir}")
print(f"\n发布包内容:")
for root, dirs, files in os.walk(target_dir):
    level = root.replace(str(target_dir), '').count(os.sep)
    indent = ' ' * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 2 * (level + 1)
    for file in files[:5]:  # 只显示前5个文件
        print(f"{subindent}{file}")
    if len(files) > 5:
        print(f"{subindent}... 还有 {len(files) - 5} 个文件")
