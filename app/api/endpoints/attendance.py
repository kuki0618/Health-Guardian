# app/api/endpoints/attendance.py
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List

from app.services.attendance_service import AttendanceService, AttendanceManager
from app.models.attendance import AttendanceResponse

router = APIRouter(prefix="/attendance", tags=["attendance"])

# �������
def get_attendance_manager():
    return AttendanceManager()

def get_attendance_service(attendance_manager: AttendanceManager = Depends(get_attendance_manager)):
    return AttendanceService(attendance_manager)

@router.get("/{userid}/details", response_model=AttendanceResponse)
async def get_attendance_details(
    userid: str,
    start_time: datetime,
    end_time: datetime,
    attendance_service: AttendanceService = Depends(get_attendance_service)
):

 #   �˵�㣺��ȡ�û���������
 #  - ֻ����HTTP����߼�
 # - ���÷���㴦��ҵ���߼�

    try:
        result = await attendance_service.process_attendance_for_user(userid, start_time, end_time)
        
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
    #����û��Ƿ�Ӧ��ǩ��
    should_check = await attendance_service.attendance_manager.should_check_in(userid)
    return {"userid": userid, "should_check_in": should_check}

@router.get("/{userid}/should-check-out")
async def should_check_out(
    userid: str,
    attendance_service: AttendanceService = Depends(get_attendance_service)
):
    #����û��Ƿ�Ӧ��ǩ��
    should_check = await attendance_service.attendance_manager.should_check_out(userid)
    return {"userid": userid, "should_check_out": should_check}