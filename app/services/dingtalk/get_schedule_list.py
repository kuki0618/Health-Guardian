from core.config import HTTPException,FastAPI,BaseModel,Optional,Dict,List,Any,get_dingtalk_access_token,httpx

app = FastAPI(title="钉钉用户信息API", version="1.0.0")
'''
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
'''
@app.get("/calendar/events")
async def get_calendar_events(
    userId: str,
    calendarId: str,
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
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
