#!/bin/bash

echo "========================================"
echo "  停止服务..."
echo "========================================"

# 停止后端
if [ -f logs/backend.pid ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    kill $BACKEND_PID 2>/dev/null
    rm -f logs/backend.pid
    echo "后端服务已停止"
fi

# 停止前端
if [ -f logs/frontend.pid ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    kill $FRONTEND_PID 2>/dev/null
    rm -f logs/frontend.pid
    echo "前端服务已停止"
fi

echo ""
echo "全部服务已停止"
echo "========================================"