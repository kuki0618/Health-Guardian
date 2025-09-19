#coding=utf-8
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Optional

from services.dingtalk.FreeBusy_service import ScheduleService
from api.models.FreeBusy import FreeBusyResponse,FreeBusyRequest

router = APIRouter(prefix="/schedule", tags=["schedule"])

# �������
def get_schedule_service():
    return ScheduleService()

@router.get("/{userId}/now/free_busy",response_model=List[FreeBusyResponse])
async def get_user_free_busy_status(
    userId:str,
    schedule_service: ScheduleService = Depends(get_schedule_service)
):
    
    #��ȡ�û�æ��״̬
    #��ѯ���2Сʱ���ճ���Ϣ
  
    try:
        # ���ò�ѯʱ�䷶Χ����ǰʱ�䵽2Сʱǰ��
        time_max = datetime.now()
        time_min = time_max - timedelta(hours=2)
        
        # ��ʽ��ʱ���ַ�����ISO 8601��ʽ��
        startTime = time_min.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
        endTime = time_max.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

        request = FreeBusyRequest(
            userIds=[userId],
            startTime=startTime,
            endTime=endTime
        )
        result = await schedule_service.get_user_free_busy_status(request)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"quary user free busy status fail: {str(e)}"
        )

@router.get("/{userId}/free_busy",response_model=List[FreeBusyResponse])
async def get_user_free_busy_status(
    userId:str,
    startTime:str,
    endTime:str,
    schedule_service: ScheduleService = Depends(get_schedule_service)
):
    
    #��ȡ�û�æ��״̬
    #��ѯ���2Сʱ���ճ���Ϣ
  
    try:
        request = FreeBusyRequest(
            userIds=[userId],
            startTime=startTime,
            endTime=endTime
        )
        result = await schedule_service.get_user_free_busy_status(request)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"quary user free busy status fail: {str(e)}"
        )