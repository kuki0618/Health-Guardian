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
        #��ȡ�����¼� - ����㷽��
        try:
            access_token = await get_dingtalk_access_token()
            
            # ����API URL
            api_url = f"https://api.dingtalk.com/v1.0/calendar/users/{request.userId}/calendars/{request.calendarId}/events"
            headers = {
                "Content-Type": "application/json",
                "x-acs-dingtalk-access-token": access_token
            }
            
            # ������ѯ����
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
                
                # ת��Ϊ��Ӧģ��
                return CalendarEventsResponse(**response_data)
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP request failed: {e}")
            raise Exception(f"Calendar API query failed: {e}")
        except Exception as e:
            logger.error(f"Calendar API query failed: {str(e)}")
            raise
    
    async def check_user_availability(self, userId: str, duration_minutes: int = 60) -> bool:
        #����û��Ƿ��п�
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
                
            # ����Ƿ���æµ���¼�
            for event in result.events:
                if event.status != "cancelled":  # ������ȡ�����¼�
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Check user availability failed: {str(e)}")
            return False