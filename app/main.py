import os
import sys
from pathlib import Path

# �����Ŀ��Ŀ¼��Python·��
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

# ��������������ʵ��
scheduler_status = AsyncIOScheduler()
scheduler_attendance = AsyncIOScheduler()

# ȫ�ִ洢�û�����
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("����Ӧ�ó�ʼ��...")
        # ��һ�����Ȼ�ȡ�����û�����
        userids = ["manager4585","604157341328085868","03366627182021511253"]
        
        for userid in userids:
            try:
                result = get_user_info(userid)
                action.create_item(table_name="employees", item=result)
                logger.info(f"�ɹ���ȡ�û� {userid} ����")
            except Exception as e:
                logger.error(f"��ȡ�û� {userid} ����ʧ��: {e}")
        
        # �ڶ������û����ݾ�������������ʱ����
        
        # ����״̬��������
        scheduler_status.add_job(
            conditional_status,
            trigger=IntervalTrigger(hours=1),
            replace_existing=True,
            args=[userids]  # �ؼ��������û����ݸ�������
        )
        
        if not scheduler_status.running:
            scheduler_status.start()
        
        # �������ڼ�������
        scheduler_attendance.add_job(
            conditional_attendance,
            trigger=IntervalTrigger(hours=1),
            replace_existing=True,
            args=[userids]  # �ؼ��������û����ݸ�������
        )
        
        if not scheduler_attendance.running:
            scheduler_attendance.start()
           
        logger.info("�����������ɹ�")
        
    except Exception as e:
        logger.error(f"����ʧ��: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("�ر�Ӧ��...")
    if scheduler_status.running:
        scheduler_status.shutdown()
    if scheduler_attendance.running:
        scheduler_attendance.shutdown()

#����û��Ƿ�Ӧ��ǩ��
def conditional_attendance(userids:List[str]):
    for userid in userids:
        try:
            if get_attendence.attendance_manager.should_check_in(userid):
                result = get_attendence.process_attendance_for_user(userid)
                if result["action_taken"] and result["checked"]:
                #��ԭ�����з�����Ϣ��ע��ǩ������ǩ�ˣ����Ƕ�д��һ������
                    action.add_attendence_info(result["data"])
                    get_attendence.attendance_manager.mark_checked_in(userid)
            elif get_attendence.attendance_manager.should_check_out(userid):
                result = get_attendence.process_attendance_for_user(userid)
                if result["action_taken"] and result["checked"]:
                #��ԭ�����з�����Ϣ��ע��ǩ������ǩ�ˣ����Ƕ�д��һ������
                    action.add_attendence_info(result["data"])
                    get_attendence.attendance_manager.mark_checked_out(userid)
            logger.info(f"�û� {userid} ���ڴ���ɹ�")
        except Exception as e:
            logger.error(f"�û� {userid} ���ڴ���ʧ��: {e}")

#����û��Ƿ�Ӧ�ò�ѯ����״̬
def conditional_status(userids: List[str]):
    for userid in userids:
        try:
        #����û��Ѿ�ǩ������û��ǩ�ˣ���ô�Ͳ�ѯ�û��Ƿ�����
            if attendance_manager.daily_status[userid]["checked_in"] == True and attendance_manager.daily_status[userid]["checked_out"] == False:
                result = get_ifFree.get_user_free_busy_status(userid)
                #������ߣ���ô�Ͳ�������
                if len(result)!=0:
                    action.insert_online_item(father_table_name="online_status",son_table_name="online_time_periods",data_list=result)
                    #����û�����ʱ�䳬��90���ӣ���ô�ͷ�����Ϣ
                    if change_time_format(result["start_time"],result["end_time"])>90 * 60:
                        user_msg = action.get_item_by_id(userid,timeable = "employees")
                        '''
                        "employee_info":{"userid":"manager4585","name":С��,"title":"�㷨����ʦ","hobby":"ɢ��",��age��:"25"},
                        '''
                        whether_msg = get_weather(os.getenv("AMAP_API_KEY"))
                        '''
                        "weather":{
                        "�¶�(��)": weather_data["lives"][0]["temperature"],
                        "����״��": weather_data["lives"][0]["weather"],
                        "ʪ��(%)": weather_data["lives"][0]["humidity"],
                        "����": weather_data["lives"][0]["windpower"],
                        }
                        '''
                        #���ǰ�����ʱ������
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
                        #ͨ������������ģ��
                        health_msg = models.create_message(all_msg)
                        #���÷�����Ϣ����������Ϣ
                        health_model = send_message.AsyncSendRequest(userid_list=[userid],msg_type="text",content=health_msg)
                        send_message.send_message(health_model)
                        #���뽡���������ݵ����ѱ�
                        action.insert_health_msg(user_id=userid,msg=health_msg,Time=datetime.now())
        except Exception as e:
            logger.error(f"���ͽ�������ʧ��: {e}")


            
            
