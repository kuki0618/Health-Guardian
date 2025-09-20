import httpx
from typing import Dict, Any
from api.dependencies.dingtalk_token import get_dingtalk_access_token
from api.models.message import AsyncSendRequest

class SendMessageService:
    def __init__(self):
        self.async_send_url = "https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2"
    
    async def async_send_message(self, request: AsyncSendRequest) -> Dict[str, Any]:
        #�첽������Ϣ����
        
        try:
            # 1. ��ȡ��������
            access_token = await get_dingtalk_access_token()
            
            # 2. ׼������ͷ
            params = {"access_token": access_token}

            headers = {"Content-Type": "application/json"}
            
            # 3. ׼��������
            data = {
                "agent_id": request.agent_id,
                "to_all_user": False,  # ����userid_list���ͣ�����ȫ���û�
                "userid_list": request.userid_list,
                "msg": request.msg.dict()
            }
            
            # 4. �����첽��Ϣ����
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.async_send_url,
                    params=params,
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                response_data = response.json()
                
                if response.status_code != 200:
                    error_msg = response_data.get("message", "send message failed")
                    raise Exception(f"API error: {error_msg}")
                
                return response_data
                
        except httpx.RequestError as e:
            raise Exception(f"internet request error: {str(e)}")
        except Exception as e:
            raise Exception(f"send message error: {str(e)}")