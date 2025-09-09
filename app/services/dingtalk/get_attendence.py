from core.config import CronTrigger,IntervalTrigger,BackgroundScheduler,FastAPI,HTTPException,BaseModel,Optional,httpx,datetime,timedelta,get_dingtalk_access_token,List

app = FastAPI(title="钉钉用户信息API", version="1.0.0")

'''发送数据格式'''
class AttendanceRequest(BaseModel):
    userid: str 
    start_time:str
    end_time:str
    cursor:int = 0
    size:int = 50

'''返回数据格式'''
class CheckInRecord(BaseModel):
    checkin_time: int  # 签到时间，单位毫秒
    detail_place: str  # 签到详细地址
    remark: str  # 签到备注
    userid: str  # 用户id
    place: str  # 签到地址
    visit_user: str  # 拜访对象
    latitude: str  # 纬度
    longitude: str  # 经度
    image_list: List[str]  # 签到照片列表
    location_method: str  # 定位方法
    ssid: str  # SSID
    mac_addr: str  # Mac地址
    corp_id: str  # 企业id

class AttendanceResponse(BaseModel):
    success: bool  # 是否成功
    result: Optional[List[CheckInRecord]] = None  # 签到记录列表
    error_code: Optional[str] = None  # 错误码
    error_msg: Optional[str] = None  # 错误信息
    next_cursor: Optional[int] = None  # 下一次查询的游标
    has_more: Optional[bool] = None  # 是否还有更多数据

def datetime_to_timestamp(dt: datetime.datetime) -> int:
    """datetime转时间戳(毫秒)"""
    return int(dt.timestamp() * 1000)

def timestamp_to_datetime(timestamp: int) -> datetime.datetime:
    """时间戳转datetime"""
    return datetime.datetime.fromtimestamp(timestamp / 1000)
        

'''发送请求获取签到记录'''  
async def get_checkin_records(start_time: int, end_time: int, userid_list: str,request:AttendanceRequest)-> List[CheckInRecord]:

    access_token = await get_dingtalk_access_token()
    
    # 调用钉钉API
    url = "https://oapi.dingtalk.com/attendance/list"
    params = {"accessToken": access_token}
    headers = {"Content-Type": "application/json"}
    data = {"userid":  userid_list,
            "workDateFrom":start_time,
            "workDateTo":end_time}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, params=params,headers=headers,json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:  
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="用户不存在")
            else:
                error_detail = e.response.json().get("message", "钉钉API调用失败")
                raise HTTPException(status_code=e.response.status_code, detail=error_detail)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"调用钉钉API失败: {str(e)}")
        
'''完整的签到记录获取函数'''
async def scheduled_health_check(userid:str):
    # 获取当前时间
    now = datetime.datetime.now()
    current_hour = now.hour
    
    # 确定查询的时间段
    if current_hour >= 8 and current_hour < 12:  # 在8点到12点之间
        time_period = "morning"
        start_time = current_hour  # 08:00-12:00
        end_time = current_hour + 1
    elif current_hour >= 18 and current_hour < 20:  # 下午6点
        time_period = "evening" 
        start_time = current_hour  
        end_time = current_hour + 1
    else:
        return
    
    # 转换为时间戳
    start_timestamp = datetime_to_timestamp(start_time)
    end_timestamp = datetime_to_timestamp(end_time)
    
   # 获取签到记录
    records = await get_checkin_records(start_timestamp, end_timestamp, userid)
    return records

'''定时发送签到记录'''
scheduler = BackgroundScheduler()
'''
# 每天12:00:00执行 - 发送POST请求
scheduler.add_job(
    scheduled_health_check,  # 这个函数会发送POST请求
    trigger=CronTrigger(hour=12, minute=0, second=0),  # 精确到12:00:00
    id="noon_data_fetch"
)

# 每天18:00:00执行 - 发送POST请求  
scheduler.add_job(
    scheduled_health_check,  # 这个函数会发送POST请求
    trigger=CronTrigger(hour=18, minute=0, second=0),  # 精确到18:00:00
    id="evening_data_fetch"
)

"""启动定时任务"""
@app.on_event("startup")
async def startup_event():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
'''
@app.on_event("startup")
async def startup_event():
    scheduler.add_job(
        scheduled_health_check,
        trigger=IntervalTrigger(hours=1),
        replace_existing=True
    )
    
    # 启动调度器
    if not scheduler.running:
        scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭时停止调度器
    """
    if scheduler.running:
        scheduler.shutdown()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
