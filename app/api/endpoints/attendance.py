# app/api/endpoints/attendance.py
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List

from core import database
from services.dingtalk.attendance_service import AttendanceService, AttendanceManager
from api.models.attendance import AttendanceResponse,AttendanceRequest

router = APIRouter(prefix="/attendance", tags=["attendance"])

# 依赖项函数
def get_attendance_manager():
    return AttendanceManager()

def get_attendance_service(attendance_manager: AttendanceManager = Depends(get_attendance_manager)):
    return AttendanceService(attendance_manager)

@router.get("/{userid}/details", response_model=AttendanceResponse)
async def get_attendance_details(
    userid: str,
    start_time: str,
    end_time: str,
    attendance_service: AttendanceService = Depends(get_attendance_service)
):

 #   端点层：获取用户考勤详情
 #  - 只处理HTTP相关逻辑
 # - 调用服务层处理业务逻辑

    try:
        request =AttendanceRequest(
            userIdList = [userid],
            workDateFrom = start_time,
            workDateTo = end_time)
        result = await attendance_service.process_attendance_for_user(request)
        
        if not result.action_taken:
            raise HTTPException(status_code=500, detail=result.error)
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error: {str(e)}")

@router.get("/{userid}/should-check-in")
async def should_check_in(
    userid: str,
    attendance_service: AttendanceService = Depends(get_attendance_service)
):
    #检查用户是否应该签到
    should_check = await attendance_service.attendance_manager.should_check_in(userid)
    return {"userid": userid, "should_check_in": should_check}

@router.get("/{userid}/should-check-out")
async def should_check_out(
    userid: str,
    attendance_service: AttendanceService = Depends(get_attendance_service)
):
    #检查用户是否应该签退
    should_check = await attendance_service.attendance_manager.should_check_out(userid)
    return {"userid": userid, "should_check_out": should_check}

@router.get("/test-add-records")
async def test_add_attendance_records(
    attendance_service: AttendanceService = Depends(get_attendance_service),
    conn = Depends(database.get_db)
):
    mock_records ={"recordresult":[
    {"userid":"manager4585","date":"2025-09-10","datetime":"2025-09-10 08:00:00","checkType":"OnDuty"},
    {"userid":"manager4585","date":"2025-09-10","datetime":"2025-09-10 16:38:43","checkType":"OffDuty"},
    {"userid":"manager4585","date":"2025-09-11","datetime":"2025-09-11 18:00:00","checkType":"OffDuty"},
    {"userid":"manager4585","date":"2025-09-11","datetime":"2025-09-11 08:00:00","checkType":"OnDuty"}
    ],}
  
    #测试添加考勤记录到数据库
    try:
        # 调用服务层的方法
        await attendance_service.add_attendence_info(mock_records, conn)
        return {
            "message": "attendance records add successed",
            "count": len(mock_records['recordresult']),
            "records": mock_records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"attendance records add failed: {str(e)}")