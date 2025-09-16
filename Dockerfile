# 构建阶段 - 安装依赖
FROM python:3.9-slim as builder

WORKDIR /app
# 复制项目配置文件
COPY pyproject.toml .
# 安装构建工具和项目依赖
RUN pip install --user --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# 运行阶段 - 最小化镜像
FROM python:3.9-slim
WORKDIR /app

# 从构建阶段复制已安装的包
COPY --from=builder /root/.local /root/.local
# 复制项目文件
COPY . .

# 设置环境变量
ENV PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# 设置健康检查（检查端口可用性）
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import socket; exit(0 if socket.socket().connect_ex(('localhost',8000)) == 0 else 1)"

# 当前执行为 start_test.sh 测试环境
# 确保脚本可执行
RUN chmod +x /app/scripts/*.sh

# 暴露端口
EXPOSE 8000

# 检查 3306数据库端口
# 检查 8000FastAPI端口
# 启动命令（带初始化等待）
CMD ["sh", "-c", \
    "while ! nc -z db 3306; do sleep 2; done && \
    ./init_db.sh && \
    uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --no-access-log"]