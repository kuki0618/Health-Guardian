from fastapi import APIRouter
from pydantic import BaseModel
import asyncio
from typing import Optional, List, Dict, Any
import httpx
from datetime import datetime,time

from dependencies.dingtalk_token_old import get_dingtalk_access_token

router = APIRouter(prefix="/attendance", tags=["attendance"])

def reschedule_data(data:dict):
    flat_data_list = []
    for item in data['recordresult']:
        userCheckTime = timestamp_to_datetime(item['userCheckTime'])
        flat_data = {
            # 第一层数据
            'userid': item["userId"],
            'date':userCheckTime.strftime("%Y-%m-%d"),
            "datetime":userCheckTime.strftime("%Y-%m-%d %H:%M:%S"),
            'checkType':item['checkType'],
        }  
        flat_data_list.append(flat_data)
    return flat_data_list

def datetime_to_timestamp(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)

def timestamp_to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp / 1000)

class AttendanceManager:
    def __init__(self):
        # 使用字典存储每天的签到状态 {date: {userid: {'checked_in': bool, 'checked_out': bool}}}
        self.daily_status: Dict[str, Dict[str, Dict[str, bool]]] = {}
        self.lock = asyncio.Lock()
    
    def _get_today_key(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")
    
    def _is_in_time_period(self, start_hour: int, end_hour: int) -> bool:
        now = datetime.now()
        current_time = now.time()
        start_time = time(start_hour, 0)
        end_time = time(end_hour, 0)
        return start_time <= current_time <= end_time
    
    async def should_check_in(self, userid: str) -> bool:
        async with self.lock:
            today = self._get_today_key()
            
            # 初始化今天的记录
            if today not in self.daily_status:
                self.daily_status[today] = {}
            if userid not in self.daily_status[today]:
                self.daily_status[today][userid] = {'checked_in': False, 'checked_out': False}
            
            # 检查是否在签到时段且未签到
            in_checkin_period = self._is_in_time_period(8, 12)
            
            return in_checkin_period 
    
    async def should_check_out(self, userid: str) -> bool:
        async with self.lock:
            today = self._get_today_key()
            
            # 初始化今天的记录
            if today not in self.daily_status:
                self.daily_status[today] = {}
            if userid not in self.daily_status[today]:
                self.daily_status[today][userid] = {'checked_in': False, 'checked_out': False}
            
            # 检查是否在签退时段且未签退
            in_checkout_period = self._is_in_time_period(18, 20) 
            
            return in_checkout_period 
    
    async def mark_checked_in(self, userid: str):
        async with self.lock:
            today = self._get_today_key()
            if today in self.daily_status and userid in self.daily_status[today]:
                self.daily_status[today][userid]['checked_in'] = True
    
    async def mark_checked_out(self, userid: str):
        async with self.lock:
            today = self._get_today_key()
            if today in self.daily_status and userid in self.daily_status[today]:
                self.daily_status[today][userid]['checked_out'] = True
    
    def cleanup_old_records(self):
        today = self._get_today_key()
        keys_to_remove = [key for key in self.daily_status.keys() if key != today]
        for key in keys_to_remove:
            if key in self.daily_status:
                del self.daily_status[key]

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
    action_taken: bool = False
    checked:bool = False
    recordresult: Optional[List[recordResult]] = None  # 签到记录列表
    errorcode: Optional[str] = None  # 错误码
    errormsg: Optional[str] = None  # 错误信息
    error: Optional[str] = None  # 错误信息

@router.get("/{userid}/details", response_model=AttendanceResponse)
async def process_attendance_for_user(userid:str,start_time:datetime,end_time:datetime):
    try:
        
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
            if "recordresult" in response:
                response = reschedule_data(response)
                return {
                    "action_taken": True,
                    "checked":True,
                    "recordresult": response
                }
            else:
                return {
                    "action_taken": True,
                    "checked":False,
                    "errormsg":response["errmsg"]
                }
            
    except Exception as e:
        print(f" {userid} error: {str(e)}")
        return {
            "action_taken": False,
            "error": str(e)
        }

