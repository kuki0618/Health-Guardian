import httpx
import json
import logging
from typing import Dict, Any
from api.dependencies.dingtalk_token import get_dingtalk_access_token
from api.models.user import UserDetailResponse

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_user_details(self, userid: str) -> UserDetailResponse:
        #��ȡ�û����� - ����㷽��
        try:
            access_token = await get_dingtalk_access_token()
            logger.info(f"get access token success: {access_token}")
            
            # ���ö���API
            url = "https://oapi.dingtalk.com/topapi/v2/user/get"
            data = {
                "userid": userid,
                "language": "zh_CN"
            }
            params = {"access_token": access_token}
            headers = {"Content-Type": "application/json"}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, params=params, headers=headers, json=data)
                response.raise_for_status()
                
                response_data = response.json()
                logger.debug(f"API response: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                
                # ��֤��Ӧ
                if response_data.get('errcode') != 0:
                    error_msg = response_data.get('errmsg', 'Unknown error')
                    raise Exception(f"API fail: {error_msg}")
                
                # ת�����ݸ�ʽ
                user_info = self._transform_user_data(response_data)
                return user_info
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise Exception(f"user  not exist")
            else:
                error_detail = e.response.json().get("errmsg", "API call failed")
                raise Exception(f"HTTP error: {error_detail}")
        except Exception as e:
            logger.error(f"get user details fail: {str(e)}")
            raise
    
    def _transform_user_data(self, response_data: Dict[str, Any]) -> UserDetailResponse:
        #ת���û����ݸ�ʽ - ҵ���߼�
        result = response_data.get("result", {})
        
        # ����extension�ֶ�
        extension_data = {}
        if "extension" in result:
           extension_data = result.pop("extension")  # ɾ��extension����ȡ������
           result.update(extension_data)  # ��extension���ݺϲ���result��
        
        # �����û���Ϣ����
        user_info = UserDetailResponse(
            userid=result.get("userid"),
            name=result.get("name"),
            unionid=result.get("unionid"),
            title=result.get("title", ""),
            hobby=extension_data.get("hobby",""),
            age=extension_data.get("age", "")
        )
        
        return user_info