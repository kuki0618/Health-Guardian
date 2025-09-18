from pydantic import BaseModel
from typing import Optional

class CalenderRequest(BaseModel):
    userId:str
    calendarId:str
    time_min: Optional[str] = None
    time_max: Optional[str] = None
