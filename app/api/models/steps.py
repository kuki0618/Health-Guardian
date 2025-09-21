from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import date

class StepInfo(BaseModel):
    step_count: int  # 步数
    stat_date:int    #格式：20200907

class UserStepResponse(BaseModel):
    stepinfo_list: Optional[List[StepInfo]] = None
    model_config = ConfigDict(
        json_schema_extra = {
        "example":
        {"stepinfo_list":
            [{"step_count":10100,"stat_date":20250916},
            {"step_count":2451,"stat_date":20250917}]
        }
    }
    )

class UserStepRequest(BaseModel):
    object_id: str  # 用户ID
    stat_dates: str  # 日期，格式为YYYY-MM-DD
    type: int = 0  # 0表示步数

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "object_id": "user123",
                "stat_dates": "20240115",
                "type": 0
            }
        }
    )