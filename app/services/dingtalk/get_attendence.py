from core.config import CronTrigger,IntervalTrigger,BackgroundScheduler,FastAPI,HTTPException,BaseModel,Optional,httpx,datetime,timedelta,get_dingtalk_access_token,List
import time as time_module

app = FastAPI(title="钉钉考勤API", version="1.0.0")

def datetime_to_timestamp(dt: datetime.datetime) -> int:
    """datetime转时间戳(毫秒)"""
    return int(dt.timestamp() * 1000)

def timestamp_to_datetime(timestamp: int) -> datetime.datetime:
    """时间戳转datetime"""
    return datetime.datetime.fromtimestamp(timestamp / 1000)

class AttendanceManager:
    def __init__(self):
        # 使用字典存储每天的签到状态 {date: {userid: {'checked_in': bool, 'checked_out': bool}}}
        self.daily_status: Dict[str, Dict[str, Dict[str, bool]]] = {}
        self.lock = asyncio.Lock()
    
    def _get_today_key(self) -> str:
        """获取今天的日期键"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def _is_in_time_period(self, start_hour: int, end_hour: int) -> bool:
        """检查当前时间是否在指定时间段内"""
        now = datetime.now()
        current_time = now.time()
        start_time = time(start_hour, 0)
        end_time = time(end_hour, 0)
        return start_time <= current_time <= end_time
    
    async def should_check_in(self, userid: str) -> bool:
        """检查是否应该执行签到"""
        async with self.lock:
            today = self._get_today_key()
            
            # 初始化今天的记录
            if today not in self.daily_status:
                self.daily_status[today] = {}
            if userid not in self.daily_status[today]:
                self.daily_status[today][userid] = {'checked_in': False, 'checked_out': False}
            
            # 检查是否在签到时段且未签到
            in_checkin_period = self._is_in_time_period(8, 12)
            already_checked_in = self.daily_status[today][userid]['checked_in']
            
            return in_checkin_period and not already_checked_in
    
    async def should_check_out(self, userid: str) -> bool:
        """检查是否应该执行签退"""
        async with self.lock:
            today = self._get_today_key()
            
            # 初始化今天的记录
            if today not in self.daily_status:
                self.daily_status[today] = {}
            if userid not in self.daily_status[today]:
                self.daily_status[today][userid] = {'checked_in': False, 'checked_out': False}
            
            # 检查是否在签退时段且未签退
            in_checkout_period = self._is_in_time_period(18, 20)
            already_checked_out = self.daily_status[today][userid]['checked_out']
            
            return in_checkout_period and not already_checked_out
    
    async def mark_checked_in(self, userid: str):
        """标记为已签到"""
        async with self.lock:
            today = self._get_today_key()
            if today in self.daily_status and userid in self.daily_status[today]:
                self.daily_status[today][userid]['checked_in'] = True
    
    async def mark_checked_out(self, userid: str):
        """标记为已签退"""
        async with self.lock:
            today = self._get_today_key()
            if today in self.daily_status and userid in self.daily_status[today]:
                self.daily_status[today][userid]['checked_out'] = True
    
    def cleanup_old_records(self):
        """清理过期的记录（防止内存泄漏）"""
        today = self._get_today_key()
        keys_to_remove = [key for key in self.daily_status.keys() if key != today]
        for key in keys_to_remove:
            if key in self.daily_status:
                del self.daily_status[key]

#明天继续修改，使之获得想要的数据
class AttendanceRequest(BaseModel):
    userIdList: List[str] 
    workDateFrom: str
    workDateTo: str
    limit: int = 0
    size: int = 50

class recordResult(BaseModel):
    userCheckTime:str
    checkType:str
    userId:str

class AttendanceResponse(BaseModel):
    recordresult: Optional[List[recordResult]] = None  # 签到记录列表
    error_code: Optional[str] = None  # 错误码
    error_msg: Optional[str] = None  # 错误信息

@app.get("/{userid}/attendance",response_model=AttendanceResponse)       
async def process_attendance_for_user(userid:str):
    """为单个用户处理考勤"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")

        now = datetime.datetime.now()
        current_hour = now.hour
        start_time = current_hour  # 08:00-12:00
        end_time = current_hour + 1
        
        # 转换为时间戳
        start_timestamp = datetime_to_timestamp(start_time)
        end_timestamp = datetime_to_timestamp(end_time)
        
        # 获取访问令牌
        access_token = await get_dingtalk_access_token()
        
        # 调用钉钉API
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
                record = data["recordresult"][0]
                '''
                final = {
                "success":response["success"],
                "checkin_time":response["result"]["checkin_time"],
                "detail_place":response["result"]["detail_place"],
                }
                return {
                    "action_taken": True,
                    "checked":True,
                    "result": response
                }
                '''
            else:
                return {
                    "action_taken": True,
                    "checked":False,
                }
            
    except Exception as e:
        print(f"处理用户 {userid} 考勤时出错: {str(e)}")
        return {
            "action_taken": False,
            "error": str(e)
        }

