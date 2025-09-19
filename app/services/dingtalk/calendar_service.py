from datetime import datetime
import httpx
import logging
from datetime import datetime,timedelta
from api.dependencies.dingtalk_token import get_dingtalk_access_token
from api.models.Calendar import CalendarRequest,CalendarEventsResponse

logger = logging.getLogger(__name__)

class CalendarService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_calendar_events(self, request: CalendarRequest) -> CalendarEventsResponse:
        #获取日历事件 - 服务层方法
        try:
            access_token = await get_dingtalk_access_token()
            
            # 构建API URL
            api_url = f"https://api.dingtalk.com/v1.0/calendar/users/{request.userId}/calendars/{request.calendarId}/events"
            headers = {
                "Content-Type": "application/json",
                "x-acs-dingtalk-access-token": access_token
            }
            
            # 构建查询参数
            params = {}
            if request.timeMin:
                params["timeMin"] = request.timeMin
            if request.timeMax:
                params["timeMax"] = request.timeMax
            if request.maxResults:
                params["maxResults"] = request.maxResults
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    api_url,
                    params=params,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                response_data = response.json()
                logger.debug(f"API response: {response_data}")
                
                # 转换为响应模型
                return CalendarEventsResponse(**response_data)
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP request failed: {e}")
            raise Exception(f"Calendar API query failed: {e}")
        except Exception as e:
            logger.error(f"Calendar API query failed: {str(e)}")
            raise
    
    async def check_user_availability(self, userId: str, duration_minutes: int = 60) -> bool:
        #检查用户是否有空
        try:
            now = datetime.now()
            timeMin = now.isoformat() + "Z"
            timeMax = (now + timedelta(minutes=duration_minutes)).isoformat() + "Z"
            
            request = CalendarRequest(
                userId=userId,
                calendarId="primary",
                timeMin=timeMin,
                timeMax=timeMax
            )
            
            result = await self.get_calendar_events(request)

            if not result.events:
                return True
                
            # 检查是否有忙碌的事件
            for event in result.events:
                if event.status != "cancelled":  # 忽略已取消的事件
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Check user availability failed: {str(e)}")
            return False