import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from api.dependencies.dingtalk_token import get_dingtalk_access_token
from api.models.FreeBusy import FreeBusyRequest, FreeBusyResponse

logger = logging.getLogger(__name__)

class ScheduleService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    def reschedule_data(self,data:dict):
        flat_data_list = []
        for schedule_info in data['scheduleInformation']:
            user_id = schedule_info['userId']
            for item in schedule_info['scheduleItems']:
                # 创建扁平化的字典
                flat_data = {
                    # 第一层数据
                    'user_id': user_id,
                    "date":item['start']['date'],
                    'start_datetime': item['start']['dateTime'],
                    'end_datetime': item['end']['dateTime']
                }
                
                flat_data_list.append(flat_data)
        return flat_data_list
    
    async def get_user_free_busy_status(self,request:FreeBusyRequest)-> FreeBusyResponse:

            access_token = await get_dingtalk_access_token()

            
            # 构建请求数据
            data = request.dict()

            
            url = f"https://api.dingtalk.com/v1.0/calendar/users/{request.userIds[0]}/querySchedule"
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
            
                        result = response.json()
                    
                        if len(result["scheduleInformation"])!=0:
                            result = self.reschedule_data(result)
                            return result
                        else: 
                            return []
                        
                    else:
                        error_msg = f"status quary fail: {response.status_code}, {response.text}"
                        raise Exception(error_msg)

            except httpx.RequestError as e:
                logger.error(f"internet quary fail: {str(e)}")
                raise Exception(f"internet quary fail: {str(e)}") from e
            except Exception as e:
               logger.error(f"quary process fail: {str(e)}")
               raise Exception(f"quary process fail: {str(e)}") from e
