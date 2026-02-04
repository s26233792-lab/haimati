#!/bin/bash
# 启动脚本 - 本地开发使用

echo "安装依赖..."
pip install -r requirements.txt

echo "初始化数据库..."
python -c "from app import init_db; init_db()"

echo "启动服务..."
python app.py
