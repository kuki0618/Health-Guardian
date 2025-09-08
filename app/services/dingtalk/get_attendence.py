from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any,List
import httpx
import datetime
from datetime import date

app = FastAPI(title="�����û���ϢAPI", version="1.0.0")

DINGTALK_APP_KEY = "ding58btzmclcdgd18uu"
DINGTALK_APP_SECRET = "G3CsonOxr853FnDiEd3k0PaJOHBj6qCs-d9ILKsrVApZbyHE2Opp4E-yN-ljgrhT"

class AttendanceRequest(BaseModel):
    userid: str 
    start_time:str
    end_time:str
    cursor:int = 0
    size:int = 50

class CheckInRecord(BaseModel):
    checkin_time: int  # ǩ��ʱ�䣬��λ����
    detail_place: str  # ǩ����ϸ��ַ
    remark: str  # ǩ����ע
    userid: str  # �û�id
    place: str  # ǩ����ַ
    visit_user: str  # �ݷö���
    latitude: str  # γ��
    longitude: str  # ����
    image_list: List[str]  # ǩ����Ƭ�б�
    location_method: str  # ��λ����
    ssid: str  # SSID
    mac_addr: str  # Mac��ַ
    corp_id: str  # ��ҵid

class AttendanceResponse(BaseModel):
    success: bool  # �Ƿ�ɹ�
    result: Optional[List[CheckInRecord]] = None  # ǩ����¼�б�
    error_code: Optional[str] = None  # ������
    error_msg: Optional[str] = None  # ������Ϣ
    next_cursor: Optional[int] = None  # ��һ�β�ѯ���α�
    has_more: Optional[bool] = None  # �Ƿ��и�������

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
            raise HTTPException(status_code=500, detail=f"��ȡ��������ʧ��: {str(e)}")
        
@app.post("/attendance/list")
async def get_attendance_details(request:AttendanceRequest):

    access_token = await get_dingtalk_access_token()
    
    # ���ö���API
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
                raise HTTPException(status_code=404, detail="�û�������")
            else:
                error_detail = e.response.json().get("message", "����API����ʧ��")
                raise HTTPException(status_code=e.response.status_code, detail=error_detail)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"���ö���APIʧ��: {str(e)}")
