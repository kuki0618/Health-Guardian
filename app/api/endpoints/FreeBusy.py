#coding=utf-8
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Optional

from repository import database
from services.dingtalk.FreeBusy_service import FreeBusyService
from api.models.FreeBusy import FreeBusyResponse,FreeBusyRequest

router = APIRouter(prefix="/schedule", tags=["schedule"])

# 依赖项函数
def get_schedule_service():
    return FreeBusyService()

@router.get("/{userId}/now/free_busy",response_model=List[FreeBusyResponse])
async def get_user_free_busy_status(
    userId:str,
    schedule_service: FreeBusyService = Depends(get_schedule_service)
):
    #获取用户忙闲状态
    #查询最近2小时的日程信息
    try:
        result = await schedule_service.get_user_free_busy_now_status(userId)
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
    schedule_service: FreeBusyService = Depends(get_schedule_service)
):
    
    #获取用户某一段时间的忙闲状态
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
    
@router.get("/test-add-records")
async def test_add_attendance_records(
    Freebusy_service: FreeBusyService = Depends(get_schedule_service),
    conn = Depends(database.get_db)
):
    mock_records =[
        {"userId":"6kPiPK8K1yV8lDlRc50TKFwiEiE",
         "date":"2025-09-20",
         "start_datetime":"2025-09-20T08:30:00+08:00",
         "end_datetime":"2025-09-20T09:30:00+08:00"}
         ]
  
    #测试添加考勤记录到数据库
    try:
        # 调用服务层的方法
        await Freebusy_service.insert_freebusy_record(mock_records, conn)
        return {
            "message": "freebusy records add successed",
            "count": len(mock_records),
            "records": mock_records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"attendance records add failed: {str(e)}")