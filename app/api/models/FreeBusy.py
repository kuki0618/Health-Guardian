from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# 请求模型
class FreeBusyRequest(BaseModel):
    userIds: List[str]  # 用户ID列表
    startTime: str  # 开始时间
    endTime: str  # 结束时间

class FreeBusyResponse(BaseModel):
    userId: str
    date: str
    start_datetime: str
    end_datetime: str