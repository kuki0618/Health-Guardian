import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dependencies.dingtalk_token import get_dingtalk_access_token
from app.models.schedule import ScheduleResponse, FlatScheduleItem, FreeBusyRequest

logger = logging.getLogger(__name__)

class ScheduleService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        async def get_user_free_busy_status(userid:str):

            access_token = await get_dingtalk_access_token()

            # 设置查询时间范围（当前时间到2小时前）
            time_max = datetime.now()
            time_min = time_max - timedelta(hours=2)
            
            # 格式化时间字符串（ISO 8601格式）
            time_min_iso = time_min.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
            time_max_iso = time_max.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
            
            # 构建请求数据
            data = {
                "userIds": [userid],
                "startTime": time_min_iso,
                "endTime": time_max_iso
            }
            
            url = f"https://api.dingtalk.com/v1.0/calendar/users/{userid}/querySchedule"
            headers = {
                "Content-Type": "application/json",
                "x-acs-dingtalk-access-token": access_token  # 关键修改：使用正确的头部
            }
            try:
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url, headers=headers,json=data)
                    #这里逻辑修改
                    if response.status_code == 200:
                        '''
                        result = response.json()
                        if len(result["scheduleInformation"])!=0:
                            result = reschedule_data(result)
                            return result
                        else: 
                            return []
                        '''
                        return response.json()
                    else:
                        error_msg = f"status quary fail: {response.status_code}, {response.text}"
                        raise HTTPException(status_code=response.status_code, detail=error_msg)
            except httpx.RequestError as e:
                logger.error(f"internet quary fail: {str(e)}")
                raise
            except Exception as e:
               logger.error(f"quary process fail: {str(e)}")
            raise
