from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.dingtalk import get_user_info, get_attendence, get_ifFree, get_schedule_list, get_sport_info, get_weather, send_message
from app.repository import action
from app.utils.change_time_format import change_time_format
from typing import List
from datetime import datetime

class AttendanceManager:
    def __init__(self):
        self.daily_status = {}
app = FastAPI()

attendance_manager = AttendanceManager()
AMAP_API_KEY = "d10ec8ed5659cf8d930ed3752b47efb5"

# ��������������ʵ��
scheduler_status = AsyncIOScheduler()
scheduler_attendance = AsyncIOScheduler()

# ȫ�ִ洢�û�����
user_data = []
@app.on_event("startup")
async def startup_event():
    global user_data
    
    # ��һ�����Ȼ�ȡ�����û�����
    userids = ["manager4585","604157341328085868","03366627182021511253"]
    user_data = []
    
    for userid in userids:
        result = get_user_info(userid)
        user_data.append(result)
        action.create_item(table_name="employees",item=result)
    
    print(f"�ɹ���ȡ {len(user_data)} ���û�����")
    
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

@app.on_event("shutdown")
async def shutdown_event():
    if scheduler_status.running:
        scheduler_status.shutdown()
    if scheduler_attendance.running:
        scheduler_attendance.shutdown()

def conditional_attendance(userids:List[str]):
    for userid in userids:
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

def conditional_status(userids: List[str]):
    for userid in userids:
        #����û��Ѿ�ǩ������û��ǩ�ˣ���ô�Ͳ�ѯ�û��Ƿ�����
        if attendance_manager.daily_status[userid]["checked_in"] == True and attendance_manager.daily_status[userid]["checked_out"] == False:
            result = get_ifFree.get_user_free_busy_status(userid)
            #������ߣ���ô�Ͳ�������
            if len(result)!=0:
                action.insert_online_item(father_table_name="online_status",son_table_name="online_time_periods",data_list=result)
                #����û�����ʱ�䳬��90���ӣ���ô�ͷ�����Ϣ
                if change_time_format(result["start_time"],result["end_time"])>90 * 60:
                    user_msg = action.get_item_by_id(userid,timeable = "employees")
                    whether_msg = get_weather(AMAP_API_KEY)
                    before_msg = action.get_online_time_periods(userid,father_table_name="online_status",son_table_name="online_time_periods",target_date="2024-08-13")
                    all_msg = {**user_msg, **whether_msg, **before_msg} 
                    # 这里需要实现pass_data和deepseek_info函数
                    # 暂时注释掉这部分代码
                    # pass_data(all_msg)
                    # health_msg = deepseek_info(userid)
                    # health_model = send_message.AsyncSendRequest(
                    #     userid_list=[userid],
                    #     msg_type="text",
                    #     content="健康提醒测试消息"
                    # )
                    # send_message.send_message(health_model)
                    # action.insert_health_msg(
                    #     user_id=userid,
                    #     msg="健康提醒测试消息",
                    #     Time=datetime.now()
                    # )

            
            
