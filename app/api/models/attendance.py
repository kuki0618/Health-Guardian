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

class AttendanceRequest(BaseModel):
    user_id_list: List[str]
    work_date_from: str
    work_date_to: str
    offset: int = 0
    limit: int = 50