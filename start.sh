NEW_FILE_CODE
#!/bin/bash

echo "========================================"
echo "  体重记录系统 - 启动中..."
echo "========================================"
echo ""

# 切换到项目根目录
cd "$(dirname "$0")"

# 启动后端（后台运行）
echo "正在启动后端服务..."
cd backend
nohup python run.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端进程 PID: $BACKEND_PID"
cd ..

# 等待后端启动
sleep 3

# 启动前端（后台运行，端口3001）
echo "正在启动前端服务..."
cd frontend
nohup npm run dev -- --port 3001 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端进程 PID: $FRONTEND_PID"
cd ..

# 创建日志目录（如果不存在）
mkdir -p logs

echo ""
echo "========================================"
echo "  服务已启动！"
echo "========================================"
echo "后端: http://127.0.0.1:6000 (PID: $BACKEND_PID)"
echo "前端: http://localhost:3001 (PID: $FRONTEND_PID)"
echo ""
echo "查看日志:"
echo "  后端: tail -f logs/backend.log"
echo "  前端: tail -f logs/frontend.log"
echo ""
echo "停止服务:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "  或运行: ./stop.sh"
echo "========================================"
