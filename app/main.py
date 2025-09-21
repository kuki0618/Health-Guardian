import logging
import logging.config
import json
import os
from pathlib import Path
from repository import database
from fastapi import FastAPI,Request
from contextlib import asynccontextmanager

from core import config
from services.dingtalk.user_service import UserService
from services.scheduler.scheduler_service import SchedulerService
from jobs.attendance_job import AttendanceJob
from jobs.status_job import StatusJob
from repository import database
from api.endpoints import Attendance, Weather, User, Calendar, FreeBusy, Steps

# 配置日志
def setup_logging():
  
    project_root = Path(__file__).parent.parent

    config_path = project_root / "log" / "logging_app_config.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Logging config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.config.dictConfig(config)
    print(f"Logging configured from: {config_path}")

# 在程序最开始调用配置函数

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    #配置日志
    setup_logging()

    # 启动应用
    logger.info("应用启动中...")
    
    # 初始化数据库
    await database.init_db()
    
    # 初始化用户数据
    user_service = UserService()
    logger.info(f"获取并保存以下用户信息: {config.USER_IDS}")
    for userid in config.USER_IDS:
        try:
            user_info = await user_service.get_user_details(userid)
            user_service.add_employee_info(user_info,conn=database.get_db())
            # 保存用户信息到数据库
            logger.info(f"用户 {userid} 数据初始化成功")
        except Exception as e:
            logger.error(f"用户 {userid} 数据初始化失败: {e}")
    
    # 初始化调度器
    attendance_job = AttendanceJob()
    status_job = StatusJob()
    scheduler_service = SchedulerService(attendance_job, status_job)
    
    await scheduler_service.start_schedulers()
    app.state.scheduler_service = scheduler_service
    
    yield
    
    # 关闭应用
    logger.info("应用关闭中...")
    await scheduler_service.shutdown_schedulers()
    await database.close_db()

# 创建FastAPI应用
app = FastAPI(
    title="Health Guardian API",
    version="1.0.0",
    lifespan=lifespan
)

# 注册路由
app.include_router(Attendance.router)
app.include_router(Weather.router)
app.include_router(User.router)
app.include_router(Calendar.router)
app.include_router(FreeBusy.router)
app.include_router(Steps.router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_logger = logging.getLogger("http")
    request_logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    request_logger.info(f"Response: {response.status_code}")
    return response

@app.get("/")
async def root():
    return {"message": "Health Guardian API is running"}
