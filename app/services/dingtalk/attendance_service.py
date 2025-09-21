# app/services/attendance_service.py
from fastapi import Depends
import asyncio
from typing import Dict, List
from datetime import datetime, time
import httpx
import logging
import pymysql.cursors

from api.dependencies.dingtalk_token import get_dingtalk_access_token
from api.models.attendance import AttendanceResponse, AttendanceRecord,AttendanceRequest

logger = logging.getLogger(__name__)

def datetime_to_timestamp(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)

def timestamp_to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp / 1000)

def reschedule_data(data: dict) -> List[AttendanceRecord]:
    flat_data_list = []
    for item in data['recordresult']:
        userCheckTime = timestamp_to_datetime(item['userCheckTime'])
        flat_data = AttendanceRecord(
            userid=item["userId"],
            date=userCheckTime.strftime("%Y-%m-%d"),
            datetime=userCheckTime.strftime("%Y-%m-%d %H:%M:%S"),
            checkType=item['checkType'],
        )
        flat_data_list.append(flat_data)
    return flat_data_list

class AttendanceManager:
    def __init__(self):
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
    
    async def get_attendance_status(self, userid: str) -> Dict[str, bool]:
        """获取用户今天的考勤状态"""
        async with self.lock:
            today = self._get_today_key()
            
            if today not in self.daily_status:
                self.daily_status[today] = {}
            if userid not in self.daily_status[today]:
                self.daily_status[today][userid] = {'checked_in': False, 'checked_out': False}
            
            return self.daily_status[today][userid].copy()
         
    async def is_in_checkin_period(self) -> bool:
        """判断是否应该调用签到api请求"""
        async with self.lock:
            
            in_checkin_period = self._is_in_time_period(8,22)

            return in_checkin_period
    
    async def is_in_checkout_period(self) -> bool:
        """判断是否应该调用签退api请求"""
        async with self.lock:
            
            in_checkout_period = self._is_in_time_period(18,22)

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

class AttendanceService:
    def __init__(self, attendance_manager: AttendanceManager):
        self.attendance_manager = attendance_manager
    
    async def process_attendance_for_user(self, request: AttendanceRequest) -> AttendanceResponse:
        #服务层：处理考勤逻辑
        try:
            
            # 获取访问令牌
            access_token = await get_dingtalk_access_token()
            #logger.info(f"获取访问令牌: {access_token}")
            
            # 调用钉钉API
            url = "https://oapi.dingtalk.com/attendance/list"
            params = {"access_token": access_token}
            headers = {"Content-Type": "application/json"}
            data = request.dict()
            async with httpx.AsyncClient() as client:
                response = await client.post(url, params=params, headers=headers, json=data)
                response.raise_for_status()
                response_data = response.json()
                
                if "recordresult" in response_data:
                    records = reschedule_data(response_data)
                    return AttendanceResponse(
                        action_taken=True,
                        checked=True,
                        recordresult=records
                    )
                else:
                    return AttendanceResponse(
                        action_taken=True,
                        checked=False,
                        errormsg=response_data.get("errmsg"),
                        errorcode=response_data.get("errcode", 0)
                    )
                    
        except Exception as e:
            logger.error(f"error: {str(e)}")
            return AttendanceResponse(
                action_taken=False,
                error=str(e)
            )
        
    async def check_attendance_for_user(self, userid:str) -> AttendanceResponse:
        #服务层：处理考勤逻辑
        try:
            now = datetime.now()
            hour_start = now.replace(minute=0, second=0, microsecond=0)

            end_time= now.strftime("%Y-%m-%d %H:%M:%S")
            start_time = hour_start.strftime("%Y-%m-%d %H:%M:%S")

            # 获取访问令牌
            access_token = await get_dingtalk_access_token()
            #logger.info(f"获取访问令牌: {access_token}")
            request = AttendanceRequest(
                userIdList=[userid],
                workDateFrom=start_time,
                workDateTo=end_time,
                offset=0,
                limit=50
            )
            # 调用钉钉API
            url = "https://oapi.dingtalk.com/attendance/list"
            params = {"access_token": access_token}
            headers = {"Content-Type": "application/json"}
            data = request.dict()
            async with httpx.AsyncClient() as client:
                response = await client.post(url, params=params, headers=headers, json=data)
                response.raise_for_status()
                response_data = response.json()

                if response_data.get("recordresult") != []:
                    records = reschedule_data(response_data)
                    return AttendanceResponse(
                        action_taken=True,
                        checked=True,
                        recordresult=records
                    )
                else:
                    return AttendanceResponse(
                        action_taken=True,
                        checked=False,
                        errormsg=response_data.get("errmsg"),
                        errorcode=response_data.get("errcode", 0)
                    )
                    
        except Exception as e:
            logger.error(f"error: {str(e)}")
            return AttendanceResponse(
                action_taken=False,
                error=str(e)
            )
    

    async def add_attendance_info(
        self,
        all_data:List[AttendanceRecord],
        conn
        ):
        cursor = None
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            for data in all_data:
                user_id = data.userid
                date = data.date
                select_query = """
                SELECT id FROM online_status WHERE userid = %s AND date = %s
                """
                cursor.execute(select_query, (user_id, date))
                existing_record = cursor.fetchone()

                if existing_record:
                    # 记录已存在，使用现有ID
                    main_id = existing_record['id']
                else:   
                    # 第一步：插入主表 online_status，获取attendance_id
                    insert_main_query = f"""
                    INSERT INTO online_status (userid, date) 
                    VALUES (%s, %s)
                    """
                    cursor.execute(insert_main_query, (user_id, date))
                    
                    # 获取刚插入的主键ID
                    main_id = cursor.lastrowid

                time = data.datetime
                checkType = data.checkType
                # 第二步：插入子表 online_time_periods
                insert_period_query = f"""
                INSERT INTO attendance_data (task_id,userCheckTime,checkType) 
                VALUES (%s, %s, %s)
                """
                cursor.execute(insert_period_query, (main_id, time, checkType))
                
            logger.info(f"添加考勤信息: {all_data}")
                # 提交事务
            conn.commit()
        except Exception as e:
        # 发生错误时回滚
            conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
