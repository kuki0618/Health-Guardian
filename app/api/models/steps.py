from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date

class StepInfo(BaseModel):
    step_count: int  # ����
    stat_date:int    #��ʽ��20200907

class UserStepResponse(BaseModel):
    stepinfo_list: Optional[List[StepInfo]] = None

class UserStepRequest(BaseModel):
    object_id: str  # �û�ID
    stat_dates: str  # ���ڣ���ʽΪYYYY-MM-DD
    type: int = 0  # 0��ʾ����

    class Config:
        schema_extra = {
            "example": {
                "object_id": "user123",
                "stat_dates": "20240115",
                "type": 0
            }
        }