import mysql.connector
from mysql.connector import pooling
import os
from typing import Generator

# 数据库配置
db_config = {
    "host": "localhost",
    "user": "你的用户名",
    "password": "你的密码",
    "database": "my_db",
    "port": 3306,
    "charset": "utf8mb4",
}

# 创建连接池
connection_pool = pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=5,
    pool_reset_session=True,
    **db_config
)

def get_db_connection():
    """获取数据库连接"""
    return connection_pool.get_connection()

def get_db():
    """依赖注入使用的数据库连接"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()