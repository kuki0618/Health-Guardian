from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import datetime
from datetime import time, timedelta
import asyncio

app = FastAPI(title="钉钉用户信息API", version="1.0.0")

DINGTALK_APP_KEY = "ding58btzmclcdgd18uu"
DINGTALK_APP_SECRET = "G3CsonOxr853FnDiEd3k0PaJOHBj6qCs-d9ILKsrVApZbyHE2Opp4E-yN-ljgrhT"

class EventAttendee(BaseModel):
    id: str
    displayName: Optional[str] = None
    responseStatus: Optional[str] = None  # accepted, declined, needsAction, tentative

class EventDateTime(BaseModel):
    dateTime: str
    timeZone: Optional[str] = None

class CalendarEvent(BaseModel):
    id: str
    summary: Optional[str] = None
    description: Optional[str] = None
    start: EventDateTime
    end: EventDateTime
    attendees: Optional[List[EventAttendee]] = None
    location: Optional[str] = None
    status: Optional[str] = None  # confirmed, cancelled, tentative
    created: Optional[str] = None
    updated: Optional[str] = None
    organizer: Optional[Dict[str, Any]] = None
    recurrence: Optional[List[str]] = None

class EventsResponse(BaseModel):
    events: List[CalendarEvent]
    nextPageToken: Optional[str] = None
    requestId: str

'''获取凭证信息'''
async def get_dingtalk_access_token() -> str:
    url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
    data = {
        "appKey": DINGTALK_APP_KEY,
        "appSecret": DINGTALK_APP_SECRET
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data)
            response.raise_for_status()
            token_data = response.json()
            return token_data["accessToken"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取访问令牌失败: {str(e)}")

@app.get("/calendar/events", response_model=EventsResponse)
async def get_calendar_events(
    userId: str,
    calendarId: str,
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    max_results: int = 100,
):
    access_token = await get_dingtalk_access_token()
    
    """
    获取日历事件列表的异步函数
    """
    # 构建API URL - 注意这里的path参数 'me'
    api_url = f"/v1.0/calendar/users/{userId}/calendars/{calendarId}"
    headers = {"Content-Type": "application/json"}
    params = {
        "accessToken": access_token,
        "userId": userId,
        "calendarId": calendarId,
        "time_min": time_min,  # 可选
        "time_max": time_max,  # 可选
        "max_results": max_results,  # 可选
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
                error_msg = f"日程列表查询失败: {response.status_code}, {response.text}"
                raise HTTPException(status_code=response.status_code, detail=error_msg)
                
    except httpx.RequestError as e:
        error_msg = f"网络请求错误: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"查询过程发生异常: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
    
async def call_calendar_events(
    userId: str,
    calendarId: str,
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    max_results: int = 100,
):
    result = await get_calendar_events(userId, calendarId, time_min, time_max, max_results)
    result = result.json()
    events = result.get("events", [])
    return len(events) > 0 
