from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date

class StepInfo(BaseModel):
    step_count: int  # ����

class UserStepResponse(BaseModel):
    stepinfo_list: List[StepInfo]

class UserStepRequest(BaseModel):
    object_id: str  # �û�ID
    stat_date: str  # ���ڣ���ʽΪYYYY-MM-DD
    type: int = 0  # 0��ʾ������1��ʾ����

    class Config:
        schema_extra = {
            "example": {
                "object_id": "user123",
                "stat_dates": "2024-01-15",
                "type": 0
            }
        }