from core.config import CronTrigger,IntervalTrigger,BackgroundScheduler,FastAPI,HTTPException,BaseModel,Optional,httpx,datetime,timedelta,get_dingtalk_access_token,List
import time as time_module

app = FastAPI(title="��������API", version="1.0.0")

def reschedule_data(data:dict):
    flat_data_list = []
    for item in data['recordresult']:
        userCheckTime = timestamp_to_datetime(item['userCheckTime'])
        flat_data = {
            # ��һ������
            'userid': item["userId"],
            'date':userCheckTime.strftime("%Y-%m-%d"),
            "datetime":userCheckTime.strftime("%Y-%m-%d %H:%M:%S"),
            'checkType':item['checkType'],
        }  
        flat_data_list.append(flat_data)
    return flat_data_list

def datetime_to_timestamp(dt: datetime.datetime) -> int:
    """datetimeתʱ���(����)"""
    return int(dt.timestamp() * 1000)

def timestamp_to_datetime(timestamp: int) -> datetime.datetime:
    """ʱ���תdatetime"""
    return datetime.datetime.fromtimestamp(timestamp / 1000)

class AttendanceManager:
    def __init__(self):
        # ʹ���ֵ�洢ÿ���ǩ��״̬ {date: {userid: {'checked_in': bool, 'checked_out': bool}}}
        self.daily_status: Dict[str, Dict[str, Dict[str, bool]]] = {}
        self.lock = asyncio.Lock()
    
    def _get_today_key(self) -> str:
        """��ȡ��������ڼ�"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def _is_in_time_period(self, start_hour: int, end_hour: int) -> bool:
        """��鵱ǰʱ���Ƿ���ָ��ʱ�����"""
        now = datetime.now()
        current_time = now.time()
        start_time = time(start_hour, 0)
        end_time = time(end_hour, 0)
        return start_time <= current_time <= end_time
    
    async def should_check_in(self, userid: str) -> bool:
        """����Ƿ�Ӧ��ִ��ǩ��"""
        async with self.lock:
            today = self._get_today_key()
            
            # ��ʼ������ļ�¼
            if today not in self.daily_status:
                self.daily_status[today] = {}
            if userid not in self.daily_status[today]:
                self.daily_status[today][userid] = {'checked_in': False, 'checked_out': False}
            
            # ����Ƿ���ǩ��ʱ����δǩ��
            in_checkin_period = self._is_in_time_period(8, 12)
            
            return in_checkin_period 
    
    async def should_check_out(self, userid: str) -> bool:
        """����Ƿ�Ӧ��ִ��ǩ��"""
        async with self.lock:
            today = self._get_today_key()
            
            # ��ʼ������ļ�¼
            if today not in self.daily_status:
                self.daily_status[today] = {}
            if userid not in self.daily_status[today]:
                self.daily_status[today][userid] = {'checked_in': False, 'checked_out': False}
            
            # ����Ƿ���ǩ��ʱ����δǩ��
            in_checkout_period = self._is_in_time_period(18, 20) 
            
            return in_checkout_period 
    
    async def mark_checked_in(self, userid: str):
        """���Ϊ��ǩ��"""
        async with self.lock:
            today = self._get_today_key()
            if today in self.daily_status and userid in self.daily_status[today]:
                self.daily_status[today][userid]['checked_in'] = True
    
    async def mark_checked_out(self, userid: str):
        """���Ϊ��ǩ��"""
        async with self.lock:
            today = self._get_today_key()
            if today in self.daily_status and userid in self.daily_status[today]:
                self.daily_status[today][userid]['checked_out'] = True
    
    def cleanup_old_records(self):
        """�������ڵļ�¼����ֹ�ڴ�й©��"""
        today = self._get_today_key()
        keys_to_remove = [key for key in self.daily_status.keys() if key != today]
        for key in keys_to_remove:
            if key in self.daily_status:
                del self.daily_status[key]

#��������޸ģ�ʹ֮�����Ҫ������
class AttendanceRequest(BaseModel):
    userIdList: List[str] 
    workDateFrom: str
    workDateTo: str
    limit: int = 0
    size: int = 50

class recordResult(BaseModel):
    userCheckTime:int
    checkType:str
    userId:str

class AttendanceResponse(BaseModel):
    recordresult: Optional[List[recordResult]] = None  # ǩ����¼�б�
    error_code: Optional[str] = None  # ������
    error_msg: Optional[str] = None  # ������Ϣ

@app.get("/{userid}/attendance",response_model=AttendanceResponse)       
async def process_attendance_for_user(userid:str):
    """Ϊ�����û���������"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")

        now = datetime.datetime.now()
        current_hour = now.hour
        start_time = current_hour  # 08:00-12:00
        end_time = current_hour + 1
        
        # ת��Ϊʱ���
        start_timestamp = datetime_to_timestamp(start_time)
        end_timestamp = datetime_to_timestamp(end_time)
        
        # ��ȡ��������
        access_token = await get_dingtalk_access_token()
        
        # ���ö���API
        url = "https://oapi.dingtalk.com/attendance/list"
        params = {"accessToken": access_token}
        headers = {"Content-Type": "application/json"}
        data = {
            "userIdList": [userid],
            "workDateFrom": start_timestamp,
            "workDateTo": end_timestamp
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params, headers=headers, json=data)
            response.raise_for_status()
            response = response.json()
            if data["recordresult"]:
                data = reschedule_data(data)
                return {
                    "action_taken": True,
                    "checked":True,
                    "data": data
                }
            else:
                return {
                    "action_taken": True,
                    "checked":False,
                }
            
    except Exception as e:
        print(f"�����û� {userid} ����ʱ����: {str(e)}")
        return {
            "action_taken": False,
            "error": str(e)
        }

