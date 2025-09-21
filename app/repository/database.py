import pymysql
import logging
from dbutils.pooled_db import PooledDB
from typing import Generator
from core import config

logger = logging.getLogger(__name__)

db_config = {
    "host":config.DB_HOST,
    "user": config.DB_USER,
    "password": config.DB_PASSWORD,
    "database": config.DB_NAME,
    "port": config.DB_PORT,
    "charset": "utf8mb4",
    "autocommit": True
}

connection_pool = None

def init_db():
    """
    初始化数据库连接池
    """
    global connection_pool
    if connection_pool is not None:
        return
    if connection_pool is None:
        connection_pool = PooledDB(
            creator=pymysql,
            maxconnections=5,
            mincached=2,
            maxcached=5,
            blocking=True,
            **db_config
        )
    logger.info("数据库连接池初始化成功")

def get_db_connection():
    if connection_pool is None:
        init_db()
    return connection_pool.connection()

def get_db() -> Generator:
    """
    获取数据库连接上下文管理器
    """
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def close_db():
    """
    关闭数据库连接池
    """
    global connection_pool
    if connection_pool:
        # DBUtils PooledDB 通常会自动管理连接关闭
        # 但我们可以手动关闭所有连接
        try:
            connection_pool.close()
            connection_pool = None
            logger.info("数据库连接池已关闭")
        except Exception as e:
            logger.debug(f"关闭数据库连接池时出错: {e}")
