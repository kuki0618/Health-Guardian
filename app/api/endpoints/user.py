from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from app.services.user_service import UserService
from app.models.user import UserDetailResponse

router = APIRouter(prefix="/user_info", tags=["user_info"])

# 依赖项函数
def get_user_service():
    return UserService()

@router.get("/{userid}", response_model=UserDetailResponse)
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