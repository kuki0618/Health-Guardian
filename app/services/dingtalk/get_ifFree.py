from core.config import uvicorn,IntervalTrigger,BackgroundScheduler,asyncio,FastAPI,HTTPException,BaseModel,Optional,httpx,datetime,timedelta,get_dingtalk_access_token,List

app = FastAPI(title="�����û�æ��״̬��ѯ����")
userids ={}

# ����ģ��
class FreeBusyRequest(BaseModel):
    userIds: List[str]  # �û�ID�б�
    timeMin: str  # ��ʼʱ��
    timeMax: str  # ����ʱ��

'''�������ݸ�ʽ'''
class FreeBusyItem(BaseModel):
    userId: str  # �û�ID
    busyStatus: str  # æ��״̬��free-�У�busy-æ
    startTime: str  # ��ʼʱ��
    endTime: str  # ����ʱ��

class FreeBusyResponse(BaseModel):
    requestId: str  # ����ID
    freeBusyItems: List[FreeBusyItem]  # æ��״̬�б�

async def get_user_free_busy_status(userid:str):
    """
    ��ȡ�û�æ��״̬���첽����
    """
    access_token = await get_dingtalk_access_token()

    # ���ò�ѯʱ�䷶Χ����ǰʱ�䵽2Сʱ��
    time_max = datetime.now()
    time_min = time_max - timedelta(hours=2)
    
    # ��ʽ��ʱ���ַ�����ISO 8601��ʽ��
    time_min_iso = time_min.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
    time_max_iso = time_max.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
    
    # ������������
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
                error_msg = f"æ��״̬��ѯʧ��: {response.status_code}, {response.text}"
                raise HTTPException(status_code=response.status_code, detail=error_msg)
                
    except httpx.RequestError as e:
        error_msg = f"�����������: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"��ѯ���̷����쳣: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)

def scheduled_free_busy_task():
    """
    ��ʱ������ - ÿ2Сʱִ��һ��
    """
    try:
        # �ں�̨�����첽����
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
    
    # ����������
    if not scheduler.running:
        scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    """
    Ӧ�ùر�ʱֹͣ������
    """
    if scheduler.running:
        scheduler.shutdown()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)