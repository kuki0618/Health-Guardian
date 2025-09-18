# app/api/endpoints/attendance.py
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import List

from core import database
from services.dingtalk.attendance_service import AttendanceService, AttendanceManager
from api.models.attendance import AttendanceResponse,AttendanceRequest

router = APIRouter(prefix="/attendance", tags=["attendance"])

# �������
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

 #   �˵�㣺��ȡ�û���������
 #  - ֻ����HTTP����߼�
 # - ���÷���㴦��ҵ���߼�

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
  
    #������ӿ��ڼ�¼�����ݿ�
    try:
        # ���÷����ķ���
        await attendance_service.add_attendence_info(mock_records, conn)
        return {
            "message": "attendance records add successed",
            "count": len(mock_records['recordresult']),
            "records": mock_records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"attendance records add failed: {str(e)}")