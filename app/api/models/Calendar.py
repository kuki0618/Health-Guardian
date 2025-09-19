from pydantic import BaseModel
from typing import Optional,List

class CalendarEventsResponse(BaseModel):
    events: Optional[List[dict]] = None
    
class CalendarRequest(BaseModel):
    unionid:str
    calendarId:str
    timeMin: Optional[str] = None
    timeMax: Optional[str] = None
    maxResults: Optional[int] = 100
