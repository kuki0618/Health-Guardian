from fastapi import FastAPI, HTTPException
import httpx
import json
import time
from typing import Optional
from pydantic import BaseModel

app = FastAPI(title="������ҵ��Ϣ����API", version="1.0.0")

DINGTALK_APP_KEY = "ding58btzmclcdgd18uu"
DINGTALK_APP_SECRET = "G3CsonOxr853FnDiEd3k0PaJOHBj6qCs-d9ILKsrVApZbyHE2Opp4E-yN-ljgrhT"

# ����API�˵�
DINGTALK_ACCESS_TOKEN_URL = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
DINGTALK_ASYNC_SEND_URL = "https://api.dingtalk.com/v1.0/robot/asyncSend"

class message(BaseModel):
    msgtype:str
    content:str

class AsyncSendRequest(BaseModel):
    """�첽������Ϣ����ģ��"""
    agent_id :int# ��Ϣģ�����
    userid_list: List[str]  # ��Ϣ����
    msg:message


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

def reschedule_data(data:dict):
    final_data = []

@app.post("/async-send-message")
async def send_message(request: AsyncSendRequest):
    """
    �첽������ҵ�Ự��Ϣ
    
    ����:
    - msg_param: ��Ϣģ�������JSON��ʽ
    - msg_key: ��Ϣ���ͣ��� "sampleText"��"sampleImageMsg"��
    - user_id: ������userId
    - robot_code: �����˱���
    """
    try:
        # 1. ��ȡ��������
        access_token = await get_dingtalk_access_token()
        
        # 2. ��������ͷ
        headers = {
            "Content-Type": "application/json",
            "x-acs-dingtalk-access-token": access_token
        }
        
        # 3. ����������
        data = {
            "agent_id": 11,
            "to_all_user":True,
            "userid_list": request.msg_key,
            "msg":request.msg
        }
        
        # 4. �����첽��Ϣ����
        async with httpx.AsyncClient() as client:
            response = await client.post(
                DINGTALK_ASYNC_SEND_URL,
                headers=headers,
                json=data
            )
            
            response_data = response.json()
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response_data.get("message", "������Ϣʧ��")
                )
            
            # ���ش�����
            return {
                "success": True,
                "message": "��Ϣ���첽����",
                "data": response_data,
                "processQueryKey": response_data.get("processQueryKey")
            }
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"�����������: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"������Ϣʧ��: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)