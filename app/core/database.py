import mysql.connector
from mysql.connector import pooling
import os
from typing import Generator

# ���ݿ�����
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT")),
    "charset": "utf8mb4",
}

# �������ӳ�
connection_pool = pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=5,
    pool_reset_session=True,
    **db_config
)

def get_db_connection():
    #��ȡ���ݿ�����
    return connection_pool.get_connection()

def get_db():
    #����ע��ʹ�õ����ݿ�����
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()