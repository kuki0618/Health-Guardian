from fastapi import HTTPException,APIRouter
from pydantic import BaseModel
import asyncio
from typing import List
import httpx
from datetime import datetime,timedelta
from dependencies.dingtalk_token import get_dingtalk_access_token


router = APIRouter(prefix="/ifFree", tags=["ifFree"])

userids ={}
def reschedule_data(data:dict):
    flat_data_list = []
    for schedule_info in data['scheduleInformation']:
        user_id = schedule_info['userId']
        for item in schedule_info['scheduleItems']:
            # ������ƽ�����ֵ�
            flat_data = {
                # ��һ������
                'user_id': user_id,
                "date":item['start']['date'],
                'start_datetime': item['start']['dateTime'],
                'end_datetime': item['end']['dateTime']
            }
            
            flat_data_list.append(flat_data)
    return flat_data_list
# ����ģ��
class FreeBusyRequest(BaseModel):
    userIds: List[str]  # �û�ID�б�
    startTime: str  # ��ʼʱ��
    endTime: str  # ����ʱ��

class Start(BaseModel):
    date:str
    dateTime:str

class End(BaseModel):
    date:str
    dateTime:str

class FreeBusyItem(BaseModel):
    status: str  # �û�ID
    start: Start  # æ��״̬��free-�У�busy-æ
    end:End

class scheduleInformation(BaseModel):
    userId: str  
    error:str
    scheduleItems: List[FreeBusyItem]  # æ��״̬�б�

@router.get("/{userid}")
async def get_user_free_busy_status(userid:str):
   
    access_token = await get_dingtalk_access_token()

    # ���ò�ѯʱ�䷶Χ����ǰʱ�䵽2Сʱǰ��
    time_max = datetime.now()
    time_min = time_max - timedelta(hours=2)
    
    # ��ʽ��ʱ���ַ�����ISO 8601��ʽ��
    time_min_iso = time_min.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
    time_max_iso = time_max.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
    
    # ������������
    data = {
        "userIds": [userid],
        "startTime": time_min_iso,
        "endTime": time_max_iso
    }
    
    url = f"https://api.dingtalk.com/v1.0/calendar/users/{userid}/querySchedule"
    headers = {
        "Content-Type": "application/json",
        "x-acs-dingtalk-access-token": access_token  # �ؼ��޸ģ�ʹ����ȷ��ͷ��
    }
    try:
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, headers=headers,json=data)
            
            if response.status_code == 200:
                result = response.json()
                if len(result["scheduleInformation"])!=0:
                    result = reschedule_data(result)
                    return result
                else: 
                    return []
            else:
                error_msg = f"status quary fail: {response.status_code}, {response.text}"
                raise HTTPException(status_code=response.status_code, detail=error_msg)
                
    except httpx.RequestError as e:
        error_msg = f"internet quary fail: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"quary process fail: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


