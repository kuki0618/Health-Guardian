from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .services.dingtalk import get_user_info,get_attendence,get_ifFree,get_schedule_list,get_sport_info,get_weather
from .repository import action
app = FastAPI()

attendance_manager = AttendanceManager()

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
            #��ԭ�����з�����Ϣ��ע��ǩ������ǩ�ˣ����Ƕ�д��һ������
            action.add_info(result)
            get_attendence.attendance_manager.mark_checked_in(userid)
        elif get_attendence.attendance_manager.should_check_out(userid):
            result = get_attendence.process_attendance_for_user(userid)
            get_attendence.attendance_manager.mark_checked_out(userid)
            action.add_info(result)

def conditional_status(userids: List[str]):
    for userid in userids:
        if attendance_manager.daily_status[userid]["checked_in"] == True and attendance_manager.daily_status[userid]["checked_out"] == False:
            result = get_ifFree.get_user_free_busy_status(userid)
            if len(result)!=0:
                action.insert_online_item(father_table_name="online_status",son_table_name="online_time_periods",data_list=result)
            
