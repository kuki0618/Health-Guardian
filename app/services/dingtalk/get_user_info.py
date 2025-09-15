from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import httpx

from dependencies.dingtalk_token import get_dingtalk_access_token

app = FastAPI(title="�����û���ϢAPI", version="1.0.0")

class UserIdRequest(BaseModel):
    userid: str = Query(..., description="�û�ID")

class Result(BaseModel):
    userid:str
    name:str
    title:str
    extension:str

class UserDetailResponse(BaseModel):
    errcode:int
    result:Result
    
        
@app.post("/v1.0/contact/users/get",response_model=UserDetailResponse)
async def get_user_details(userid:str):
    """
    ��ȡ�û�������Ϣ
    - access_token: ��ѯ�����еķ�������
    - userid: �������е��û�ID
    """
    access_token = await get_dingtalk_access_token()
    
    # ���ö���API
    url = "https://api.dingtalk.com/v1.0/contact/users/get"
    params = {"accessToken": access_token}
    headers = {"Content-Type": "application/json"}
    data = {"userid": userid}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, params=params,headers=headers,json=data)
            response.raise_for_status()
            #��JSON�ַ���ת��ΪPython�ֵ�/����
            response = response.json()
            if "extension" in data["result"]:
                extension_data = data["result"].pop("extension")  # ɾ��extension����ȡ������
                data["result"].update(extension_data)  # ��extension���ݺϲ���result��
            data["hobby"] = data["result"].pop("����")
            data["age"] = data["result"].pop("����")
        except httpx.HTTPStatusError as e:  
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="�û�������")
            else:
                error_detail = e.response.json().get("message", "����API����ʧ��")
                raise HTTPException(status_code=e.response.status_code, detail=error_detail)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"���ö���APIʧ��: {str(e)}")
