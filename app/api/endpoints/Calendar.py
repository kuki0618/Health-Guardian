from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from services.dingtalk.calendar_service import CalendarService
from api.models.Calendar import CalendarEventsResponse, CalendarRequest

router = APIRouter(prefix="/calendar", tags=["calendar"])

# 依赖项函数
def get_calendar_service():
    return CalendarService()

@router.get("/{userId}/{calendarId}/events", response_model=CalendarEventsResponse)
async def get_calendar_events(
    userId: str,
    calendarId: str,
    timeMin: Optional[str] = Query(None, description="beginning time"),
    timeMax: Optional[str] = Query(None, description="end time"),
    maxResults: Optional[int] = Query(100, description="max results"),
    calendar_service: CalendarService =Depends(get_calendar_service)
):

    #获取日历事件
    #- 查询指定用户的日历事件
    
    try:
        request = CalendarRequest(
            userId=userId,
            calendarId=calendarId,
            timeMin=timeMin,
            timeMax=timeMax,
            maxResults=maxResults
        )
        
        result = await calendar_service.get_calendar_events(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Calendar API query failed: {str(e)}"
        )

@router.get("/{userId}/availability", response_model=bool)
async def check_user_availability(
    userId: str,
    duration_minutes: int = Query(60, description="check duration (minutes)"),
    calendar_service: CalendarService = Depends(get_calendar_service)
):
    #检查用户是否有空
    try:
        is_available = await calendar_service.check_user_availability(userId, duration_minutes)
        return is_available
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Check user availability failed: {str(e)}"
        )