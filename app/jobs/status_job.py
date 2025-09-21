import logging
from datetime import datetime, timedelta
from typing import List
from repository import database
from services.dingtalk.FreeBusy_service import FreeBusyService
from services.amap.weather_service import WeatherService
from services.dingtalk.attendance_service import AttendanceService
from services.dingtalk.message_service import SendMessageService
from services.dingtalk.user_service import UserService
from services.dingtalk.steps_service import StepsService
from utils.change_time_format import change_time_format
from models.deepseek_model_server import create_message
from core import config
from api.models.FreeBusy import FreeBusyRequest
from api.models.message import AsyncSendRequest,Message,TextContent
from utils.find_userId_by_unionid import find_unionid_by_userId

logger = logging.getLogger(__name__)

class StatusJob:
    def __init__(self, 
                 freebusy_service: FreeBusyService,
                 weather_service: WeatherService,
                 attendance_service: AttendanceService,
                 message_service: SendMessageService,
                 user_service: UserService,
                 steps_service: StepsService):
        self.freebusy_service = freebusy_service
        self.weather_service = weather_service
        self.attendance_service = attendance_service
        self.message_service = message_service
        self.user_service = user_service
        self.steps_service = steps_service
    
    async def check_user_status_and_send_alerts(self, userids: List[str]):
        """检查用户状态并发送提醒"""
        
        logger.info(f"检查用户状态并发送提醒，用户列表：{userids}")
        for userid in userids:
            try:
                # 检查用户考勤状态          
                attendance_status = await self.attendance_service.attendance_manager.get_attendance_status(userid)
                check_in_result = attendance_status["checked_in"]
                check_out_result = attendance_status["checked_out"]
                logger.info(f"检查到用户 {userid} 考勤状态，签到状态：{check_in_result},签退状态：{check_out_result}")
                if check_in_result and not check_out_result:

                    logger.info(f"开始查询用户{userid}忙闲状态...")
                    freebusy_result = await self.freebusy_service.get_user_free_busy_now_status(userid)
                    if freebusy_result != []:
                        
                        logger.info(f"检查到用户 {userid} 忙碌：{freebusy_result}")
                        await self.freebusy_service.insert_freebusy_record(freebusy_result,conn=database.get_db_connection())
                        # 检查在线时长
                        online_duration = 0
                        for i in range(len(freebusy_result)):
                            online_duration += change_time_format( freebusy_result[i]["start_datetime"], freebusy_result[i]["end_datetime"])
                        
                        if online_duration > 90 * 60:  # 90分钟
                            logger.info(f"检查到用户 {userid} 忙碌时长超过90分钟")
                            await self._send_health_alert(userid)
                    else:
                        logger.info(f"检查到用户{userid}暂时没有忙碌状态")
                
            except Exception as e:
                logger.error(f"用户 {userid} 状态检查失败: {e}")
    
    async def _send_health_alert(self, userid: str):
        """发送健康提醒"""
        try:
            
            logger.info("开始生成并发送健康提醒...")

            # 获取用户信息
            user_info = await self.user_service.get_userinfo_from_database(userid)
            user_info_dict = { "employee_info": user_info}

            # 获取天气信息
            weather_info = await self.weather_service.get_weather_data(config.DEFAULT_CITY)
            weather_info_dict = { "weather": weather_info}

            # 获取最近7天工作状态
            target_dates = [
                (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%dT%H:%M:%S+08:00") 
                for i in range(7)
            ]

            unionid = await find_unionid_by_userId(userid,conn=database.get_db_connection())
            request = FreeBusyRequest(
                userIds=[unionid],
                startTime=target_dates[6],
                endTime=target_dates[0]
            )
            work_status = await self.freebusy_service.get_user_free_busy_status(request)
            work_status_dict = {"work_status": [item.model_dump() for item in work_status]}
            
            # 获取步数信息
            steps_info = await self.steps_service.get_steps_record(userid,date=datetime.now().strftime("%Y-%m-%d"),conn=database.get_db_connection())
            steps_info_dict = { "steps": steps_info}

            #整合所有数据
            all_data = {**user_info_dict, **weather_info_dict, **work_status_dict,**steps_info_dict}

            # 生成健康消息（这里可以调用AI模型）
            health_msg = await self._generate_health_message(all_data)
            
            logger.info(f"生成健康提醒：{health_msg}")
            
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
            await self.message_service.insert_health_message(userid, health_msg, datetime.now(),conn=database.get_db_connection())
            
        except Exception as e:
            logger.error(f"发送健康提醒失败: {e}")
    
    async def _generate_health_message(self, all_data:dict):
        """生成健康提醒消息(集成AI模型)"""
        content = create_message(all_data)
        return content