from pydantic import BaseModel
from typing import Optional,List

class CalendarEventsResponse(BaseModel):
    events: Optional[List[dict]] = None
    
class CalenderRequest(BaseModel):
    userId:str
    calendarId:str
    timeMin: Optional[str] = None
    timeMax: Optional[str] = None
