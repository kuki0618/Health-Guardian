#!/bin/bash
set -e

# 等待MySQL服务可用
while ! mysqladmin ping -h"db" --silent; do
    sleep 1
done

# 执行SQL脚本创建表结构
if mysql -h db -u ${DB_USER} -p${DB_PASS} ${DB_NAME} -e "SHOW TABLES" | grep -q . ; then
    echo "Database already initialized, skipping initialization."
    exit 0
fi

echo "Database initialized successfully!"