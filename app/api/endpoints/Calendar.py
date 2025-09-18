from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from services.dingtalk.calendar_service import CalendarService
from models.Calendar import CalendarEventsResponse, CalendarRequest, CalendarEvent

router = APIRouter(prefix="/calendar", tags=["calendar"])

# 依赖项函数
def get_calendar_service():
    return CalendarService()

@router.get("/{user_id}/{calendar_id}/events", response_model=CalendarEventsResponse)
async def get_calendar_events(
    user_id: str,
    calendar_id: str,
    time_min: Optional[str] = Query(None, description="beginning time"),
    time_max: Optional[str] = Query(None, description="end time"),
    max_results: Optional[int] = Query(100, description="max results"),
    calendar_service: CalendarService = Depends(get_calendar_service)
):

    #获取日历事件
    #- 查询指定用户的日历事件
    
    try:
        request = CalendarRequest(
            user_id=user_id,
            calendar_id=calendar_id,
            time_min=time_min,
            time_max=time_max,
            max_results=max_results
        )
        
        result = await calendar_service.get_calendar_events(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Calendar API query failed: {str(e)}"
        )

@router.get("/{user_id}/availability", response_model=bool)
async def check_user_availability(
    user_id: str,
    duration_minutes: int = Query(60, description="check duration (minutes)"),
    calendar_service: CalendarService = Depends(get_calendar_service)
):
    #检查用户是否有空
    try:
        is_available = await calendar_service.check_user_availability(user_id, duration_minutes)
        return is_available
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Check user availability failed: {str(e)}"
        )