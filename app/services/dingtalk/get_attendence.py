from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any,List
import httpx
import datetime
from datetime import date

app = FastAPI(title="钉钉用户信息API", version="1.0.0")

DINGTALK_APP_KEY = "ding58btzmclcdgd18uu"
DINGTALK_APP_SECRET = "G3CsonOxr853FnDiEd3k0PaJOHBj6qCs-d9ILKsrVApZbyHE2Opp4E-yN-ljgrhT"

class AttendanceRequest(BaseModel):
    userid: str 
    start_time:str
    end_time:str
    cursor:int = 0
    size:int = 50

class CheckInRecord(BaseModel):
    checkin_time: int  # 签到时间，单位毫秒
    detail_place: str  # 签到详细地址
    remark: str  # 签到备注
    userid: str  # 用户id
    place: str  # 签到地址
    visit_user: str  # 拜访对象
    latitude: str  # 纬度
    longitude: str  # 经度
    image_list: List[str]  # 签到照片列表
    location_method: str  # 定位方法
    ssid: str  # SSID
    mac_addr: str  # Mac地址
    corp_id: str  # 企业id

class AttendanceResponse(BaseModel):
    success: bool  # 是否成功
    result: Optional[List[CheckInRecord]] = None  # 签到记录列表
    error_code: Optional[str] = None  # 错误码
    error_msg: Optional[str] = None  # 错误信息
    next_cursor: Optional[int] = None  # 下一次查询的游标
    has_more: Optional[bool] = None  # 是否还有更多数据

async def get_dingtalk_access_token() -> str:
    url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
    data = {
        "appKey": DINGTALK_APP_KEY,
        "appSecret": DINGTALK_APP_SECRET
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data)
            response.raise_for_status()
            token_data = response.json()
            return token_data["accessToken"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取访问令牌失败: {str(e)}")
        
@app.post("/attendance/list")
async def get_attendance_details(request:AttendanceRequest):

    access_token = await get_dingtalk_access_token()
    
    # 调用钉钉API
    url = "https://oapi.dingtalk.com/attendance/list"
    params = {"accessToken": access_token}
    headers = {"Content-Type": "application/json"}
    data = {"userid": "zhangsan",
            "workDateFrom":"2020-09-06 00:00:00",
            "workDateTo":"2020-09-07 00:00:00"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, params=params,headers=headers,json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:  
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="用户不存在")
            else:
                error_detail = e.response.json().get("message", "钉钉API调用失败")
                raise HTTPException(status_code=e.response.status_code, detail=error_detail)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"调用钉钉API失败: {str(e)}")
