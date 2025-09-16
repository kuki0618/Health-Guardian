#!/bin/bash
set -e

# 等待MySQL服务可用
while ! mysqladmin ping -h"db" --silent; do
    sleep 1
done

# 执行SQL脚本创建表结构
mysql -h db -u root -ppassword health_guardian < /app/app/repository/create_MySQL.sql

echo "Database initialized successfully!"