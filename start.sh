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

nohup gunicorn \
-w 4 \
-b 127.0.0.1:6000 \
--proxy-allow-ips="*" \
run:app \
> ../logs/backend.log 2>&1 &

BACKEND_PID=$!

echo "后端进程 PID: $BACKEND_PID"

cd ..

########################################
# 保存 PID
########################################

echo $BACKEND_PID > logs/backend.pid

########################################
# 输出信息
########################################

echo ""
echo "========================================"
echo "  服务已启动！"
echo "========================================"

echo ""
echo "访问地址:"
echo "  http://你的域名/weight/"

echo ""
echo "API:"
echo "  http://你的域名/weight/api/"

echo ""
echo "日志文件:"
echo "  后端: logs/backend.log"

echo ""
echo "查看日志:"
echo "  tail -f logs/backend.log"

echo ""
echo "停止服务:"
echo "  ./stop.sh"

echo "========================================"