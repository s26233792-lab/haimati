"""
生产环境启动文件
"""

from app import app
import os

# 生产环境配置
if __name__ == '__main__':
    # 确保 uploads 目录存在
    os.makedirs('uploads', exist_ok=True)

    # 检查环境变量
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key or secret_key == 'your-secret-key-change-this':
        print("⚠️  警告: 请设置 SECRET_KEY 环境变量!")
        print("   示例: export SECRET_KEY='your-random-secret-key-here'")

    # 启动服务（关闭 debug 模式）
    print("🚀 肖像照生成服务启动成功!")
    print("📍 访问地址: http://0.0.0.0:5000")
    print("🔧 管理后台: http://0.0.0.0:5000/admin")
    print("⚠️  注意: 管理后台目前无身份验证，请配置防火墙限制访问!")
    print()
    app.run(debug=False, host='0.0.0.0', port=5000)
