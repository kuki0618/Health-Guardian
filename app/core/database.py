import pymysql
from dbutils.pooled_db import PooledDB
import os
from typing import Generator
from core import config

db_config = {
    "host":config.DB_HOST,
    "user": config.DB_USER,
    "password": config.DB_PASSWORD,
    "database": config.DB_NAME,
    "port": config.DB_PORT,
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