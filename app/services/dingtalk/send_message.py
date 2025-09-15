from fastapi import FastAPI, HTTPException
import httpx
from pydantic import BaseModel
from typing import List
from dependencies.dingtalk_token import get_dingtalk_access_token

app = FastAPI(title="������ҵ��Ϣ����API", version="1.0.0")

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

