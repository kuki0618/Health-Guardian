from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Optional
from datetime import date

from services.dingtalk.steps_service import SportService
from api.models.steps import UserStepResponse, UserStepRequest

router = APIRouter(prefix="/sport_info", tags=["sport_info"])

# �������
def get_sport_service():
    return SportService()

@router.get("/{object_id}/{stat_date}", response_model=UserStepResponse)
async def get_user_steps(
    object_id: str,
    stat_date: str,
    type: int = Query(0),
    sport_service: SportService = Depends(get_sport_service)
):

    #��ȡ�û�������Ϣ
    #- ��ѯָ�����ڵ��û��˶�����
    try:
        request = UserStepRequest(
            object_id=object_id,
            stat_dates=stat_date,
            type=type
        )
        result = await sport_service.get_user_steps(request)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"steps quary fail: {str(e)}"
        )