import pymysql
from dbutils.pooled_db import PooledDB
import os
from typing import Generator

db_config = {
    "host": os.getenv("DB_HOST","localhost"),
    "user": os.getenv("DB_USER","root"),
    "password": os.getenv("DB_PASSWORD","123456"),
    "database": os.getenv("DB_NAME","my_db"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "charset": "utf8mb4",
    "autocommit": True
}

# 使用 DBUtils 连接池
connection_pool = PooledDB(
    creator=pymysql,
    maxconnections=5,
    mincached=2,
    maxcached=5,
    blocking=True,
    **db_config
)

def get_db_connection():
    return connection_pool.connection()

def get_db() -> Generator:
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()