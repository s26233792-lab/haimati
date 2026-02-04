# Vercel WSGI 入口文件
# 用于 Vercel 部署

from app import app

# Vercel 需要的这个 WSGI 应用
wsgi_app = app

# 如果需要，可以添加 Vercel 特定的配置
if __name__ == '__main__':
    app.run()
