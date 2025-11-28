#!/bin/bash

echo "启动 FastAPI 用户管理系统..."

# 激活虚拟环境
source .venv/bin/activate

# 创建数据库表
echo "初始化数据库..."
python -c "from app.database import create_db_and_tables; create_db_and_tables()"

# 启动服务器
echo "启动服务器..."
python run.py &
SERVER_PID=$!

# 等待服务器启动
echo "等待服务器启动..."
sleep 5

# 执行详细测试
echo "执行详细的API测试..."
python test_api_detailed.py

# 显示访问信息
echo ""
echo "================================================================="
echo "FastAPI用户管理系统已启动完成！"
echo "服务器运行在: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "停止服务器: kill $SERVER_PID"
echo "================================================================="
echo ""

# 等待服务器运行
wait $SERVER_PID