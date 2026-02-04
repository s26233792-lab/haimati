"""
验证码批量生成工具
使用方法: python generate_codes.py --count 100 --output codes.txt
"""

import argparse
import sqlite3
import random
import string
import sys

# Windows 控制台编码修复
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def generate_code(length=8):
    """生成随机验证码"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_codes(count=100, max_uses=3):
    """批量生成验证码并保存到数据库"""
    conn = sqlite3.connect('codes.db')
    c = conn.cursor()

    # 创建表（如果不存在）
    c.execute('''
        CREATE TABLE IF NOT EXISTS verification_codes (
            code TEXT PRIMARY KEY,
            max_uses INTEGER DEFAULT 3,
            used_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')

    codes = []
    for _ in range(count):
        code = generate_code()
        c.execute('''
            INSERT INTO verification_codes (code, max_uses)
            VALUES (?, ?)
        ''', (code, max_uses))
        codes.append(code)

    conn.commit()
    conn.close()

    return codes


def export_to_file(codes, filename='codes.txt'):
    """导出验证码到文件"""
    with open(filename, 'w') as f:
        for code in codes:
            f.write(code + '\n')
    print(f"✅ 已导出 {len(codes)} 个验证码到 {filename}")


def main():
    parser = argparse.ArgumentParser(description='生成验证码')
    parser.add_argument('--count', type=int, default=100, help='生成数量')
    parser.add_argument('--output', type=str, default='codes.txt', help='输出文件')
    parser.add_argument('--uses', type=int, default=3, help='每个验证码最大使用次数')

    args = parser.parse_args()

    print(f"🔄 正在生成 {args.count} 个验证码...")
    codes = generate_codes(args.count, args.uses)
    export_to_file(codes, args.output)

    print("\n📋 前10个验证码预览:")
    for code in codes[:10]:
        print(f"   {code}")

    if len(codes) > 10:
        print(f"   ... 还有 {len(codes) - 10} 个")


if __name__ == '__main__':
    main()
