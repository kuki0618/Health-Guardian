import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from core import config, database
from services.dingtalk.user_service import UserService
from services.scheduler.scheduler_service import SchedulerService
from jobs.attendance_job import AttendanceJob
from jobs.status_job import StatusJob
from core import database
from api.endpoints import attendance, weather, user, calendar, freebusy, steps

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
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
app.include_router(attendance.router)
app.include_router(weather.router)
app.include_router(user.router)
app.include_router(calendar.router)
app.include_router(freebusy.router)
app.include_router(steps.router)

@app.get("/")
async def root():
    return {"message": "Health Guardian API is running"}
