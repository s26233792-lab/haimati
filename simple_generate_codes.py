#!/usr/bin/env python3
"""
Simple verification code generator
Generates codes and displays them without requiring admin login
"""
import os
import sys
import random
import string
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database functions
import sqlite3

def get_db_path():
    """Get database path"""
    if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
        return os.path.join(os.getenv('RAILWAY_VOLUME_MOUNT_PATH', '/data'), 'codes.db')
    return os.getenv('DATABASE_PATH', 'codes.db')

def generate_codes(count=10, max_uses=3):
    """Generate verification codes"""
    db_path = get_db_path()

    # Check if database exists
    if not os.path.exists(db_path):
        print(f"⚠️  Database not found at: {db_path}")
        print("Please run the application first to initialize the database.")
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    codes = []
    for _ in range(count):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        try:
            cursor.execute('INSERT INTO verification_codes (code, max_uses) VALUES (?, ?)', (code, max_uses))
            codes.append(code)
        except sqlite3.IntegrityError:
            # Code already exists, skip
            continue

    conn.commit()
    conn.close()

    return codes

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate verification codes')
    parser.add_argument('--count', type=int, default=10, help='Number of codes to generate')
    parser.add_argument('--max-uses', type=int, default=3, help='Max uses per code')
    parser.add_argument('--format', choices=['list', 'csv'], default='list', help='Output format')

    args = parser.parse_args()

    codes = generate_codes(args.count, args.max_uses)

    if args.format == 'csv':
        print('code,max_uses')
        for code in codes:
            print(f'{code},{args.max_uses}')
    else:
        print(f'✅ Generated {len(codes)} verification codes:')
        print('-' * 50)
        for i, code in enumerate(codes, 1):
            print(f'{i}. {code}')

        if len(codes) > 0:
            print()
            print('📋 Quick copy (space-separated):')
            print(' '.join(codes))
