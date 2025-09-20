import logging
from datetime import datetime
from typing import List
from services.dingtalk.attendance_service import AttendanceService
from core import database
from fastapi import Depends

logger = logging.getLogger(__name__)

class AttendanceJob:
    def __init__(self, attendance_service: AttendanceService):
        self.attendance_service = attendance_service
    
    async def job_process_attendance_for_users(self, userids: List[str]):
        """处理用户考勤任务"""
        for userid in userids:
            try:
                should_check_in = await self.attendance_service.attendance_manager.should_check_in(userid)
                should_check_out = await self.attendance_service.attendance_manager.should_check_out(userid)
                
                if should_check_in:
                    result = await self.attendance_service.check_attendance_for_user(userid)
                    if result.action_taken and result.checked:
                        await self.attendance_service.add_attendance_info(result.recordresult,conn=Depends(database.get_db))
                        await self.attendance_service.attendance_manager.mark_checked_in(userid)
                        logger.info(f"用户 {userid} 已签到")
                
                elif should_check_out:
                    result = await self.attendance_service.check_attendance_for_user(userid)
                    if result.action_taken and result.checked:
                        await self.attendance_service.add_attendance_info(result.recordresult,conn=Depends(database.get_db))
                        await self.attendance_service.attendance_manager.mark_checked_out(userid)
                        logger.info(f"用户 {userid} 已签退")
                
                logger.info(f"用户 {userid} 考勤处理成功")
                
            except Exception as e:
                logger.error(f"用户 {userid} 考勤处理失败: {e}")