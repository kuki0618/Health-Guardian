from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ����ģ��
class FreeBusyRequest(BaseModel):
    userIds: List[str]  # �û�ID�б�
    startTime: str  # ��ʼʱ��
    endTime: str  # ����ʱ��

class FreeBusyResponse(BaseModel):
    userId: Optional[str] = None
    date: Optional[str] = None
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None
