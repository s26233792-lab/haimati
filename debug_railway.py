"""
Railway 环境调试工具
用于诊断生产环境问题
"""

import os
import sys

print("=" * 70)
print("🔍 Railway 环境调试工具")
print("=" * 70)

# 1. 环境变量检查
print("\n1️⃣ 环境变量检查:")
print("-" * 70)

env_vars = {
    'NANOBANANA_API_KEY': 'API密钥',
    'SECRET_KEY': 'Flask密钥',
    'DATABASE_URL': '数据库连接',
    'RAILWAY_ENVIRONMENT': 'Railway环境',
    'RAILWAY_VOLUME_PATH': 'Railway卷路径',
    'RAILWAY_VOLUME_MOUNT_PATH': 'Railway挂载路径',
    'API_PROVIDER': 'API提供商',
    'MODEL_NAME': '模型名称',
    'ADMIN_USERNAME': '管理员用户名',
    'ADMIN_PASSWORD': '管理员密码',
}

for var_name, description in env_vars.items():
    value = os.getenv(var_name)
    if value:
        # 隐藏敏感信息
        if 'KEY' in var_name or 'PASSWORD' in var_name or 'SECRET' in var_name:
            display_value = f"✅ 已配置 (长度: {len(value)} 字符)"
        else:
            display_value = f"✅ {value}"
    else:
        display_value = "❌ 未配置"
    print(f"  {description} ({var_name}): {display_value}")

# 2. 数据库配置检查
print("\n2️⃣ 数据库配置:")
print("-" * 70)

DATABASE_URL = os.getenv('DATABASE_URL')
is_railway = os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_VOLUME_PATH')

if DATABASE_URL:
    print(f"  数据库类型: PostgreSQL")
    print(f"  连接字符串: {DATABASE_URL[:20]}... (已隐藏)")
else:
    print(f"  数据库类型: SQLite")
    print(f"  ⚠️  生产环境建议使用 PostgreSQL")

# 3. API 配置检查
print("\n3️⃣ API 配置:")
print("-" * 70)

API_PROVIDER = os.getenv('API_PROVIDER', '12ai')
MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-3-pro-image-preview-2k')

API_BASE_URLS = {
    'laozhang': 'https://api.laozhang.ai/v1',
    '12ai': 'https://ismaque.org/v1'
}

base_url = API_BASE_URLS.get(API_PROVIDER, API_BASE_URLS['12ai'])
is_gemini = MODEL_NAME.startswith('gemini-')

if is_gemini and API_PROVIDER == '12ai':
    api_url = f"{base_url}/models/{MODEL_NAME}:generateContent"
    api_format = "Gemini 原生格式"
else:
    api_url = f"{base_url}/chat/completions"
    api_format = "OpenAI 兼容格式"

print(f"  API 提供商: {API_PROVIDER}")
print(f"  API 基础 URL: {base_url}")
print(f"  模型名称: {MODEL_NAME}")
print(f"  API 完整 URL: {api_url}")
print(f"  请求格式: {api_format}")

# 4. 数据库占位符检查
print("\n4️⃣ 数据库占位符:")
print("-" * 70)

db_type = 'postgresql' if DATABASE_URL else 'sqlite'
PLACEHOLDER = '%s' if db_type == 'postgresql' else '?'

print(f"  数据库类型: {db_type}")
print(f"  占位符类型: {PLACEHOLDER}")
print(f"  ✅ 占位符配置正确")

# 5. 测试数据库连接
print("\n5️⃣ 测试数据库连接:")
print("-" * 70)

try:
    if db_type == 'postgresql':
        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = psycopg2.connect(DATABASE_URL)
        print(f"  ✅ PostgreSQL 连接成功")

        # 测试查询
        c = conn.cursor()
        c.execute("SELECT version()")
        version = c.fetchone()[0]
        print(f"  PostgreSQL 版本: {version[:50]}...")

        # 检查表是否存在
        c.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in c.fetchall()]
        print(f"  数据库表: {', '.join(tables)}")

        conn.close()

    else:
        import sqlite3
        conn = sqlite3.connect('codes.db')
        print(f"  ✅ SQLite 连接成功")

        # 检查表
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]
        print(f"  数据库表: {', '.join(tables)}")

        conn.close()

except Exception as e:
    print(f"  ❌ 数据库连接失败: {e}")

# 6. 检查上传目录
print("\n6️⃣ 文件系统检查:")
print("-" * 70)

persistent_path = os.getenv('RAILWAY_VOLUME_MOUNT_PATH', '/data')
upload_folder = os.path.join(persistent_path, 'uploads')

print(f"  持久化路径: {persistent_path}")
print(f"  上传目录: {upload_folder}")

if os.path.exists(persistent_path):
    print(f"  ✅ 持久化路径存在")
else:
    print(f"  ⚠️  持久化路径不存在（将在首次写入时创建）")

if os.path.exists(upload_folder):
    print(f"  ✅ 上传目录存在")
    # 统计文件数
    try:
        files = os.listdir(upload_folder)
        print(f"  上传文件数: {len(files)}")
    except Exception as e:
        print(f"  ⚠️  无法读取上传目录: {e}")
else:
    print(f"  ⚠️  上传目录不存在（将在首次上传时创建）")

# 7. 依赖检查
print("\n7️⃣ Python 依赖检查:")
print("-" * 70)

required_packages = {
    'flask': 'Flask',
    'requests': 'Requests',
    'PIL': 'Pillow',
    'psycopg2': 'psycopg2 (PostgreSQL)',
    'dotenv': 'python-dotenv'
}

for module_name, package_name in required_packages.items():
    try:
        __import__(module_name)
        print(f"  ✅ {package_name}")
    except ImportError:
        print(f"  ❌ {package_name} 未安装")

# 8. 常见问题诊断
print("\n8️⃣ 常见问题诊断:")
print("-" * 70)

api_key = os.getenv('NANOBANANA_API_KEY')
if not api_key:
    print("  ⚠️  NANOBANANA_API_KEY 未配置")
    print("     → 图片生成将使用模拟模式")
    print("     → 解决方案：在 Railway Variables 中添加 API Key")
else:
    print("  ✅ NANOBANANA_API_KEY 已配置")

if not DATABASE_URL and is_railway:
    print("  ⚠️  Railway 环境未使用 PostgreSQL")
    print("     → 建议：在 Railway 中添加 PostgreSQL 插件")
else:
    print("  ✅ 数据库配置正确")

# 9. 建议的调试步骤
print("\n9️⃣ 建议的调试步骤:")
print("-" * 70)
print("  1. 访问 /debug/config 端点查看完整配置")
print("  2. 访问 /debug/api 端点查看最后一次 API 调用")
print("  3. 检查 Railway 控制台的日志")
print("  4. 测试验证码验证功能")
print("  5. 测试图片上传功能")

print("\n" + "=" * 70)
print("✅ 调试检查完成")
print("=" * 70)
