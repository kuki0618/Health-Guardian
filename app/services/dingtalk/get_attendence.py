from core.config import CronTrigger,IntervalTrigger,BackgroundScheduler,FastAPI,HTTPException,BaseModel,Optional,httpx,datetime,timedelta,get_dingtalk_access_token,List

app = FastAPI(title="�����û���ϢAPI", version="1.0.0")

'''�������ݸ�ʽ'''
class AttendanceRequest(BaseModel):
    userid: str 
    start_time:str
    end_time:str
    cursor:int = 0
    size:int = 50

'''�������ݸ�ʽ'''
class CheckInRecord(BaseModel):
    checkin_time: int  # ǩ��ʱ�䣬��λ����
    detail_place: str  # ǩ����ϸ��ַ
    remark: str  # ǩ����ע
    userid: str  # �û�id
    place: str  # ǩ����ַ
    visit_user: str  # �ݷö���
    latitude: str  # γ��
    longitude: str  # ����
    image_list: List[str]  # ǩ����Ƭ�б�
    location_method: str  # ��λ����
    ssid: str  # SSID
    mac_addr: str  # Mac��ַ
    corp_id: str  # ��ҵid

class AttendanceResponse(BaseModel):
    success: bool  # �Ƿ�ɹ�
    result: Optional[List[CheckInRecord]] = None  # ǩ����¼�б�
    error_code: Optional[str] = None  # ������
    error_msg: Optional[str] = None  # ������Ϣ
    next_cursor: Optional[int] = None  # ��һ�β�ѯ���α�
    has_more: Optional[bool] = None  # �Ƿ��и�������

def datetime_to_timestamp(dt: datetime.datetime) -> int:
    """datetimeתʱ���(����)"""
    return int(dt.timestamp() * 1000)

def timestamp_to_datetime(timestamp: int) -> datetime.datetime:
    """ʱ���תdatetime"""
    return datetime.datetime.fromtimestamp(timestamp / 1000)
        

'''���������ȡǩ����¼'''  
async def get_checkin_records(start_time: int, end_time: int, userid_list: str,request:AttendanceRequest)-> List[CheckInRecord]:

    access_token = await get_dingtalk_access_token()
    
    # ���ö���API
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
                raise HTTPException(status_code=404, detail="�û�������")
            else:
                error_detail = e.response.json().get("message", "����API����ʧ��")
                raise HTTPException(status_code=e.response.status_code, detail=error_detail)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"���ö���APIʧ��: {str(e)}")
        
'''������ǩ����¼��ȡ����'''
async def scheduled_health_check(userid:str):
    # ��ȡ��ǰʱ��
    now = datetime.datetime.now()
    current_hour = now.hour
    
    # ȷ����ѯ��ʱ���
    if current_hour >= 8 and current_hour < 12:  # ��8�㵽12��֮��
        time_period = "morning"
        start_time = current_hour  # 08:00-12:00
        end_time = current_hour + 1
    elif current_hour >= 18 and current_hour < 20:  # ����6��
        time_period = "evening" 
        start_time = current_hour  
        end_time = current_hour + 1
    else:
        return
    
    # ת��Ϊʱ���
    start_timestamp = datetime_to_timestamp(start_time)
    end_timestamp = datetime_to_timestamp(end_time)
    
   # ��ȡǩ����¼
    records = await get_checkin_records(start_timestamp, end_timestamp, userid)
    return records

'''��ʱ����ǩ����¼'''
scheduler = BackgroundScheduler()
'''
# ÿ��12:00:00ִ�� - ����POST����
scheduler.add_job(
    scheduled_health_check,  # ��������ᷢ��POST����
    trigger=CronTrigger(hour=12, minute=0, second=0),  # ��ȷ��12:00:00
    id="noon_data_fetch"
)

# ÿ��18:00:00ִ�� - ����POST����  
scheduler.add_job(
    scheduled_health_check,  # ��������ᷢ��POST����
    trigger=CronTrigger(hour=18, minute=0, second=0),  # ��ȷ��18:00:00
    id="evening_data_fetch"
)

"""������ʱ����"""
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
