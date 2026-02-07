"""
肖像照生成网站 - 后端主文件
功能：验证码验证、图片上传、API调用、使用次数管理
"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3
import os
import random
import string
import requests
from datetime import datetime, timedelta
import json
import sys
import time
import urllib.parse

# Windows 控制台编码修复
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# ==================== 数据库配置 ====================
# 支持 PostgreSQL (Railway 生产环境) 和 SQLite (本地开发)
DATABASE_URL = os.getenv('DATABASE_URL')

# Railway 环境检测 - 使用 PostgreSQL 或 SQLite
is_railway = os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_VOLUME_PATH')

# 持久化存储路径（Railway Volume 或本地）
persistent_path = os.getenv('RAILWAY_VOLUME_MOUNT_PATH', '/data')

if is_railway:
    # Railway 环境：优先使用 PostgreSQL，否则使用持久化 SQLite
    if DATABASE_URL:
        # Railway 会自动提供 DATABASE_URL 给 PostgreSQL
        db_type = 'postgresql'
        db_config = DATABASE_URL
    else:
        # 使用持久化存储的 SQLite（Railway Volume）
        db_type = 'sqlite'
        db_config = os.path.join(persistent_path, 'codes.db')
        os.makedirs(persistent_path, exist_ok=True)

    # 上传目录也使用持久化存储
    upload_folder = os.path.join(persistent_path, 'uploads')
else:
    # 本地开发环境：使用 SQLite
    db_type = 'sqlite'
    db_config = 'codes.db'
    upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')

os.makedirs(upload_folder, exist_ok=True)

# PostgreSQL 支持
POSTGRES_AVAILABLE = False
if db_type == 'postgresql':
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        POSTGRES_AVAILABLE = True
    except ImportError:
        print("警告: psycopg2 未安装，将回退到 SQLite")
        db_type = 'sqlite'
        # 使用持久化路径（Railway环境）或本地路径
        if is_railway:
            db_config = os.path.join(persistent_path, 'codes.db')
            os.makedirs(persistent_path, exist_ok=True)
        else:
            db_config = 'codes.db'

# SQL 占位符配置（兼容 PostgreSQL 和 SQLite）
# PostgreSQL 使用 %s，SQLite 使用 ?
PLACEHOLDER = '%s' if db_type == 'postgresql' else '?'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB max file size
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# NanoBanana API 配置
# 支持多个 API 提供商: laozhang.ai, 12ai.org
# 使用更可靠的端点配置
NANOBANANA_API_KEY = os.getenv('NANOBANANA_API_KEY', '')

# API 提供商选择
API_PROVIDER = os.getenv('API_PROVIDER', '12ai')  # 'laozhang' 或 '12ai'

# API 基础 URL 配置
# laozhang.ai 使用 OpenAI 兼容格式
API_BASE_URLS = {
    'laozhang': 'https://api.laozhang.ai/v1',
    '12ai': 'https://ismaque.org/v1'
}

# 支持多个模型选项 (12ai.org 支持的图像生成模型)
MODEL_CONFIGS = {
    'gemini-3-pro-image-preview-2k': {
        'name': 'Gemini 3 Pro Image Preview 2K (推荐)',
        'model_id': 'gemini-3-pro-image-preview-2k'
    },
    'gemini-2.0-flash-exp': {
        'name': 'Gemini 2.0 Flash Exp (图像生成)',
        'model_id': 'gemini-2.0-flash-exp'
    },
    'gemini-1.5-pro-latest': {
        'name': 'Gemini 1.5 Pro (旗舰)',
        'model_id': 'gemini-1.5-pro-latest'
    },
    'gpt-4o': {
        'name': 'GPT-4o (OpenAI)',
        'model_id': 'gpt-4o'
    }
}

# 从环境变量或默认值获取模型
# 默认使用 gemini-3-pro-image-preview-2k (图像生成模型)
MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-3-pro-image-preview-2k')
model_config = MODEL_CONFIGS.get(MODEL_NAME, MODEL_CONFIGS['gemini-3-pro-image-preview-2k'])

# 构建完整的 API URL
base_url = API_BASE_URLS.get(API_PROVIDER, API_BASE_URLS['12ai'])

# 检测是否是 Gemini 模型（用于图像生成）
is_gemini_model = MODEL_NAME.startswith('gemini-')

if is_gemini_model and API_PROVIDER == '12ai':
    # Gemini 模型使用原生格式: /v1beta/models/{model}:generateContent
    NANOBANANA_API_URL = f"{base_url}/models/{MODEL_NAME}:generateContent"
    API_FORMAT = 'gemini'
else:
    # 其他模型使用 OpenAI 兼容格式: /v1/chat/completions
    NANOBANANA_API_URL = f"{base_url}/chat/completions"
    API_FORMAT = 'openai'

# 管理后台认证配置
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# ==================== 启动时打印配置信息 ====================
print("=" * 70)
print("🚀 肖像照生成服务启动中...")
print("=" * 70)
print(f"📡 API 提供商: {API_PROVIDER}")
print(f"🤖 使用模型: {MODEL_NAME} ({model_config['name']})")
print(f"🔗 API URL: {NANOBANANA_API_URL}")
print(f"🔑 API Key: {'已配置 (' + str(len(NANOBANANA_API_KEY)) + ' 字符)' if NANOBANANA_API_KEY else '❌ 未配置'}")
print(f"💾 数据库类型: {'PostgreSQL' if POSTGRES_AVAILABLE else 'SQLite'}")
print(f"📁 上传目录: {upload_folder}")
print("=" * 70)

from functools import wraps


def admin_required(f):
    """管理后台身份验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查 session 中是否有登录标记
        if not session.get('admin_logged_in'):
            # 如果是 API 请求，返回 401
            if request.path.startswith('/admin/') and request.path != '/admin':
                return jsonify({'success': False, 'message': '请先登录'}), 401
            # 否则重定向到登录页
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated_function

# ==================== 数据库初始化 ====================

# ==================== 安全配��� ====================
# 请求频率限制配置
RATE_LIMIT_CONFIG = {
    'max_requests_per_minute': 10,  # 每分钟最多10次请求
    'max_verify_attempts_per_hour': 5,  # 每小时最多5次验证尝试
    'block_duration_minutes': 30  # 违规后封禁时长（分钟）
}

# 内存存储的请求记录（生产环境建议使用Redis）
request_tracker = {}  # {ip: {'count': int, 'reset_time': timestamp, 'blocked_until': timestamp}}
verify_attempts = {}  # {ip: {'count': int, 'reset_time': timestamp}}

# API 调用调试信息
last_api_call = {
    'called': False,
    'url': '',
    'status_code': None,
    'response_keys': [],
    'error': None,
    'timestamp': None
}


def get_client_ip():
    """获取客户端真实IP"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr


def check_rate_limit(ip, limit_type='general'):
    """检查请求频率限制"""
    now = time.time()

    # ��查是否被封禁
    if ip in request_tracker and request_tracker[ip].get('blocked_until', 0) > now:
        return False, f"请求过于频繁，请在 {int((request_tracker[ip]['blocked_until'] - now) / 60)} 分钟后重试"

    # 检查频率限制
    if limit_type == 'verify':
        # 验证码验证限制
        if ip not in verify_attempts:
            verify_attempts[ip] = {'count': 0, 'reset_time': now + 3600}

        if verify_attempts[ip]['reset_time'] < now:
            verify_attempts[ip] = {'count': 0, 'reset_time': now + 3600}

        if verify_attempts[ip]['count'] >= RATE_LIMIT_CONFIG['max_verify_attempts_per_hour']:
            return False, "验证尝试次数过多，请稍后再试"

        verify_attempts[ip]['count'] += 1
    else:
        # 通用请求限制
        if ip not in request_tracker:
            request_tracker[ip] = {'count': 0, 'reset_time': now + 60, 'blocked_until': 0}

        if request_tracker[ip]['reset_time'] < now:
            request_tracker[ip] = {'count': 0, 'reset_time': now + 60, 'blocked_until': 0}

        if request_tracker[ip]['count'] >= RATE_LIMIT_CONFIG['max_requests_per_minute']:
            # 封禁该IP
            request_tracker[ip]['blocked_until'] = now + (RATE_LIMIT_CONFIG['block_duration_minutes'] * 60)
            return False, f"请求过于频繁，已被临时限制访问 {RATE_LIMIT_CONFIG['block_duration_minutes']} 分钟"

        request_tracker[ip]['count'] += 1

    return True, None


# ==================== 数据库连接辅助函数 ====================

def get_db_connection():
    """获取数据库连接（支持 PostgreSQL 和 SQLite）"""
    if db_type == 'postgresql' and POSTGRES_AVAILABLE:
        conn = psycopg2.connect(db_config)
        conn.autocommit = False
        return conn
    else:
        conn = sqlite3.connect(db_config)
        conn.row_factory = sqlite3.Row
        return conn


def get_db_cursor(conn):
    """获取数据库游标（PostgreSQL 使用 RealDictCursor）"""
    if db_type == 'postgresql' and POSTGRES_AVAILABLE:
        return conn.cursor(cursor_factory=RealDictCursor)
    else:
        return conn.cursor()


def init_db():
    """初始化数据库（支持 PostgreSQL 和 SQLite）"""
    conn = get_db_connection()
    c = get_db_cursor(conn)

    try:
        # 验证码表
        if db_type == 'postgresql':
            # PostgreSQL 语法
            c.execute('''
                CREATE TABLE IF NOT EXISTS verification_codes (
                    code TEXT PRIMARY KEY,
                    max_uses INTEGER DEFAULT 3,
                    used_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            ''')
        else:
            # SQLite 语法
            c.execute('''
                CREATE TABLE IF NOT EXISTS verification_codes (
                    code TEXT PRIMARY KEY,
                    max_uses INTEGER DEFAULT 3,
                    used_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            ''')

        # 生成记录表
        if db_type == 'postgresql':
            c.execute('''
                CREATE TABLE IF NOT EXISTS generation_logs (
                    id SERIAL PRIMARY KEY,
                    code TEXT,
                    style TEXT,
                    original_image TEXT,
                    result_image TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            c.execute('''
                CREATE TABLE IF NOT EXISTS generation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT,
                    style TEXT,
                    original_image TEXT,
                    result_image TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        # 验证尝试日志表
        if db_type == 'postgresql':
            c.execute('''
                CREATE TABLE IF NOT EXISTS verification_attempts (
                    id SERIAL PRIMARY KEY,
                    code TEXT,
                    ip_address TEXT,
                    success BOOLEAN,
                    failure_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            c.execute('''
                CREATE TABLE IF NOT EXISTS verification_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT,
                    ip_address TEXT,
                    success BOOLEAN,
                    failure_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        conn.commit()
        print(f"[DB] 数据库初始化成功 (类型: {db_type})")
    except Exception as e:
        print(f"[DB] 数据库初始化失败: {e}")
        conn.rollback()
    finally:
        conn.close()


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def verify_code(code):
    """验证验证码并返回剩余次数"""
    conn = get_db_connection()
    c = get_db_cursor(conn)

    c.execute(f'SELECT max_uses, used_count, status FROM verification_codes WHERE code = {PLACEHOLDER}', (code,))
    result = c.fetchone()
    conn.close()

    if not result:
        return None, "验证码不存在"

    # 兼容多种数据库返回格式（元组、Row对象、字典）
    if isinstance(result, dict):
        max_uses = result['max_uses']
        used_count = result['used_count']
        status = result['status']
    else:
        # 元组或Row对象，按索引访问
        max_uses = result[0]
        used_count = result[1]
        status = result[2]

    if status != 'active':
        return None, "验证码已失效"

    remaining = max_uses - used_count
    if remaining <= 0:
        return None, "验证码使用次数已用完"

    return {'max_uses': max_uses, 'used_count': used_count, 'remaining': remaining}, None


def use_code(code):
    """使用验证码（扣减次数）"""
    conn = get_db_connection()
    c = get_db_cursor(conn)
    c.execute(f'UPDATE verification_codes SET used_count = used_count + 1 WHERE code = {PLACEHOLDER}', (code,))
    conn.commit()
    conn.close()


def log_generation(code, style, original_image, result_image, ip_address=None, user_agent=None):
    """记录生成历史（包含IP和用户代理）"""
    conn = get_db_connection()
    c = get_db_cursor(conn)
    c.execute(f'''
        INSERT INTO generation_logs (code, style, original_image, result_image, ip_address, user_agent)
        VALUES ({PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER})
    ''', (code, style, original_image, result_image, ip_address, user_agent))
    conn.commit()
    conn.close()


def log_verification_attempt(code, ip_address, success, failure_reason=None):
    """记录验证尝试（用于安全审计）"""
    conn = get_db_connection()
    c = get_db_cursor(conn)
    c.execute(f'''
        INSERT INTO verification_attempts (code, ip_address, success, failure_reason)
        VALUES ({PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER})
    ''', (code, ip_address, success, failure_reason))
    conn.commit()
    conn.close()


def call_nanobanana_api(image_path, style, clothing, angle, background, bg_color='white', beautify='no'):
    """
    调用图片生成 API (12ai.org NanoBanana Pro)

    参数:
        style: 风格 (portrait)
        clothing: 服装 (business_suit, formal_dress, casual_shirt, turtleneck, tshirt)
        angle: 拍摄角度 (front, slight_tilt)
        background: 背景 (textured, solid)
        bg_color: 背景色 (white, gray, blue, black, warm)
        beautify: 是否美颜 (yes, no)
    """
    import base64
    from PIL import Image, ImageFilter, ImageEnhance

    # ==================== 读取并编码图片 ====================
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()

    # ==================== 构建文本 prompt ====================
    # 服装处理
    clothing_map = {
        'business_suit': '商务西装',
        'formal_dress': '正装礼服',
        'casual_shirt': '休闲衬衫',
        'turtleneck': '高领毛衣',
        'tshirt': '简约T恤',
        'keep_original': '和原图保持一致'
    }

    # 背景处理
    background_map = {
        'textured': '质感影棚背景，柔和自然光，背景略微虚化，营造专业氛围',
        'solid': '纯净纯色背景，简洁干净，颜色均匀，无杂色'
    }

    # 背景色处理（质感影棚和纯色背景都支持）
    bg_color_map = {
        'white': '白色',
        'gray': '灰色',
        'blue': '蓝色',
        'black': '深灰色',
        'warm': '暖米色'
    }

    # 角度处理
    angle_map = {
        'front': '正面照，完全正对镜头',
        'slight_tilt': '微微倾斜角度，身体微侧，面部朝前'
    }

    # 构建文本 prompt
    angle_desc = angle_map.get(angle, '正面照，完全正对镜头')
    color_desc = bg_color_map.get(bg_color, '白色')

    # 美颜处理
    if beautify == 'yes':
        beauty_desc = "轻微美颜效果，自然提亮肤色，优化肤质，保持真实五官比例"
    else:
        beauty_desc = "保持真实面容，不添加美颜效果"

    # 根据背景类型选择描述
    if background == 'solid':
        bg_desc = f"纯净{color_desc}背景，颜色均匀，无杂色"
    else:  # textured
        bg_desc = f"质感影棚背景，{color_desc}色调，柔和自然光，背景略微虚化，营造专业氛围"

    prompt_text = f"""你是一个专业的AI换装助手。请执行以下操作：

【任务目标】根据参考图片，为人物更换服装和背景，生成一张���新的肖像照。

【人物要求】
- 保持人物的面部特征和发型完全一致
- 保持人物的性别和年龄特征
- 可以调整肤色光影，使整体更专业
- {beauty_desc}

【服装要求】
- {clothing_map.get(clothing, '商务西装')}
- 必须为人物穿上这套服装
- 服装要贴合身形，看起来真实自然

【背景要求】
- {bg_desc}
- 完全替换原背景
- 背景要专业、干净

【风格要求】
- 美式专业职场风格，{'微微倾斜角度拍摄' if angle == 'slight_tilt' else '正面角度拍摄'}
- 如军人般挺拔{'，身体微微侧转，面部正对镜头' if angle == 'slight_tilt' else '，完全正对镜头'}
- 超高清，2K分辨率，清晰对焦
- 3:4比例，确保输出分辨率为2048x2730像素
- 影棚级布光，构图优雅

【禁止事项】
- 禁止直接返回原图
- 禁止只做简单滤镜处理
- 必须重新生成图片

【验证标准】生成的图片必须与原图有明显差异：服装不同、背景不同、光影不同。"""

    # ==================== 打印调试信息 ====================
    print("=" * 70)
    print("📋 生成参数:")
    print(f"  服装: {clothing} -> {clothing_map.get(clothing, '商务西装')}")
    print(f"  角度: {angle} -> {angle_desc}")
    print(f"  背景: {background} + {bg_color}")
    print(f"  背景描述: {bg_desc}")
    print(f"  美颜: {beautify}")
    print("=" * 70)
    print("📝 完整 Prompt:")
    print(prompt_text)
    print("=" * 70)

    # ==================== 构建请求 payload ====================
    # 添加随机种子以确保每次生成不同的图片
    import time
    random_seed = int(time.time() * 1000) % 1000000
    print(f"[API] 使用随机种子: {random_seed}")

    # 根据模型类型选择不同的请求格式
    if API_FORMAT == 'gemini':
        # Gemini 原生格式 (用于 12ai Gemini 模型)
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt_text},
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}
                ]
            }],
            "generationConfig": {
                "temperature": 0.9,
                "topP": 0.95,
                "responseModalities": ["IMAGE"],
                "imageFormat": "PNG"
            }
        }
        api_format_name = "Gemini 原生格式"
        payload_type = "Gemini contents/parts 格式"
    else:
        # OpenAI 兼容格式
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }
            ],
            "temperature": 0.9,
            "top_p": 0.95,
            "seed": random_seed,
            "max_tokens": 4096
        }
        api_format_name = "OpenAI 兼容格式"
        payload_type = "OpenAI chat/completions 格式"

    # ==================== 打印发送给 API 的数据 ====================
    print("=" * 70)
    print(f"🚀 发送给 API 的数据 ({api_format_name}):")
    print(f"  URL: {NANOBANANA_API_URL}")
    print(f"  模型: {MODEL_NAME}")
    print(f"  Prompt 长度: {len(prompt_text)} 字符")
    print(f"  图片数据大小: {len(image_data)} 字符 (base64)")
    print(f"  Payload 结构: {payload_type}")
    print("-" * 70)
    print("📤 Prompt 内容 (发送给 API):")
    print(prompt_text)
    print("=" * 70)

    # ========== 真实 API 调用部分 ==========
    api_key = os.getenv('NANOBANANA_API_KEY', '')
    api_url = NANOBANANA_API_URL

    # 记录 API 调用开始
    last_api_call['called'] = True
    last_api_call['url'] = api_url
    last_api_call['timestamp'] = datetime.now().isoformat()

    # 检查 API Key 是否配置
    if api_key:
        print(f"[API] ==================== API 配置 ====================")
        print(f"[API] API 提供商: {API_PROVIDER}")
        print(f"[API] API 格式: {API_FORMAT.upper()}")
        print(f"[API] API Key 已配置 (长度: {len(api_key)} 字符)")
        print(f"[API] 模型: {MODEL_NAME}")
        print(f"[API] API URL: {api_url}")
        print(f"[API] ================================================")
        try:
            print(f"[API] 开始调用 API ({API_FORMAT.upper()} 格式)...")
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }

            # 使用 Session 来处理连接池和重试
            session = requests.Session()
            session.mount('https://', requests.adapters.HTTPAdapter(
                max_retries=3,
                pool_connections=1,
                pool_maxsize=1
            ))

            print(f"[API] 请求 URL: {api_url}")
            print(f"[API] 模型: {MODEL_NAME}")
            print(f"[API] 请求超时: 120秒")
            # 确认 payload 中的 prompt (OpenAI 格式)
            payload_content = payload.get('messages', [{}])[0].get('content', [])
            if isinstance(payload_content, list):
                for item in payload_content:
                    if item.get('type') == 'text':
                        prompt_text_check = item.get('text', '')
                        print(f"[API] ✅ Payload 中的 Prompt: {prompt_text_check[:50]}... (长度: {len(prompt_text_check)})")
                        break

            # 捕获所有可能的异常
            try:
                response = session.post(api_url, json=payload, headers=headers, timeout=120)
            except requests.exceptions.Timeout as e:
                print(f"[API] ❌ 请求超时: {e}")
                last_api_call['error'] = f'请求超时（120秒）'
                last_api_call['status_code'] = 408
                raise Exception(f"API 请求超时，请稍后重试")
            except requests.exceptions.ConnectionError as e:
                print(f"[API] ❌ 连接错误: {e}")
                last_api_call['error'] = f'连接失败: {str(e)}'
                last_api_call['status_code'] = 503
                raise Exception(f"无法连接到 API 服务器，请检查网络配置")
            except (SystemExit, KeyboardInterrupt) as e:
                print(f"[API] ❌ 进程退出: {e}")
                last_api_call['error'] = f'进程意外退出'
                last_api_call['status_code'] = 500
                raise Exception(f"API 调用被中断")
            except Exception as e:
                print(f"[API] ❌ 请求失败: {type(e).__name__}: {e}")
                last_api_call['error'] = f'{type(e).__name__}: {str(e)}'
                last_api_call['status_code'] = 500
                raise

            print(f"[API] 响应状态码: {response.status_code}")

            # 检查 HTTP 状态码
            if response.status_code != 200:
                error_text = response.text[:500]
                print(f"[API] HTTP 错误响应: {error_text}")
                last_api_call['error'] = f'HTTP {response.status_code}: {error_text}'
                raise Exception(f"API 返回错误 {response.status_code}: {error_text[:100]}")

            # 保存调试信息
            last_api_call['called'] = True
            last_api_call['url'] = api_url
            last_api_call['status_code'] = response.status_code
            last_api_call['timestamp'] = datetime.now().isoformat()

            if response.status_code == 200:
                result = response.json()
                print(f"[API] 响应键: {list(result.keys())}")
                print(f"[API] 响应内容预览: {json.dumps(result, ensure_ascii=False)[:400]}...")

                # 保存响应信息
                last_api_call['response_keys'] = list(result.keys())
                last_api_call['error'] = None

                # ========== 处理 OpenAI 兼容响应格式 ==========
                # OpenAI 格式: {"choices": [{"message": {"content": "..."}}]}
                if 'choices' in result and len(result['choices']) > 0:
                    choice = result['choices'][0]
                    print(f"[API] 检测到 OpenAI 格式响应")
                    print(f"[API] Choice 数据: {list(choice.keys())}")
                    if 'message' in choice:
                        message = choice['message']
                        print(f"[API] Message 数据存在: True")
                        if 'content' in message:
                            content = message['content']
                            print(f"[API] Content 类型: {type(content)}")

                            # 检查 content 是否包含图片数据
                            if isinstance(content, str):
                                print(f"[API] Content 长度: {len(content)}")
                                print(f"[API] Content 预览: {content[:200]}...")

                                # 检查是否是 base64 编码的图片 (data:image/...;base64,...)
                                if content.startswith('data:image') and 'base64' in content:
                                    import base64
                                    # 提取 base64 数据
                                    base64_data = content.split('base64,')[-1]
                                    image_data = base64.b64decode(base64_data)
                                    result_path = image_path.replace('.', '_result.')

                                    # 检查图片大小
                                    original_size = os.path.getsize(image_path)
                                    print(f"[API] 原图大小: {original_size} bytes")
                                    print(f"[API] 生成图片大小: {len(image_data)} bytes")

                                    # 检查是否和原图大小相同（可能返回了原图）
                                    if abs(len(image_data) - original_size) < 100:
                                        print(f"[API] ❌ 错误: 生成图片大小与原图几乎相同！")
                                        print(f"[API] ❌ API 返回了原图而不是生成的新图片")
                                        last_api_call['error'] = 'API返回了原图而非生成的图片'
                                        raise Exception("API返回了原图，图片生成失败。请尝试调整prompt或更换模型。")

                                    with open(result_path, 'wb') as f:
                                        f.write(image_data)

                                    saved_size = os.path.getsize(result_path)
                                    print(f"[API] 保存后大小: {saved_size} bytes")

                                    print(f"[API] ✓ OpenAI 图片生成成功: {result_path}")
                                    last_api_call['success'] = True
                                    last_api_call['format'] = 'openai_base64'
                                    return result_path

                # ========== 处理 Gemini API 响应格式 (向后兼容) ==========
                # Gemini 格式: {"candidates": [{"content": {"parts": [{"inlineData": {"data": "base64..."}}]}}]}
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    print(f"[API] Candidate 数据: {list(candidate.keys())}")
                    if 'content' in candidate:
                        print(f"[API] Content 数据存在: True")
                        if 'parts' in candidate['content']:
                            print(f"[API] Parts 数量: {len(candidate['content']['parts'])}")
                            for i, part in enumerate(candidate['content']['parts']):
                                print(f"[API] Part {i} keys: {list(part.keys())}")
                                # 检查 inlineData（驼峰命名）或 inline_data（下划线命名）
                                inline_data = part.get('inlineData') or part.get('inline_data')
                                if inline_data and 'data' in inline_data:
                                    import base64
                                    image_data = base64.b64decode(inline_data['data'])
                                    result_path = image_path.replace('.', '_result.')

                                    # 检查图片大小
                                    original_size = os.path.getsize(image_path)
                                    print(f"[API] 原图大小: {original_size} bytes")
                                    print(f"[API] 生成图片大小: {len(image_data)} bytes")

                                    # 检查是否和原图大小相同（可能返回了原图）
                                    if abs(len(image_data) - original_size) < 100:
                                        print(f"[API] ❌ 错误: 生成图片大小与原图几乎相同！")
                                        print(f"[API] ❌ API 返回了原图而不是生成的新图片")
                                        last_api_call['error'] = 'API返回了原图而非生成的图片'
                                        raise Exception("API返回了原图，图片生成失败。请尝试调整prompt或更换模型。")

                                    with open(result_path, 'wb') as f:
                                        f.write(image_data)

                                    # 验证保存后的文件大小
                                    saved_size = os.path.getsize(result_path)
                                    print(f"[API] 保存后大小: {saved_size} bytes")

                                    print(f"[API] ✓ Gemini 图片生成成功: {result_path}")
                                    last_api_call['success'] = True
                                    last_api_call['format'] = 'gemini'
                                    return result_path
                                else:
                                    print(f"[API] Part {i} 没有 inlineData")
                        else:
                            print(f"[API] Content 中没有 parts")
                    else:
                        print(f"[API] Candidate 中没有 content")

                # ========== 兼容其他格式 ==========
                # 格式1: {"image": "base64_string"}
                if 'image' in result:
                    import base64
                    image_data = base64.b64decode(result['image'])
                    result_path = image_path.replace('.', '_result.')
                    with open(result_path, 'wb') as f:
                        f.write(image_data)
                    print(f"[API] ✓ 图片生成成功 (base64格式): {result_path}")
                    last_api_call['success'] = True
                    last_api_call['format'] = 'base64'
                    return result_path

                # 格式2: {"url": "https://..."}
                elif 'url' in result:
                    img_response = requests.get(result['url'], timeout=30)
                    if img_response.status_code == 200:
                        result_path = image_path.replace('.', '_result.')
                        with open(result_path, 'wb') as f:
                            f.write(img_response.content)
                        print(f"[API] ✓ 图片下载成功 (URL格式): {result_path}")
                        last_api_call['success'] = True
                        last_api_call['format'] = 'url'
                        return result_path
                    else:
                        print(f"[API] 下载图片失败: {img_response.status_code}")
                        last_api_call['error'] = f'下载失败: {img_response.status_code}'

                print(f"[API] ⚠ 未知响应格式，使用模拟模式")
                print(f"[API] 完整响应: {json.dumps(result, ensure_ascii=False)[:800]}")
                last_api_call['error'] = '未知响应格式'
            else:
                print(f"[API] ✗ API 调用失败: {response.status_code}")
                print(f"[API] 错误内容: {response.text[:500]}")
                last_api_call['error'] = f'状态码: {response.status_code}, 内容: {response.text[:200]}'

        except Exception as e:
            print(f"[API] ✗ API 调用异常: {type(e).__name__}: {e}")
            import traceback
            print(f"[API] 异常堆栈: {traceback.format_exc()}")
            print(f"[API] 将使用模拟模式")
            last_api_call['error'] = f'{type(e).__name__}: {str(e)}'
    else:
        print(f"[API] ⚠ API Key 未配置，使用模拟模式")
        print(f"[API] 提示: 请在 Railway Variables 中设置 NANOBANANA_API_KEY")
        last_api_call['error'] = 'API Key 未配置'

    # ========== 模拟模式：对图片进行简单处理 ==========
    print(f"[模拟模式] 开始处理图片")
    print(f"[模拟模式] 原图: {image_path}")
    # 服装名称映射 (用于显示)
    clothing_names = {
        'business_suit': '商务西装',
        'formal_dress': '正装礼服',
        'casual_shirt': '休闲衬衫',
        'turtleneck': '高领毛衣',
        'tshirt': '简约T恤'
    }

    # 背景颜色映射 (用于模拟模式，质感影棚和纯色都支持)
    bg_color_map_sim = {
        'white': (255, 255, 255),
        'gray': (200, 200, 210),      # 质感影棚用稍浅的灰色
        'blue': (180, 200, 230),       # 柔和的蓝色
        'black': (70, 70, 80),         # 深灰色
        'warm': (245, 235, 210)        # 暖米色
    }

    # 纯色背景使用更鲜艳的颜色
    solid_bg_colors = {
        'white': (255, 255, 255),
        'gray': (233, 236, 239),
        'blue': (187, 222, 251),
        'black': (52, 58, 64),
        'warm': (255, 236, 179)
    }

    try:
        # 打开原始图片
        img = Image.open(image_path)
        img = img.convert('RGBA')

        # 根据背景类型选择颜色
        if background == 'solid':
            bg_color_rgb = solid_bg_colors.get(bg_color, (255, 255, 255))
        else:  # textured
            bg_color_rgb = bg_color_map_sim.get(bg_color, (200, 200, 210))

        # 创建带背景的新图片
        background_img = Image.new('RGBA', img.size, bg_color_rgb + (255,))
        background_img.paste(img, (0, 0), img)
        img = background_img.convert('RGB')

        # 美式肖像风格处理
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.85)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)
        img = img.filter(ImageFilter.SMOOTH)

        # 保存处理后的图片
        result_path = image_path.replace('.', '_result.')
        img.save(result_path, quality=95)

        print(f"[模拟模式] 图片已处理: {result_path}")
        bg_type_text = '质感影棚' if background == 'textured' else '纯色背景'
        bg_color_text = {'white': '白色', 'gray': '灰色', 'blue': '蓝色', 'black': '深灰', 'warm': '暖色'}.get(bg_color, '白色')
        beauty_text = '轻微美颜' if beautify == 'yes' else '无美颜'
        print(f"  风格: {style}, 服装: {clothing}, 背景: {bg_type_text}({bg_color_text}), 美颜: {beauty_text}")

        return result_path

    except Exception as e:
        print(f"图片处理失败: {e}")
        return image_path  # 失败时返回原图


# ==================== 路由 ====================

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/verify', methods=['POST'])
def verify():
    """验证验证码（带安全检查）"""
    # 获取客户端IP
    client_ip = get_client_ip()

    # 检查频率限制
    allowed, error_msg = check_rate_limit(client_ip, 'verify')
    if not allowed:
        log_verification_attempt('', client_ip, False, f'频率限制: {error_msg}')
        return jsonify({'success': False, 'message': error_msg}), 429

    data = request.json
    code = data.get('code', '').strip()

    if not code:
        log_verification_attempt('', client_ip, False, '请输入验证码')
        return jsonify({'success': False, 'message': '请输入验证码'}), 400

    result, error = verify_code(code)

    if error:
        log_verification_attempt(code, client_ip, False, error)
        return jsonify({'success': False, 'message': error}), 400

    # 记录成功的验证尝试
    log_verification_attempt(code, client_ip, True)

    return jsonify({
        'success': True,
        'remaining': result['remaining'],
        'max_uses': result['max_uses']
    })


@app.route('/api/upload', methods=['POST'])
def upload():
    """上传图片并生成（带安全检查）"""
    # 获取客户端信息
    client_ip = get_client_ip()
    user_agent = request.headers.get('User-Agent', '')

    # 检查频率限制
    allowed, error_msg = check_rate_limit(client_ip)
    if not allowed:
        return jsonify({'success': False, 'message': error_msg}), 429

    code = request.form.get('code', '').strip()
    style = request.form.get('style', 'portrait')
    clothing = request.form.get('clothing', 'business_suit')
    angle = request.form.get('angle', 'front')
    background = request.form.get('background', 'textured')
    bg_color = request.form.get('bgColor', 'white')  # 获取背景色，默认白色
    beautify = request.form.get('beautify', 'no')  # 获取美颜选项，默认不美颜

    # 验证验证码
    result, error = verify_code(code)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    # 检查文件
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': '请上传图片'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': '请选择图片'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': '只支持 PNG、JPG、JPEG、WEBP 格式'}), 400

    # 保存上传的文件
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # 调用 API 生成图片
    try:
        print(f"[Upload] 开始处理上传: {filename}")
        print(f"[Upload] 配置: style={style}, clothing={clothing}, angle={angle}, bg={background}, color={bg_color}, beautify={beautify}")

        result_path = call_nanobanana_api(filepath, style, clothing, angle, background, bg_color, beautify)

        print(f"[Upload] API 调用成功: {result_path}")

        # 扣减使用次数
        use_code(code)

        # 记录日志（包含IP和用户代理）
        log_generation(code, f"{style}_{clothing}_{background}", filename, result_path, client_ip, user_agent)

        return jsonify({
            'success': True,
            'result_url': f'/result/{result_path.split("/")[-1]}',
            'remaining': result['remaining'] - 1
        })

    except Exception as e:
        import traceback
        print(f"[Upload] 异常: {type(e).__name__}: {e}")
        print(f"[Upload] 堆栈: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'生成失败: {str(e)}'}), 500


@app.route('/result/<filename>')
def result(filename):
    """返回生成的图片"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath)
    return "图片不存在", 404


@app.route('/uploads/<filename>')
def uploads(filename):
    """返回上传的原始图片（用于示例展示）"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath)
    return "图片不存在", 404


@app.route('/debug/test')
def debug_test():
    """简单测试端点"""
    try:
        import os
        import sys

        result = {
            'status': 'ok',
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'env_vars': {
                'NANOBANANA_API_KEY': bool(os.getenv('NANOBANANA_API_KEY')),
                'SECRET_KEY': bool(os.getenv('SECRET_KEY')),
                'RAILWAY_ENVIRONMENT': os.getenv('RAILWAY_ENVIRONMENT'),
            }
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/debug/config')
def debug_config():
    """调试端点 - 检查配置"""
    api_key = os.getenv('NANOBANANA_API_KEY', '')
    return jsonify({
        'api_key_configured': bool(api_key),
        'api_key_length': len(api_key) if api_key else 0,
        'api_key_prefix': api_key[:10] + '...' if api_key else None,
        'api_url': NANOBANANA_API_URL,
        'db_type': db_type,
        'postgres_available': POSTGRES_AVAILABLE,
        'is_railway': is_railway,
        'upload_folder': upload_folder,
        'upload_folder_exists': os.path.exists(upload_folder)
    })


@app.route('/debug/api')
def debug_api():
    """调试端点 - 查看最后一次 API 调用信息"""
    return jsonify(last_api_call)


@app.route('/debug/health')
def debug_health():
    """健康检查端点 - 全面检查系统状态"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }

    # 1. 数据库连接检查
    try:
        conn = get_db_connection()
        c = get_db_cursor(conn)
        if db_type == 'postgresql':
            c.execute('SELECT version()')
            version = c.fetchone()[0]
            health_status['checks']['database'] = {
                'status': 'ok',
                'type': 'PostgreSQL',
                'version': version[:50]
            }
        else:
            c.execute('SELECT sqlite_version()')
            version = c.fetchone()[0]
            health_status['checks']['database'] = {
                'status': 'ok',
                'type': 'SQLite',
                'version': version
            }
        conn.close()
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'error',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'

    # 2. API Key 检查
    api_key = os.getenv('NANOBANANA_API_KEY', '')
    health_status['checks']['api_key'] = {
        'status': 'configured' if api_key else 'missing',
        'length': len(api_key) if api_key else 0
    }

    # 3. 上传目录检查
    upload_exists = os.path.exists(upload_folder)
    health_status['checks']['upload_folder'] = {
        'status': 'ok' if upload_exists else 'warning',
        'path': upload_folder,
        'exists': upload_exists
    }

    # 4. 数据库表检查
    try:
        conn = get_db_connection()
        c = get_db_cursor(conn)
        c.execute('SELECT name FROM sqlite_master WHERE type="table"') if db_type == 'sqlite' else \
                c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")

        tables = [row[0] for row in c.fetchall()]
        health_status['checks']['tables'] = {
            'status': 'ok',
            'count': len(tables),
            'tables': tables
        }
        conn.close()
    except Exception as e:
        health_status['checks']['tables'] = {
            'status': 'error',
            'error': str(e)
        }

    # 5. 最后一次 API 调用状态
    health_status['checks']['last_api_call'] = last_api_call

    # 确定整体状态
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code


@app.route('/api/status/<code>')
def status(code):
    """获取验证码状态"""
    result, error = verify_code(code)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    # 获取生成历史
    conn = get_db_connection()
    c = get_db_cursor(conn)
    c.execute(f'''
        SELECT style, created_at, result_image
        FROM generation_logs
        WHERE code = {PLACEHOLDER}
        ORDER BY created_at DESC
    ''', (code,))
    logs = c.fetchall()
    conn.close()

    return jsonify({
        'success': True,
        'remaining': result['remaining'],
        'max_uses': result['max_uses'],
        'history': [{'style': row[0], 'time': row[1], 'result': row[2]} for row in logs]
    })


@app.route('/api/showcase')
def showcase():
    """获取示例图片列表（用于首页展示）"""
    examples = [
        {
            'id': 1,
            'before': 'uploads/20260204_194214_IMG_6217.JPG',
            'after': 'uploads/20260204_194214_IMG_6217_result.JPG',
            'desc': '商务西装 + 质感影棚'
        },
        {
            'id': 2,
            'before': 'uploads/20260204_194227_HAAS4nYacAAp2Td.jpg',
            'after': 'uploads/20260204_194227_HAAS4nYacAAp2Td_result.jpg',
            'desc': '正装礼服 + 质感影棚'
        },
        {
            'id': 3,
            'before': 'uploads/20260204_201428_G_ktJfGaIAABVef.jpg',
            'after': 'uploads/20260204_201428_G_ktJfGaIAABVef_result.jpg',
            'desc': '休闲衬衫 + 纯色背景'
        }
    ]
    return jsonify({'success': True, 'examples': examples})


# ==================== 管理后台路由 ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """管理后台登录"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session.permanent = False  # 浏览器关闭后过期
            return redirect(url_for('admin'))
        else:
            return render_template('admin_login.html', error='用户名或密码错误')

    # 如果已登录，直接跳转到管理后台
    if session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    """管理后台登出"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/admin')
@admin_required
def admin():
    """管理后台"""
    conn = get_db_connection()
    c = get_db_cursor(conn)
    c.execute('SELECT * FROM verification_codes ORDER BY created_at DESC')
    codes = c.fetchall()
    conn.close()
    return render_template('admin.html', codes=codes)


@app.route('/admin/generate_codes', methods=['POST'])
@admin_required
def admin_generate_codes():
    """批量生成验证码"""
    data = request.json
    count = data.get('count', 10)
    max_uses = data.get('max_uses', 3)

    conn = get_db_connection()
    c = get_db_cursor(conn)

    codes = []
    for _ in range(count):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        try:
            c.execute(f'INSERT INTO verification_codes (code, max_uses) VALUES ({PLACEHOLDER}, {PLACEHOLDER})', (code, max_uses))
            codes.append(code)
        except Exception:
            continue

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'codes': codes, 'count': len(codes)})


@app.route('/admin/export_codes')
@admin_required
def export_codes():
    """导出所有活跃验证码"""
    conn = get_db_connection()
    c = get_db_cursor(conn)
    c.execute(f'SELECT code FROM verification_codes WHERE status = {PLACEHOLDER} ORDER BY code', ('active',))
    codes = [row[0] for row in c.fetchall()]
    conn.close()

    # 返回文本文件
    import io
    output = io.StringIO()
    for code in codes:
        output.write(f"{code}\n")

    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/plain',
        headers={'Content-Disposition': 'attachment; filename=verification_codes.txt'}
    )


@app.route('/admin/export_security_logs')
@admin_required
def export_security_logs():
    """导出安全审计日志"""
    conn = get_db_connection()
    c = get_db_cursor(conn)
    c.execute('''
        SELECT code, ip_address, success, failure_reason, created_at
        FROM verification_attempts
        ORDER BY created_at DESC
        LIMIT 1000
    ''')
    logs = c.fetchall()
    conn.close()

    # 返回CSV文件
    import io
    output = io.StringIO()
    output.write("验证码,IP地址,是否成功,失败原因,时间\n")
    for log in logs:
        output.write(f"{log[0] or ''},{log[1] or ''},{log[2]},{log[3] or ''},{log[4]}\n")

    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=security_logs.csv'}
    )


@app.route('/admin/batch_delete', methods=['POST'])
@admin_required
def batch_delete():
    """批量删除验证码"""
    data = request.json
    codes = data.get('codes', [])

    if not codes:
        return jsonify({'success': False, 'message': '未选择验证码'}), 400

    conn = get_db_connection()
    c = get_db_cursor(conn)

    # 使用占位符构建IN查询
    placeholders = ','.join([PLACEHOLDER for _ in codes])
    c.execute(f'DELETE FROM verification_codes WHERE code IN ({placeholders})', codes)

    deleted = c.rowcount
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'deleted': deleted})


@app.route('/admin/batch_update_status', methods=['POST'])
@admin_required
def batch_update_status():
    """批量更新验证码状态"""
    data = request.json
    codes = data.get('codes', [])
    status = data.get('status', 'active')

    if not codes:
        return jsonify({'success': False, 'message': '未选择验证码'}), 400

    if status not in ['active', 'inactive']:
        return jsonify({'success': False, 'message': '无效的状态'}), 400

    conn = get_db_connection()
    c = get_db_cursor(conn)

    placeholders = ','.join([PLACEHOLDER for _ in codes])
    c.execute(f'UPDATE verification_codes SET status = {PLACEHOLDER} WHERE code IN ({placeholders})', [status] + codes)

    updated = c.rowcount
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'updated': updated})


@app.route('/admin/reset_code', methods=['POST'])
@admin_required
def reset_code():
    """重置验证码使用次数"""
    data = request.json
    code = data.get('code')

    if not code:
        return jsonify({'success': False, 'message': '未指定验证码'}), 400

    conn = get_db_connection()
    c = get_db_cursor(conn)

    c.execute(f'UPDATE verification_codes SET used_count = 0, status = {PLACEHOLDER} WHERE code = {PLACEHOLDER}', ('active', code))

    if c.rowcount == 0:
        conn.close()
        return jsonify({'success': False, 'message': '验证码不存在'}), 404

    conn.commit()
    conn.close()

    return jsonify({'success': True})


# ==================== 启动 ====================

# 初始化数据库（在任何环境下都执行）
init_db()

if __name__ == '__main__':
    print("🚀 AI肖像馆 - 美式肖像生成器 启动成功!")
    print("📍 访问地址: http://localhost:5000")
    print("🔧 管理后台: http://localhost:5000/admin")
    print("💡 提示: 先运行 generate_codes.py 生成验证码")
    app.run(debug=True, host='0.0.0.0', port=5000)
