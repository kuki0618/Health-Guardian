import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pymysql.cursors
from api.dependencies.dingtalk_token import get_dingtalk_access_token
from api.models.steps import UserStepResponse, UserStepRequest, StepInfo

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
                logger.debug(f"得到API响应: {response_data}")
                
                # 转换为Pydantic模型
                return  response_data 
                
        except httpx.HTTPStatusError as e:
            logger.error(f"API查询失败: {e}")
            raise Exception(f"API查询失败: {e}")
        except Exception as e:
            logger.error(f"获取步数失败: {str(e)}")
            raise Exception(f"获取步数失败: {str(e)}")
        
    async def get_steps_record(
        self,
        userid:str,
        date:str,
        conn 
    )->int:
        # 插入用户步数信息
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            # 查询主表获取attendance_id
            query_main = f"""
            SELECT steps FROM online_status
            WHERE userid = %s AND date = %s
            """
            cursor.execute(query_main, (userid,date))
            steps_record = cursor.fetchone()
            conn.commit()
            return steps_record
            
        except Exception as e:
        # 发生错误时回滚
            conn.rollback()
            logger.error(f"查找用户步数失败: {e}")
            raise e
        finally:
            if cursor:
                cursor.close()
        
        