# 构建阶段
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.9-slim
WORKDIR /app

# 从构建阶段复制已安装的包
COPY --from=builder /root/.local /root/.local
COPY . .

# 确保脚本可执行
RUN chmod +x /app/scripts/*.sh

# 保持root用户
USER root

# 确保PATH包含用户安装目录
ENV PATH=/root/.local/bin:$PATH

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]