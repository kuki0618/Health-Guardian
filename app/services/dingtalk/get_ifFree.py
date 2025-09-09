from core.config import uvicorn,IntervalTrigger,BackgroundScheduler,asyncio,FastAPI,HTTPException,BaseModel,Optional,httpx,datetime,timedelta,get_dingtalk_access_token,List

app = FastAPI(title="钉钉用户忙闲状态查询服务")
userids ={}

# 请求模型
class FreeBusyRequest(BaseModel):
    userIds: List[str]  # 用户ID列表
    timeMin: str  # 开始时间
    timeMax: str  # 结束时间

'''返回数据格式'''
class FreeBusyItem(BaseModel):
    userId: str  # 用户ID
    busyStatus: str  # 忙闲状态：free-闲，busy-忙
    startTime: str  # 开始时间
    endTime: str  # 结束时间

class FreeBusyResponse(BaseModel):
    requestId: str  # 请求ID
    freeBusyItems: List[FreeBusyItem]  # 忙闲状态列表

async def get_user_free_busy_status(userid:str):
    """
    获取用户忙闲状态的异步函数
    """
    access_token = await get_dingtalk_access_token()

    # 设置查询时间范围（当前时间到2小时后）
    time_max = datetime.now()
    time_min = time_max - timedelta(hours=2)
    
    # 格式化时间字符串（ISO 8601格式）
    time_min_iso = time_min.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
    time_max_iso = time_max.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
    
    # 构建请求数据
    data = {
        "userIds": "",
        "timeMin": time_min_iso,
        "timeMax": time_max_iso
    }
    
    url = f"/v1.0/calendar/users/{userid}/getSchedule HTTP/1.1"
    params = {"accessToken": access_token}
    headers = {"Content-Type": "application/json"}
    try:
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, params=params,headers=headers,json=data)
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                error_msg = f"忙闲状态查询失败: {response.status_code}, {response.text}"
                raise HTTPException(status_code=response.status_code, detail=error_msg)
                
    except httpx.RequestError as e:
        error_msg = f"网络请求错误: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"查询过程发生异常: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)

def scheduled_free_busy_task():
    """
    定时任务函数 - 每2小时执行一次
    """
    try:
        # 在后台运行异步任务
        for userid in userids:
            asyncio.create_task(get_user_free_busy_status(userid))
    except Exception as e:
        pass

scheduler = BackgroundScheduler()

@app.on_event("startup")
async def startup_event():
    scheduler.add_job(
        scheduled_free_busy_task,
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