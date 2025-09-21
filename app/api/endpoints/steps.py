from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Optional
from datetime import date

from repository import database
from services.dingtalk.steps_service import SportService
from api.models.steps import UserStepResponse, UserStepRequest,StepInfo

router = APIRouter(prefix="/sport_info", tags=["sport_info"])

def get_sport_service():
    return SportService()

@router.get("/{object_id}/{stat_dates}", response_model=UserStepResponse)
async def get_user_steps(
    object_id: str,
    stat_dates: str,
    type: int = Query(0),
    sport_service: SportService = Depends(get_sport_service)
):
    # 获取用户步数信息
    # - 查询指定日期的用户运动步数
    try:
        request = UserStepRequest(
            object_id=object_id,
            stat_dates=stat_dates,
            type=type
        )
        result = await sport_service.get_user_steps(request)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"steps quary fail: {str(e)}"
        )


@router.get("/test-add-records")
async def insert_user_steps(
    sport_service: SportService = Depends(get_sport_service),
    conn = Depends(database.get_db)
):
    # 插入用户步数信息
    userid = "manager4585"
    mock_records = UserStepResponse(
        stepinfo_list=[
            StepInfo(step_count=10100, stat_date=20250916),
            StepInfo(step_count=2451, stat_date=20250917)
        ]
    )
    try:
       
        await sport_service.insert_steps_record(userid,mock_records,conn)
        return {
            "message": "attendance records add successed",
            "records": mock_records
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"steps insert fail: {str(e)}"
        )

