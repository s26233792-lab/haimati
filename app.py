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
if is_railway:
    # Railway 环境：优先使用 PostgreSQL，否则使用持久化 SQLite
    if DATABASE_URL:
        # Railway 会自动提供 DATABASE_URL 给 PostgreSQL
        db_type = 'postgresql'
        db_config = DATABASE_URL
    else:
        # 没有配置 PostgreSQL，使用本地 SQLite（数据会丢失，不推荐）
        db_type = 'sqlite'
        db_config = '/tmp/portrait_app/codes.db'
        os.makedirs('/tmp/portrait_app', exist_ok=True)
else:
    # 本地开发环境：使用 SQLite
    db_type = 'sqlite'
    db_config = 'codes.db'

# 上传目录配置
if is_railway:
    # Railway 环境：使用临时目录（图片在重启后会丢失）
    upload_folder = '/tmp/portrait_app/uploads'
else:
    upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
os.makedirs(upload_folder, exist_ok=True)

# PostgreSQL 支持
if db_type == 'postgresql':
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        POSTGRES_AVAILABLE = True
    except ImportError:
        print("警告: psycopg2 未安装，将回退到 SQLite")
        db_type = 'sqlite'
        db_config = 'codes.db'
        POSTGRES_AVAILABLE = False
else:
    POSTGRES_AVAILABLE = False

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB max file size
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# NanoBanana API 配置
NANOBANANA_API_URL = os.getenv('NANOBANANA_API_URL', 'https://cdn.12ai.org/v1/images/edits')
NANOBANANA_API_KEY = os.getenv('NANOBANANA_API_KEY', '')

# 管理后台认证配置
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

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

    c.execute('SELECT max_uses, used_count, status FROM verification_codes WHERE code = ?', (code,))
    result = c.fetchone()
    conn.close()

    if not result:
        return None, "验证码不存在"

    max_uses, used_count, status = result

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
    c.execute('UPDATE verification_codes SET used_count = used_count + 1 WHERE code = ?', (code,))
    conn.commit()
    conn.close()


def log_generation(code, style, original_image, result_image, ip_address=None, user_agent=None):
    """记录生成历史（包含IP和用户代理）"""
    conn = get_db_connection()
    c = get_db_cursor(conn)
    c.execute('''
        INSERT INTO generation_logs (code, style, original_image, result_image, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (code, style, original_image, result_image, ip_address, user_agent))
    conn.commit()
    conn.close()


def log_verification_attempt(code, ip_address, success, failure_reason=None):
    """记录验证尝试（用于安全审计）"""
    conn = get_db_connection()
    c = get_db_cursor(conn)
    c.execute('''
        INSERT INTO verification_attempts (code, ip_address, success, failure_reason)
        VALUES (?, ?, ?, ?)
    ''', (code, ip_address, success, failure_reason))
    conn.commit()
    conn.close()


def call_nanobanana_api(image_path, style, clothing, background):
    """
    调用图片生成 API

    参数:
        style: 风格 (portrait)
        clothing: 服装 (business_suit, formal_dress, casual_shirt, turtleneck, tshirt)
        background: 背景 (gray, white, blue, warm)

    注意：当前使用模拟模式，对图片进行处理。
    要启用真实 API 生成，请配置支持图片生成的 API Key。
    """
    import base64
    from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
    import os

    # ==================== 基本关键词结构 ====================
    base_prompt = {
        "主体转换任务": {
            "目标风格": "美式专业职场风格",
            "肖像类型": "正面半身肖像"
        },
        "人物特征保留": {
            "五官": "100%还原原始五官特征",
            "发型": "保留原始发型",
            "身份一致性": "严格保持原始身份"
        },
        "视觉与构图": {
            "背景环境": "质感影棚背景，柔和自然光，背景略微虚化",
            "画质细节": "清晰对焦，肤色真实自然，构图干净优雅",
            "镜头语言": "微微倾斜镜头"
        },
        "姿态动作": {
            "体态": "如军人般挺拔，强调宽肩",
            "角度": "非正面（身体微侧，面部朝前）"
        },
        "画面尺寸": "3:4"
    }

    # ==================== 构建完整 prompt ====================
    # 服装和背景直接使用用户选择的值，不做转换
    full_prompt = base_prompt.copy()

    # 服装处理：如果选择"和原图保持一致"，使用特殊标记
    if clothing == 'keep_original':
        full_prompt["服装"] = "和原图保持一致"
    else:
        full_prompt["服装"] = clothing

    full_prompt["背景"] = background

    # ==================== 读取并编码图片 ====================
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()

    # ==================== 构建最终 JSON payload ====================
    payload = {
        "prompt": full_prompt,
        "image": image_data
    }

    # ==================== 打印 JSON 用于调试 ====================
    print(f"[API Request] JSON Prompt:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("-" * 60)

    # ========== 真实 API 调用部分 ==========
    api_key = os.getenv('NANOBANANA_API_KEY', '')
    api_url = os.getenv('NANOBANANA_API_URL', 'https://cdn.12ai.org/v1/images/edits')

    # 检查 API Key 是否配置
    if api_key:
        print(f"[API] API Key 已配置 (长度: {len(api_key)} 字符)")
        print(f"[API] API URL: {api_url}")
        try:
            print(f"[API] 开始调用 NanoBanana API...")
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            response = requests.post(api_url, json=payload, headers=headers, timeout=120)

            print(f"[API] 响应状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"[API] 响应键: {list(result.keys())}")
                print(f"[API] 响应内容预览: {json.dumps(result, ensure_ascii=False)[:300]}...")

                # 处理不同格式的响应
                # 格式1: {"image": "base64_string"}
                if 'image' in result:
                    import base64
                    image_data = base64.b64decode(result['image'])
                    result_path = image_path.replace('.', '_result.')
                    with open(result_path, 'wb') as f:
                        f.write(image_data)
                    print(f"[API] ✓ 图片生成成功 (base64格式): {result_path}")
                    return result_path

                # 格式2: {"url": "https://..."}
                elif 'url' in result:
                    img_response = requests.get(result['url'], timeout=30)
                    if img_response.status_code == 200:
                        result_path = image_path.replace('.', '_result.')
                        with open(result_path, 'wb') as f:
                            f.write(img_response.content)
                        print(f"[API] ✓ 图片下载成功 (URL格式): {result_path}")
                        return result_path
                    else:
                        print(f"[API] 下载图片失败: {img_response.status_code}")

                # 格式3: {"data": [{"b64_json": "..."}]}
                elif 'data' in result and len(result['data']) > 0:
                    import base64
                    image_data = base64.b64decode(result['data'][0].get('b64_json', ''))
                    result_path = image_path.replace('.', '_result.')
                    with open(result_path, 'wb') as f:
                        f.write(image_data)
                    print(f"[API] ✓ 图片生成成功 (data格式): {result_path}")
                    return result_path

                print(f"[API] ⚠ 未知响应格式，使用模拟模式")
            else:
                print(f"[API] ✗ API 调用失败: {response.status_code}")
                print(f"[API] 错误内容: {response.text[:500]}")

        except Exception as e:
            print(f"[API] ✗ API 调用异常: {type(e).__name__}: {e}")
            import traceback
            print(f"[API] 异常堆栈: {traceback.format_exc()}")
            print(f"[API] 将使用模拟模式")
    else:
        print(f"[API] ⚠ API Key 未配置，使用模拟模式")
        print(f"[API] 提示: 请在 Railway Variables 中设置 NANOBANANA_API_KEY")

    # ========== 模拟模式：对图片进行简单处理 ==========
    # 服装名称映射 (用于显示)
    clothing_names = {
        'business_suit': '商务西装',
        'formal_dress': '正装礼服',
        'casual_shirt': '休闲衬衫',
        'turtleneck': '高领毛衣',
        'tshirt': '简约T恤'
    }

    # 背景颜色映射 (用于模拟模式)
    background_colors = {
        'gray': (128, 128, 128),
        'white': (245, 245, 245),
        'blue': (102, 126, 234),
        'warm': (245, 147, 251)
    }

    try:
        # 打开原始图片
        img = Image.open(image_path)
        img = img.convert('RGBA')

        # 创建带背景的新图片
        bg_color = background_colors.get(background, (128, 128, 128))
        background_img = Image.new('RGBA', img.size, bg_color + (255,))
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
        print(f"  风格: {style}, 服装: {clothing}, 背景: {background}")

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
    background = request.form.get('background', 'gray')

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
        result_path = call_nanobanana_api(filepath, style, clothing, background)

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
        return jsonify({'success': False, 'message': f'生成失败: {str(e)}'}), 500


@app.route('/result/<filename>')
def result(filename):
    """返回生成的图片"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath)
    return "图片不存在", 404


@app.route('/debug/config')
def debug_config():
    """调试端点 - 检查配置（仅供调试使用）"""
    api_key = os.getenv('NANOBANANA_API_KEY', '')
    return jsonify({
        'api_key_configured': bool(api_key),
        'api_key_length': len(api_key) if api_key else 0,
        'api_key_prefix': api_key[:10] + '...' if api_key else None,
        'api_url': os.getenv('NANOBANANA_API_URL', 'https://cdn.12ai.org/v1/images/edits'),
        'db_type': db_type,
        'postgres_available': POSTGRES_AVAILABLE,
        'is_railway': is_railway
    })


@app.route('/api/status/<code>')
def status(code):
    """获取验证码状态"""
    result, error = verify_code(code)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    # 获取生成历史
    conn = get_db_connection()
    c = get_db_cursor(conn)
    c.execute('''
        SELECT style, created_at, result_image
        FROM generation_logs
        WHERE code = ?
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
            c.execute('INSERT INTO verification_codes (code, max_uses) VALUES (?, ?)', (code, max_uses))
            codes.append(code)
        except sqlite3.IntegrityError:
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
    c.execute('SELECT code FROM verification_codes WHERE status = "active" ORDER BY code')
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
    placeholders = ','.join(['?' for _ in codes])
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

    placeholders = ','.join(['?' for _ in codes])
    c.execute(f'UPDATE verification_codes SET status = ? WHERE code IN ({placeholders})', [status] + codes)

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

    c.execute('UPDATE verification_codes SET used_count = 0, status = "active" WHERE code = ?', (code,))

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
    print("🚀 肖像照生成服务启动成功!")
    print("📍 访问地址: http://localhost:5000")
    print("🔧 管理后台: http://localhost:5000/admin")
    print("💡 提示: 先运行 generate_codes.py 生成验证码")
    app.run(debug=True, host='0.0.0.0', port=5000)
