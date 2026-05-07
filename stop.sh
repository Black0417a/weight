NEW_FILE_CODE
#!/bin/bash

echo "========================================"
echo "  体重记录系统 - 停止中..."
echo "========================================"
echo ""

# 查找并停止后端进程
BACKEND_PIDS=$(ps aux | grep "[p]ython run.py" | awk '{print $2}')
if [ ! -z "$BACKEND_PIDS" ]; then
    echo "停止后端服务 (PIDs: $BACKEND_PIDS)..."
    echo $BACKEND_PIDS | xargs kill
else
    echo "未找到运行中的后端服务"
fi

# 查找并停止前端进程
FRONTEND_PIDS=$(ps aux | grep "[n]pm run dev" | grep "3001" | awk '{print $2}')
if [ ! -z "$FRONTEND_PIDS" ]; then
    echo "停止前端服务 (PIDs: $FRONTEND_PIDS)..."
    echo $FRONTEND_PIDS | xargs kill
else
    echo "未找到运行中的前端服务"
fi

sleep 2

# 检查是否还有残留进程
REMAINING=$(ps aux | grep -E "[p]ython run.py|[n]pm run dev.*3001" | awk '{print $2}')
if [ ! -z "$REMAINING" ]; then
    echo "强制终止残留进程..."
    echo $REMAINING | xargs kill -9
fi

echo ""
echo "服务已停止"
echo "========================================"
