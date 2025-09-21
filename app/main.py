import logging
import logging.config
import json
import os
import sys
from pathlib import Path
from fastapi import FastAPI,Request
from contextlib import asynccontextmanager

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir) 
sys.path.insert(0, app_dir) 

from app.core import config
from app.repository import database
from app.services.scheduler.scheduler_service import SchedulerService
from app.services.dingtalk.FreeBusy_service import FreeBusyService
from app.services.amap.weather_service import WeatherService
from app.services.dingtalk.attendance_service import AttendanceService,AttendanceManager
from app.services.dingtalk.message_service import SendMessageService
from app.services.dingtalk.user_service import UserService
from app.jobs.attendance_job import AttendanceJob
from app.jobs.status_job import StatusJob
from app.repository import database
from app.api.endpoints import Attendance, Weather, User, Calendar, FreeBusy, Steps

# 配置日志
def setup_logging():
  
    project_root = Path(__file__).parent

    config_path = project_root / "logs" / "logging_app_config.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Logging config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    config["disable_existing_loggers"] = False

    logging.config.dictConfig(config)
    print(f"Logging configured from: {config_path}")

# 在程序最开始调用配置函数

@asynccontextmanager
async def lifespan(app: FastAPI):
    #配置日志
    setup_logging()

    logger = logging.getLogger("app") 

    # 启动应用
    logger.info("应用启动中...")
    
    # 初始化数据库
    database.init_db()
    
    # 初始化用户数据
    user_service = UserService()
    logger.info(f"获取并保存以下用户信息: {config.USER_IDS}")
    for userid in config.USER_IDS:
        try:
            user_info = await user_service.get_user_details(userid)
            user_dict = user_info.model_dump() 
            user_service.add_employee_info(user_dict,conn=database.get_db_connection())
            # 保存用户信息到数据库
            logger.info(f"用户 {userid} 数据初始化成功")
        except Exception as e:
            logger.error(f"用户 {userid} 数据初始化失败: {e}")
    
    # 初始化调度器
    attendance_manager = AttendanceManager()
    attendance_service = AttendanceService(attendance_manager)

    free_busy_service = FreeBusyService()
    weather_service = WeatherService()
    message_service = SendMessageService()
    user_service= UserService()

    # 然后创建 attendance_job，传入必需的参数
    attendance_job = AttendanceJob(attendance_service)

    status_job = StatusJob(free_busy_service, weather_service, attendance_service, message_service, user_service)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
