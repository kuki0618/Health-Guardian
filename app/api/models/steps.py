from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date

class StepInfo(BaseModel):
    step_count: int  # 步数

class UserStepResponse(BaseModel):
    stepinfo_list: List[StepInfo]

class UserStepRequest(BaseModel):
    object_id: str  # 用户ID
    stat_date: str  # 日期，格式为YYYY-MM-DD
    type: int = 0  # 0表示步数，1表示距离

    class Config:
        schema_extra = {
            "example": {
                "object_id": "user123",
                "stat_dates": "2024-01-15",
                "type": 0
            }
        }