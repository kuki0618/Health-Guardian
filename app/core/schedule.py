import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from typing import List
from services.dingtalk.attendance_service import AttendanceManager, conditional_attendance, conditional_status
from services.dingtalk.get_user_info import get_user_details
from repository import action

logger = logging.getLogger(__name__)

attendance_manager = AttendanceManager()
scheduler_status = AsyncIOScheduler()
scheduler_attendance = AsyncIOScheduler()

async def init_schedulers():
    """初始化所有调度器"""
    try:
        userids = ["manager4585", "604157341328085868", "03366627182021511253"]
        
        for userid in userids:
            try:
                result = get_user_details(userid)
                action.create_item(table_name="employees", item=result)
                logger.info(f"成功获取用户 {userid} 数据")
            except Exception as e:
                logger.error(f"获取用户 {userid} 数据失败: {e}")
        
        # 启动状态检查调度器
        scheduler_status.add_job(
            conditional_status,
            trigger=IntervalTrigger(hours=1),
            replace_existing=True,
            args=[userids]
        )
        
        # 启动考勤检查调度器
        scheduler_attendance.add_job(
            conditional_attendance,
            trigger=IntervalTrigger(hours=1),
            replace_existing=True,
            args=[userids]
        )
        
        scheduler_status.start()
        scheduler_attendance.start()
        logger.info("调度器启动成功")
        
    except Exception as e:
        logger.error(f"调度器启动失败: {e}")
        raise

async def shutdown_schedulers():
    """关闭所有调度器"""
    if scheduler_status.running:
        scheduler_status.shutdown()
    if scheduler_attendance.running:
        scheduler_attendance.shutdown()
    logger.info("调度器已关闭")