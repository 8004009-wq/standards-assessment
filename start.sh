#!/bin/bash

echo "=== 标准智能评估系统启动脚本 ==="

# 检查环境变量
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "警告：DASHSCOPE_API_KEY 未设置，大模型功能将不可用"
    echo "请设置：export DASHSCOPE_API_KEY='your-api-key'"
fi

# 启动后端
echo "启动后端服务..."
cd backend
pip install -r requirements.txt -q
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo "启动前端服务..."
cd frontend
npm install -q
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== 服务已启动 ==="
echo "后端：http://localhost:8000"
echo "前端：http://localhost:3000"
echo "API 文档：http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"

wait
