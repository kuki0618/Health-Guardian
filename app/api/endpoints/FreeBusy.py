from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Optional

from app.services.schedule_service import ScheduleService
from app.models.schedule import FlatScheduleItem

router = APIRouter(prefix="/schedule", tags=["schedule"])

# �������
def get_schedule_service():
    return ScheduleService()

@router.get("/{userid}/free-busy", response_model=List[FlatScheduleItem])
async def get_user_free_busy_status(
    userid: str,
    schedule_service: ScheduleService = Depends(get_schedule_service)
):
    
    #��ȡ�û�æ��״̬
    #��ѯ���2Сʱ���ճ���Ϣ
  
    try:
        result = await schedule_service.get_user_free_busy_status(userid)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"quary user free busy status fail: {str(e)}"
        )