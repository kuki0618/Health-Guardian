import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import timedelta
from jobs.attendance_job import AttendanceJob
from jobs.status_job import StatusJob
from core import config

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self, 
                 attendance_job: AttendanceJob,
                 status_job: StatusJob):
        self.attendance_scheduler = AsyncIOScheduler()
        self.status_scheduler = AsyncIOScheduler()
        self.attendance_job = attendance_job
        self.status_job = status_job
        self.last_attendance_time = None
        self.status_waiting = False
    
    async def start_schedulers(self):
        """启动所有调度任务"""
        try:
            # 考勤检查任务 - 每一小时
            self.attendance_scheduler.add_job(
                self._run_attendance_and_trigger_status,
                trigger=IntervalTrigger(hours=1),
                args=[config.USER_IDS],
                id="attendance_check",
                next_run_time=datetime.now()
            )
            
            # 状态检查任务 - 每两小时，但只在考勤后执行
            self.status_scheduler.add_job(
                self._run_status_if_ready,
                trigger=IntervalTrigger(hours=2),
                args=[config.USER_IDS],
                id="status_check",
                next_run_time=datetime.now() + timedelta(seconds=5)
            )
            
            self.attendance_scheduler.start()
            self.status_scheduler.start()
            logger.info("调度器启动成功")
            
        except Exception as e:
            logger.error(f"调度器启动失败: {e}")
            raise
    
    async def _run_attendance_and_trigger_status(self, user_ids):
        """执行考勤任务并标记状态检查就绪"""
        try:
            logger.info("开始执行考勤检查任务...")
            await self.attendance_job.job_process_attendance_for_users(user_ids)
            self.last_attendance_time = datetime.now()
            self.status_waiting = True
            logger.info("考勤检查任务完成，状态检查就绪")
            
        except Exception as e:
            logger.error(f"考勤任务执行失败: {e}")
    
    async def _run_status_if_ready(self, user_ids):
        """只在考勤任务完成后执行状态检查"""
        if not self.status_waiting:
            logger.info("状态检查：等待考勤任务完成...")
            return
            
        try:
            logger.info("开始执行状态检查任务...")
            await self.status_job.check_user_status_and_send_alerts(user_ids)
            logger.info("状态检查任务完成")
            self.status_waiting = False
            
        except Exception as e:
            logger.error(f"状态检查任务执行失败: {e}")