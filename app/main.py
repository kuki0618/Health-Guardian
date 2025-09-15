import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from typing import List
from datetime import datetime,timedelta
import logging

from services.dingtalk import get_user_info,get_attendence,get_ifFree,get_schedule_list,get_sport_info,get_weather,send_message
from repository import action
from services.dingtalk import send_message 
from utils.change_time_format import change_time_format
from models import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

attendance_manager = get_attendence.AttendanceManager()

# 创建两个调度器实例
scheduler_status = AsyncIOScheduler()
scheduler_attendance = AsyncIOScheduler()

# 全局存储用户数据
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("启动应用初始化...")
        # 第一步：先获取所有用户数据
        userids = ["manager4585","604157341328085868","03366627182021511253"]
        
        for userid in userids:
            try:
                result = get_user_info(userid)
                action.create_item(table_name="employees", item=result)
                logger.info(f"成功获取用户 {userid} 数据")
            except Exception as e:
                logger.error(f"获取用户 {userid} 数据失败: {e}")
        
        # 第二步：用户数据就绪后，再启动定时任务
        
        # 启动状态检查调度器
        scheduler_status.add_job(
            conditional_status,
            trigger=IntervalTrigger(hours=1),
            replace_existing=True,
            args=[userids]  # 关键：传递用户数据给任务函数
        )
        
        if not scheduler_status.running:
            scheduler_status.start()
        
        # 启动考勤检查调度器
        scheduler_attendance.add_job(
            conditional_attendance,
            trigger=IntervalTrigger(hours=1),
            replace_existing=True,
            args=[userids]  # 关键：传递用户数据给任务函数
        )
        
        if not scheduler_attendance.running:
            scheduler_attendance.start()
           
        logger.info("调度器启动成功")
        
    except Exception as e:
        logger.error(f"启动失败: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("关闭应用...")
    if scheduler_status.running:
        scheduler_status.shutdown()
    if scheduler_attendance.running:
        scheduler_attendance.shutdown()

#检查用户是否应该签到
def conditional_attendance(userids:List[str]):
    for userid in userids:
        try:
            if get_attendence.attendance_manager.should_check_in(userid):
                result = get_attendence.process_attendance_for_user(userid)
                if result["action_taken"] and result["checked"]:
                #在原函数中返回信息标注好签到还是签退，但是都写在一个表里
                    action.add_attendence_info(result["data"])
                    get_attendence.attendance_manager.mark_checked_in(userid)
            elif get_attendence.attendance_manager.should_check_out(userid):
                result = get_attendence.process_attendance_for_user(userid)
                if result["action_taken"] and result["checked"]:
                #在原函数中返回信息标注好签到还是签退，但是都写在一个表里
                    action.add_attendence_info(result["data"])
                    get_attendence.attendance_manager.mark_checked_out(userid)
            logger.info(f"用户 {userid} 考勤处理成功")
        except Exception as e:
            logger.error(f"用户 {userid} 考勤处理失败: {e}")

#检查用户是否应该查询工作状态
def conditional_status(userids: List[str]):
    for userid in userids:
        try:
        #如果用户已经签到但是没有签退，那么就查询用户是否在线
            if attendance_manager.daily_status[userid]["checked_in"] == True and attendance_manager.daily_status[userid]["checked_out"] == False:
                result = get_ifFree.get_user_free_busy_status(userid)
                #如果在线，那么就插入数据
                if len(result)!=0:
                    action.insert_online_item(father_table_name="online_status",son_table_name="online_time_periods",data_list=result)
                    #如果用户在线时间超过90分钟，那么就发送消息
                    if change_time_format(result["start_time"],result["end_time"])>90 * 60:
                        user_msg = action.get_item_by_id(userid,timeable = "employees")
                        '''
                        "employee_info":{"userid":"manager4585","name":小赵,"title":"算法工程师","hobby":"散步",“age”:"25"},
                        '''
                        whether_msg = get_weather(os.getenv("AMAP_API_KEY"))
                        '''
                        "weather":{
                        "温度(℃)": weather_data["lives"][0]["temperature"],
                        "天气状况": weather_data["lives"][0]["weather"],
                        "湿度(%)": weather_data["lives"][0]["humidity"],
                        "风力": weather_data["lives"][0]["windpower"],
                        }
                        '''
                        #设计前七天的时间数据
                        target_times = []
                        for i in range(7):
                            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                            target_times.append(date)
                        before_msg = action.get_online_time_periods(userid,target_times)
                        '''
                        "work_status":{
                            "2023-10-01": [
                                ("2023-10-01 09:00:00", "2023-10-01 12:00:00"),
                                ("2023-10-01 14:00:00", "2023-10-01 18:00:00")
                            ],
                            "2023-10-02": [
                                ("2023-10-02 08:30:00", "2023-10-02 17:30:00")
                            ]
                        }  
                        '''
                        all_msg = {"employee_info":{**user_msg}, "weather":{**whether_msg}, "work_status":{**before_msg}} 
                        #通过函数传给大模型
                        health_msg = models.create_message(all_msg)
                        #调用发送消息函数发送消息
                        health_model = send_message.AsyncSendRequest(userid_list=[userid],msg_type="text",content=health_msg)
                        send_message.send_message(health_model)
                        #插入健康提醒数据到提醒表
                        action.insert_health_msg(user_id=userid,msg=health_msg,Time=datetime.now())
        except Exception as e:
            logger.error(f"发送健康提醒失败: {e}")


            
            
