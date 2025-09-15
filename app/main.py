from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .services.dingtalk import get_user_info,get_attendence,get_ifFree,get_schedule_list,get_sport_info,get_weather,send_message
from .repository import action
from .services.dingtalk import send_message 
from .utils.change_time_format import change_time_format
app = FastAPI()

attendance_manager = AttendanceManager()
AMAP_API_KEY = "d10ec8ed5659cf8d930ed3752b47efb5"

# 创建两个调度器实例
scheduler_status = AsyncIOScheduler()
scheduler_attendance = AsyncIOScheduler()

# 全局存储用户数据
user_data = []
@app.on_event("startup")
async def startup_event():
    global user_data
    
    # 第一步：先获取所有用户数据
    userids = ["manager4585","604157341328085868","03366627182021511253"]
    user_data = []
    
    for userid in userids:
        result = get_user_info(userid)
        user_data.append(result)
        action.create_item(table_name="employees",item=result)
    
    print(f"成功获取 {len(user_data)} 个用户数据")
    
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
            #在原函数中返回信息标注好签到还是签退，但是都写在一个表里
                action.add_attendence_info(result["data"])
                get_attendence.attendance_manager.mark_checked_in(userid)
        elif get_attendence.attendance_manager.should_check_out(userid):
            result = get_attendence.process_attendance_for_user(userid)
            if result["action_taken"] and result["checked"]:
            #在原函数中返回信息标注好签到还是签退，但是都写在一个表里
                action.add_attendence_info(result["data"])
                get_attendence.attendance_manager.mark_checked_out(userid)

def conditional_status(userids: List[str]):
    for userid in userids:
        #如果用户已经签到但是没有签退，那么就查询用户是否在线
        if attendance_manager.daily_status[userid]["checked_in"] == True and attendance_manager.daily_status[userid]["checked_out"] == False:
            result = get_ifFree.get_user_free_busy_status(userid)
            #如果在线，那么就插入数据
            if len(result)!=0:
                action.insert_online_item(father_table_name="online_status",son_table_name="online_time_periods",data_list=result)
                #如果用户在线时间超过90分钟，那么就发送消息
                if change_time_format(result["start_time"],result["end_time"])>90 * 60:
                    user_msg = action.get_item_by_id(userid,timeable = "employees")
                    whether_msg = get_weather(AMAP_API_KEY)
                    before_msg = action.get_online_time_periods(userid,father_table_name="online_status",son_table_name="online_time_periods",target_date="2024-08-13")
                    all_msg = {**user_msg, **whether_msg, **before_msg} 
                    #通过函数传给大模型
                    pass_data(all_msg)
                    health_msg = deepseek_info(userid)
                    #调用发送消息函数发送消息
                    health_model = send_message.AsyncSendRequest(userid_list=[userid],msg_type="text",content=health_msg)
                    send_message.send_message(health_model)
                    #插入健康提醒数据到提醒表
                    action.insert_health_msg(user_id=userid,msg=health_msg,Time=datetime.now())

            
            
