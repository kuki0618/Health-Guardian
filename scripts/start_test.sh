#!/bin/bash

# 加载测试环境变量
if [ -f ".env.test" ]; then
    export $(grep -v '^#' .env.test | xargs)
    echo "测试环境变量已加载"
else
    echo "警告：未找到 .env.test 文件"
fi


# 启动测试服务

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000