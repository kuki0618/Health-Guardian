from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from repository import database
from services.dingtalk.user_service import UserService
from api.models.user import UserDetailResponse

router = APIRouter(prefix="/user_info", tags=["user_info"])

# 依赖项函数

def get_user_service():
    return UserService()

@router.get("/{userid}/info", response_model=UserDetailResponse)
async def get_user_details(
    userid: str,
    user_service: UserService = Depends(get_user_service)
):
    
    #获取用户详情
    #- 端点层只处理HTTP相关逻辑
    #- 调用服务层处理业务逻辑
    
    try:
        user_info = await user_service.get_user_details(userid)
        return user_info
        
    except Exception as e:
        if "user not exist" in str(e):
            raise HTTPException(status_code=404, detail="user not exist")
        else:
            raise HTTPException(status_code=500, detail=f"get user details fail: {str(e)}")

@router.get("/add_records")
async def test_add_attendance_records(
    user_service: UserService = Depends(get_user_service),
    conn = Depends(database.get_db)
):
    mock_records ={"userid":"manager4585",
    "name":"173******04",
    "title":"","hobby":"","age":"",
    "unionid":"6kPiPK8K1yV8lDlRc50TKFwiEiE"}
  
    #测试添加考勤记录到数据库
    try:
        # 调用服务层的方法
        await user_service.add_employee_info(mock_records, conn)
        return {
            "message": "employee records add successed",
            "records": mock_records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"attendance records add failed: {str(e)}")