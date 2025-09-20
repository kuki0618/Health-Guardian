import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from api.dependencies.dingtalk_token import get_dingtalk_access_token
from api.models.FreeBusy import FreeBusyRequest, FreeBusyResponse
from utils.find_userId_by_unionid import find_userid_by_unionid
import pymysql.cursors

logger = logging.getLogger(__name__)

class FreeBusyService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    def reschedule_data(self,data:dict):
        flat_data_list = []
        for schedule_info in data['scheduleInformation']:
            userId = schedule_info['userId']
            for item in schedule_info['scheduleItems']:

                start = item['start']
                if 'dateTime' in start:
                    start_time = item['start']['dateTime']
                    # ��ʱ�¼����䡰���ڡ����Դ� dateTime ����ȡ
                    date = start_time.split('T')[0] # �� '2024-09-20T10:00:00+08:00' ����ȡ '2024-09-20'
                elif 'date' in item['start']:
                    date = item['start']['date']
                    start_time = None # ȫ���¼�����û�о��忪ʼʱ���

                end = item['end']
                if 'dateTime' in end:
                    end_time = end['dateTime']
                elif 'date' in end:
                    end_time = end['date']
                else:
                    end_time = None

                # ������ƽ�����ֵ�
                flat_data = {
                    # ��һ������
                    'userId': userId,
                    "date":date,
                    'start_datetime': start_time,
                    'end_datetime': end_time
                }
                
                flat_data_list.append(flat_data)
        return flat_data_list
    
    async def get_user_free_busy_status(self,request:FreeBusyRequest)-> List[FreeBusyResponse]:

            access_token = await get_dingtalk_access_token()

            
            # ������������
            data = request.dict()

            
            url = f"https://api.dingtalk.com/v1.0/calendar/users/{request.userIds[0]}/querySchedule"
            headers = {
                "Content-Type": "application/json",
                "x-acs-dingtalk-access-token": access_token  # �ؼ��޸ģ�ʹ����ȷ��ͷ��
            }
            try:
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url, headers=headers,json=data)
                    #�����߼��޸�
                    if response.status_code == 200:
            
                        result = response.json()
                    
                        if len(result["scheduleInformation"])!=0:
                            result = self.reschedule_data(result)
                            return result
                        else: 
                            return []
                        
                    else:
                        error_msg = f"status quary fail: {response.status_code}, {response.text}"
                        raise Exception(error_msg)

            except httpx.RequestError as e:
                logger.error(f"internet quary fail: {str(e)}")
                raise Exception(f"internet quary fail: {str(e)}") from e
            except Exception as e:
               logger.error(f"quary process fail: {str(e)}")
               raise Exception(f"quary process fail: {str(e)}") from e
            
    async def get_user_free_busy_now_status(
            self,
            userId:str
        )-> List[FreeBusyResponse]:
    
        #��ȡ�û�æ��״̬
        #��ѯ���2Сʱ���ճ���Ϣ
    
        try:
            # ���ò�ѯʱ�䷶Χ����ǰʱ�䵽2Сʱǰ��
            time_max = datetime.now()
            time_min = time_max - timedelta(hours=2)
            
            # ��ʽ��ʱ���ַ�����ISO 8601��ʽ��
            startTime = time_min.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
            endTime = time_max.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

            request = FreeBusyRequest(
                userIds=[userId],
                startTime=startTime,
                endTime=endTime
            )
            result = await self.get_user_free_busy_status(request)
            return result
            
        except Exception as e:
               logger.error(f"quary process fail: {str(e)}")
               raise Exception(f"quary process fail: {str(e)}") from e
        
    async def insert_freebusy_record(
        self,
        data_list: List[dict],
        conn 
    ):
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            for data in data_list:
                userId = await find_userid_by_unionid(data['userId'],conn)
                if not userId:
                    logger.error(f"user {data['userId']} not found")
                    continue
                date = data['date']
                start_datetime = data['start_datetime']
                end_datetime = data['end_datetime']
            
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
                INSERT INTO online_time_periods (task_id, start_datetime, end_datetime) 
                VALUES (%s, %s, %s)
                """
                
                # ����datetime��ʽ���Ƴ�ʱ����Ϣ��
                def format_datetime(dt_str):
                    if dt_str and 'T' in dt_str:
                        if '+' in dt_str:
                            dt_str = dt_str.split('+')[0]
                        return dt_str.replace('T', ' ')
                    return dt_str
                
                # ����ʱ�������
                cursor.execute(insert_period_query, (
                    task_id,
                    format_datetime(start_datetime),
                    format_datetime(end_datetime)
                ))
            
                # �ύ����
            conn.commit()
        except Exception as e:
        # ��������ʱ�ع�
            conn.rollback()
            raise e
        finally:
            cursor.close()
