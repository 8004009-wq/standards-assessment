#!/bin/bash

# 标准自评估系统 - 一键启动脚本

echo "🛡️  标准自评估系统"
echo "=================="

# 创建数据目录
mkdir -p data/uploads

# 安装依赖
echo "📦 检查后端依赖..."
cd backend
if ! command -v pip3 &> /dev/null; then
    echo "❌ 未找到 pip3，请先安装 Python3 和 pip"
    exit 1
fi

pip3 install -q -r requirements.txt

# 启动后端
echo "🚀 启动后端服务..."
cd ..

# 检查端口是否被占用
if lsof -i:8001 > /dev/null 2>&1; then
    echo "⚠️  端口 8001 已被占用，请先停止占用该端口的进程"
    exit 1
fi

# 后台启动后端
nohup python3 -c "
import sys
sys.path.insert(0, 'backend')
from main import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8001)
" > backend/server.log 2>&1 &

BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端启动
sleep 3

# 检查后端是否正常启动
if ! curl -s http://localhost:8001/api/health > /dev/null; then
    echo "❌ 后端服务启动失败，请查看 backend/server.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ 后端服务运行正常"

# 启动前端
echo "🌐 启动前端服务..."
if lsof -i:8080 > /dev/null 2>&1; then
    echo "⚠️  端口 8080 已被占用"
else
    cd frontend
    python3 -m http.server 8080 > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
    cd ..
fi

echo ""
echo "=================="
echo "🎉 系统启动成功！"
echo ""
echo "📱 前端地址：http://localhost:8080"
echo "🔧 后端 API: http://localhost:8001"
echo "📖 API 文档：http://localhost:8001/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=================="

# 保存 PID 文件
echo $BACKEND_PID > backend.pid
if [ -n "$FRONTEND_PID" ]; then
    echo $FRONTEND_PID > frontend.pid
fi

# 等待用户中断
trap "echo ''; echo '👋 正在停止服务...'; kill $BACKEND_PID 2>/dev/null; kill $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

wait
