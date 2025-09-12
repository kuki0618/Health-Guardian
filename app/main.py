from .services.dingtalk.get_user_info import get_user_details
from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any 
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from services.dingtalk.get_attendence import AttendanceManager,process_attendance_for_user
from services.dingtalk.get_ifFree import get_user_free_busy_status
from core import database
from repository import action
from services.dingtalk.send_message import send_message

action.create_item()
action.get_tables(table_name="Allusers")

scheduler_attendence = BackgroundScheduler()
scheduler_status = BackgroundScheduler()

attendance_manager = AttendanceManager()

userids = ["zhangsan","lisi","zhaowu"]
AMAP_API_KEY = "d10ec8ed5659cf8d930ed3752b47efb5"

def conditional_attendence(userids:List[str]):
    for userid in userids:
        if attendance_manager.should_check_in(userid):
            result = process_attendance_for_user(userid)
            attendance_manager.mark_checked_in(userid)
        elif attendance_manager.should_check_out(userid):
            result = process_attendance_for_user(userid)
        attendance_manager.mark_checked_out(userid)

def conditional_status(userid: List[str]):
    for userid in userids:
        if attendance_manager.daily_status[userid]["checked_in"] == True and attendance_manager.daily_status[userid]["checked_out"] == False:
            result = get_user_free_busy_status(userid)

@app.on_event("startup")
async def startup_event():
    scheduler_status.add_job(
        conditional_attendence(),
        trigger=IntervalTrigger(hours=1),
        replace_existing=True
    )
    
    if not scheduler_status.running:
        scheduler_status.start()

@app.on_event("shutdown")
async def shutdown_event():
    if scheduler_status.running:
        scheduler_status.shutdown()

@app.on_event("startup")
async def startup_event():
    scheduler_attendence.add_job(
        conditional_status(),
        trigger=IntervalTrigger(hours=1),
        replace_existing=True
    )
    
    if not scheduler_attendence.running:
        scheduler_attendence.start()

@app.on_event("shutdown")
async def shutdown_event():
    if scheduler_attendence.running:
        scheduler_attendence.shutdown()

for userid in userids:
    result = get_user_details(userid)
    action.create_item(table_name="Allusers",item=result)

    #使用能相减的时间数据
    start_time = result["start"]["date"]
    end_time = result["end"]["date"]

    def condition_send():
        if end_time - start_time >= 1.5 and check_no_schedule(now):
            user_msg = get_item_by_id(userid,timeable = "用户信息")
            whether_msg = get_amap_weather( AMAP_API_KEY)
            before_msg = get_item_from_Mysql()
            send_deepseek_api()
            request = AsyncSendRequest(
                agent_id = 1000002,
                userid_list = [userid],
                text = 
            )
            send_message(request)


        


