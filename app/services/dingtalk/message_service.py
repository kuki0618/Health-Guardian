import httpx
from typing import Dict, Any
from api.dependencies.dingtalk_token import get_dingtalk_access_token
from api.models.message import AsyncSendRequest
from datetime import datetime
import pymysql.cursors

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
        
    async def insert_health_message(
            self, 
            userId: str, 
            health_msg: str, 
            time: datetime,
            conn):
        # ���뽡����Ϣ�����ݿ�
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            date= time.strftime("%Y-%m-%d")
            select_query = """  
            SELECT id FROM online_status WHERE userid = %s AND date = %s
            """
            cursor.execute(select_query, (userId, date))
            existing_record = cursor.fetchone()

            if existing_record:
                task_id = existing_record['id']
                logger.info(f"record exist,id: {task_id}")
            else:
            # ��һ������������ online_status����ȡattendance_id
                insert_main_query = f"""
                INSERT INTO online_status (userid, date) 
                VALUES (%s, %s)
                """
                cursor.execute(insert_main_query, (userId, date))
            
            # ��ȡ�ղ��������ID
            task_id = cursor.lastrowid
                
            # �ڶ����������ӱ� online_time_periods
            insert_period_query = f"""
            INSERT INTO health_messages (task_id, msg, date_time) 
            VALUES (%s, %s, %s)
            """
            
            date_time = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # ����ʱ�������
            cursor.execute(insert_period_query, (
                task_id,
                health_msg,
                date_time
            ))
        
            # �ύ����
            conn.commit()
        except Exception as e:
        # ��������ʱ�ع�
            conn.rollback()
            raise e
        finally:
            cursor.close()
