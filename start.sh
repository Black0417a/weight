#!/bin/bash

echo "========================================"
echo "  体重记录系统 - 启动中..."
echo "========================================"

cd "$(dirname "$0")"

# 创建日志目录
mkdir -p logs

########################################
# 启动后端
########################################

echo ""
echo "正在启动后端服务..."

cd backend

nohup gunicorn -w 4 -b 0.0.0.0:6000 run:app \
> ../logs/backend.log 2>&1 &

BACKEND_PID=$!

echo "后端进程 PID: $BACKEND_PID"

cd ..

sleep 3

########################################
# 启动前端
########################################

echo ""
echo "正在启动前端服务..."

cd frontend

nohup serve -s dist -l 3001 \
> ../logs/frontend.log 2>&1 &

FRONTEND_PID=$!

echo "前端进程 PID: $FRONTEND_PID"

cd ..

########################################
# 保存 PID
########################################

echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

########################################
# 输出信息
########################################

echo ""
echo "========================================"
echo "  服务已启动！"
echo "========================================"

echo "后端地址:"
echo "  http://127.0.0.1:6000"

echo ""
echo "前端地址:"
echo "  http://127.0.0.1:3001"

echo ""
echo "日志文件:"
echo "  后端: logs/backend.log"
echo "  前端: logs/frontend.log"

echo ""
echo "查看日志:"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"

echo ""
echo "停止服务:"
echo "  ./stop.sh"

echo "========================================"