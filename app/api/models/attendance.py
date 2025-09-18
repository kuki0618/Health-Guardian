# app/models/attendance.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional

class AttendanceRecord(BaseModel):
    userid: str
    date: str
    datetime: str
    checkType: str

class AttendanceResponse(BaseModel):
    action_taken: bool
    checked: Optional[bool] = None
    recordresult: Optional[List[AttendanceRecord]] = None
    errormsg: Optional[str] = None
    errorcode: Optional[int] = None
    error: Optional[str] = None
    '''
    {"action_taken":true,"checked":true,
    "recordresult":[
    {"userid":"manager4585","date":"2025-09-10","datetime":"2025-09-10 08:00:00","checkType":"OnDuty"},
    {"userid":"manager4585","date":"2025-09-10","datetime":"2025-09-10 16:38:43","checkType":"OffDuty"},
    {"userid":"manager4585","date":"2025-09-11","datetime":"2025-09-11 18:00:00","checkType":"OffDuty"},
    {"userid":"manager4585","date":"2025-09-11","datetime":"2025-09-11 08:00:00","checkType":"OnDuty"}
    ],
    "errormsg":null,"errorcode":null,"error":null}
    '''
    
class AttendanceRequest(BaseModel):
    userIdList: List[str]
    workDateFrom: str
    workDateTo: str
    offset: int = 0
    limit: int = 50

    class Config:
        schema_extra = {
            "example": {
                "userIdList": ["manager4585"],
                "workDateFrom": "2025-09-15 00:00:00 ",
                "workDateTo": "2025-09-15 23:59:59 ",
                "offset":0,
                "limit":50
            }
        }
