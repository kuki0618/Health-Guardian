import logging
from datetime import datetime, timedelta
from typing import List
from services.dingtalk.FreeBusy_service import FreeBusyService
from services.amap.weather_service import WeatherService
from services.dingtalk.attendance_service import AttendanceService
from services.dingtalk.message_service import SendMessageService
from services.dingtalk.user_service import UserService
from utils.change_time_format import change_time_format
from core import config
from api.models.FreeBusy import FreeBusyRequest
from api.models.message import AsyncSendRequest,Message,TextContent

logger = logging.getLogger(__name__)

class StatusJob:
    def __init__(self, 
                 freebusy_service: FreeBusyService,
                 weather_service: WeatherService,
                 attendance_service: AttendanceService,
                 message_service: SendMessageService,
                 user_service: UserService):
        self.freebusy_service = freebusy_service
        self.weather_service = weather_service
        self.attendance_service = attendance_service
        self.message_service = message_service
        self.user_service = user_service
    
    async def check_user_status_and_send_alerts(self, userids: List[str]):
        """检查用户状态并发送提醒"""
        for userid in userids:
            try:
                # 检查用户考勤状态
                attendance_status = await self.attendance_service.attendance_manager.daily_status(userid)
                
                if attendance_status["checked_in"] and not attendance_status["checked_out"]:
                    # 查询用户忙闲状态
                    freebusy_result = await self.freebusy_service.get_user_free_busy_status(userid)
                    
                    if freebusy_result != []:
                        await self.freebusy_service.insert_freebusy_record(userid, freebusy_result)
                        
                        # 检查在线时长
                        for i in len(freebusy_result):
                            online_duration += change_time_format( freebusy_result[i]["start_datetime"], freebusy_result[i]["end_datetime"])
                        
                        if online_duration > 90 * 60:  # 90分钟
                            await self._send_health_alert(userid)
                
            except Exception as e:
                logger.error(f"用户 {userid} 状态检查失败: {e}")
    
    async def _send_health_alert(self, userid: str):
        """发送健康提醒"""
        try:
            # 获取用户信息
            user_info = await self.user_service.get_user_details(userid)
            
            # 获取天气信息
            weather_info = await self.weather_service.get_weather_data(config.DEFAULT_CITY)
            
            # 获取最近7天工作状态
            target_dates = [
                (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") 
                for i in range(7)
            ]
            request = FreeBusyRequest(
                userIds=[userid],
                startTime=target_dates[6],
                endTime=target_dates[0]
            )
            work_status = await self.freebusy_service.get_user_free_busy_status(request)
            
            # 生成健康消息（这里可以调用AI模型）
            health_msg = await self._generate_health_message(user_info, weather_info, work_status)
            
            # 发送消息
            request = AsyncSendRequest(
            userid_list=userid,
            agent_id = int(config.AGENT_ID),
            msg=Message(
                msgtype="text",
                text=TextContent(
                    content= health_msg 
                )
            )
            )
            await self.message_service.async_send_message(request)
            
            # 保存提醒记录
            await self.message_service.insert_health_message(userid, health_msg, datetime.now(),conn= Depends(database.get_db))
            
        except Exception as e:
            logger.error(f"发送健康提醒失败: {e}")
    
    async def _generate_health_message(self, user_info, weather_info, work_status):
        """生成健康提醒消息(可以集成AI模型)"""
        # 这里可以是简单的规则，也可以调用AI服务
        return f"健康提醒: 您已连续工作较长时间，请注意休息。当前温度: {weather_info['temperature']}℃"