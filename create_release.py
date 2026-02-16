#!/usr/bin/env python3
"""
创建发布包工具
使用方法:
  python create_release.py                    # 使用默认路径
  python create_release.py --source . --target ./release
  环境变量: SOURCE_DIR, TARGET_DIR
"""
import os
import shutil
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='创建项目发布包')
    parser.add_argument('--source', type=str, help='源目录路径')
    parser.add_argument('--target', type=str, help='目标目录路径')

    args = parser.parse_args()

    # 从命令行参数、环境变量或默认值获取路径
    source_dir = Path(args.source or os.getenv('SOURCE_DIR', '.'))
    target_dir = Path(args.target or os.getenv('TARGET_DIR', './release'))

    print(f"源目录: {source_dir.resolve()}")
    print(f"目标目录: {target_dir.resolve()}")

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

    # 检查源目录是否存在
    if not source_dir.exists():
        print(f"错误: 源目录不存在: {source_dir}")
        return 1

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

    return 0

if __name__ == '__main__':
    exit(main())
