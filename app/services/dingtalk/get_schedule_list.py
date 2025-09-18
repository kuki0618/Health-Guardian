from datetime import datetime
from api.endpoints.schedule_list import get_calendar_events
from fastapi import  HTTPException,APIRouter
from typing import Optional
import httpx
from datetime import datetime
from dependencies.dingtalk_token import get_dingtalk_access_token
from api.models.Calendar import CalenderRequest

router = APIRouter(prefix="/calendar",tags=["calendar"])


@router.get("/{userId}/{calendarId}")
async def get_calendar_events(
    calneder_request:CalenderRequest,
    calendar_service
):
    access_token = await get_dingtalk_access_token()
    
    # 构建API URL - 注意这里的spath参数 'me'
    api_url = f"https://api.dingtalk.com/v1.0/calendar/users/{userId}/calendars/{calendarId}/events"
    headers = {
        "Content-Type": "application/json",
        "x-acs-dingtalk-access-token": access_token}
    params = {
        "timeMin": time_min,
        "timeMax": time_max,  # 可选
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                api_url,
                params=params,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                error_msg = f"schedule list query fail: {response.status_code}, {response.text}"
                raise HTTPException(status_code=response.status_code, detail=error_msg)
                
    except httpx.RequestError as e:
        error_msg = f"schedule list query internet request fail: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"schedule list query process fail: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)

async def call_calendar_events(userId:str):
    now = datetime.datetime.now()
    time_min = now.isoformat() + "Z"  # 当前时间
    time_max = (now + datetime.timedelta(minutes=60)).isoformat() + "Z"  
    result = await get_calendar_events(userId,"primary",time_min, time_max)
    events = result.get("events", [])
    return len(events) > 0 
