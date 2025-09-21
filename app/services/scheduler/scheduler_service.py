import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from jobs.attendance_job import AttendanceJob
from jobs.status_job import StatusJob
from core import config

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self, 
                 attendance_job: AttendanceJob,
                 status_job: StatusJob):
        self.scheduler = AsyncIOScheduler()
        self.attendance_job = attendance_job
        self.status_job = status_job
    
    async def start_schedulers(self):
        """启动所有调度任务"""
        try:
            # 考勤检查任务 - 每小时执行
            self.scheduler.add_job(
                self.attendance_job.job_process_attendance_for_users,
                trigger=IntervalTrigger(hours=1),
                args=[config.USER_IDS],
                id="attendance_check"
            )
            
            # 状态检查任务 - 每30分钟执行
            self.scheduler.add_job(
                self.status_job.check_user_status_and_send_alerts,
                trigger=IntervalTrigger(minutes=2),
                args=[config.USER_IDS],
                id="status_check"
            )
            
            self.scheduler.start()
            logger.info("调度器启动成功")
            
        except Exception as e:
            logger.error(f"调度器启动失败: {e}")
            raise
    
    async def shutdown_schedulers(self):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("调度器已关闭")