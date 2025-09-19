import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from api.dependencies.dingtalk_token import get_dingtalk_access_token
from api.models.steps import UserStepResponse, UserStepRequest

logger = logging.getLogger(__name__)

class SportService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_user_steps(self, request: UserStepRequest) -> UserStepResponse:
        #获取用户步数信息 - 服务层方法
        try:
            access_token = await get_dingtalk_access_token()
            
            api_url = "https://oapi.dingtalk.com/topapi/health/stepinfo/list"
            params = {"access_token": access_token}
            headers = {"Content-Type": "application/json"}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_url, 
                    params=params, 
                    headers=headers, 
                    json=request.dict(),
                    timeout=30.0
                )
                response.raise_for_status()
                
                response_data = response.json()
                logger.debug(f"steps API response: {response_data}")
                
                # 转换为Pydantic模型
                step_response = UserStepResponse(**response_data)
                return step_response
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP query fail: {e}")
            raise Exception(f"API query fail: {e}")
        except Exception as e:
            logger.error(f"get steps info fail: {str(e)}")
            raise Exception(f"get steps info fail: {str(e)}")
