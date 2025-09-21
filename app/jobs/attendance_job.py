import logging
from datetime import datetime
from typing import List
from services.dingtalk.attendance_service import AttendanceService
from repository import database
from fastapi import Depends

logger = logging.getLogger(__name__)

class AttendanceJob:
    def __init__(self, attendance_service: AttendanceService):
        self.attendance_service = attendance_service
    
    async def job_process_attendance_for_users(self, userids: List[str]):
        """处理用户考勤任务"""
        for userid in userids:
            try:
                check_in_result = await self.attendance_service.attendance_manager.get_attendance_status(userid)
                check_in_result = check_in_result.get("checked_in", False)
                check_out_result = await self.attendance_service.attendance_manager.get_attendance_status(userid)
                check_out_result = check_out_result.get("checked_out", False)
                if not check_in_result and await self.attendance_service.attendance_manager.is_in_checkin_period():
                    result = await self.attendance_service.check_attendance_for_user(userid)
                    #写上班还是下班
                    logger.info(f"接收到用户{userid}签到数据：{result}")
                    check_in_result = result.action_taken and result.checked
                    if result.action_taken and result.checked:
                        await self.attendance_service.add_attendance_info(result.recordresult,conn=database.get_db_connection())
                        await self.attendance_service.attendance_manager.mark_checked_in(userid)
                        logger.info(f"用户 {userid} 已签到")
                
                if check_in_result and not check_out_result and await self.attendance_service.attendance_manager.is_in_checkout_period():
                    result = await self.attendance_service.check_attendance_for_user(userid)
                    #写上班还是下班
                    logger.info(f"接收到用户{userid}签退数据：{result}")
                    check_out_result = result.action_taken and result.checked
                    if result.action_taken and result.checked:
                        result.recordresult
                        await self.attendance_service.add_attendance_info(result.recordresult,conn=database.get_db_connection())
                        await self.attendance_service.attendance_manager.mark_checked_out(userid)
                        logger.info(f"用户 {userid} 已签退")
                
                logger.info(f"用户 {userid} 考勤处理成功，签到状态：{check_in_result}，签退状态：{check_out_result}")
                
            except Exception as e:
                logger.error(f"用户 {userid} 考勤处理失败: {e}")