import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from api.dependencies.dingtalk_token import get_dingtalk_access_token
from api.models.FreeBusy import FreeBusyRequest, FreeBusyResponse
from utils.find_userId_by_unionid import find_unionid_by_userId,find_userid_by_unionid
from repository import database
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
                    # 定时事件，其“日期”可以从 dateTime 中提取
                    date = start_time.split('T')[0] # 从 '2024-09-20T10:00:00+08:00' 中提取 '2024-09-20'
                elif 'date' in item['start']:
                    date = item['start']['date']
                    start_time = None # 全天事件可能没有具体开始时间点

                end = item['end']
                if 'dateTime' in end:
                    end_time = end['dateTime']
                elif 'date' in end:
                    end_time = end['date']
                else:
                    end_time = None

                # 创建扁平化的字典
                flat_data = {
                    # 第一层数据
                    'userId': userId,
                    "date":date,
                    'start_datetime': start_time,
                    'end_datetime': end_time
                }
                
                flat_data_list.append(flat_data)
        return flat_data_list
    
    async def get_user_free_busy_status(self,request:FreeBusyRequest)-> List[FreeBusyResponse]:

            access_token = await get_dingtalk_access_token()

            
            # 构建请求数据
            data = request.dict()

            
            url = f"https://api.dingtalk.com/v1.0/calendar/users/{request.userIds[0]}/querySchedule"
            headers = {
                "Content-Type": "application/json",
                "x-acs-dingtalk-access-token": access_token  # 关键修改：使用正确的头部
            }
            try:
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url, headers=headers,json=data)

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
        #获取用户忙闲状态
        #查询最近2小时的日程信息
    
        try:
            # 设置查询时间范围（当前时间到2小时前）
            time_max = datetime.now()
            time_min = time_max - timedelta(hours=3)
            
            # 格式化时间字符串（ISO 8601格式）
            startTime = time_min.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
            endTime = time_max.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

            unionid = await find_unionid_by_userId(userId,conn=database.get_db_connection())
            request = FreeBusyRequest(
                userIds=[unionid],
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
                # 第一步：插入主表 online_status，获取attendance_id
                    insert_main_query = f"""
                    INSERT INTO online_status (userid, date) 
                    VALUES (%s, %s)
                    """
                    cursor.execute(insert_main_query, (userId, date))
                    
                    # 获取刚插入的主键ID
                    task_id = cursor.lastrowid
                    
                # 第二步：插入子表 online_time_periods
                insert_period_query = f"""
                INSERT INTO online_time_periods (task_id, start_datetime, end_datetime) 
                VALUES (%s, %s, %s)
                """
                
                # 处理datetime格式（移除时区信息）
                def format_datetime(dt_str):
                    if dt_str and 'T' in dt_str:
                        if '+' in dt_str:
                            dt_str = dt_str.split('+')[0]
                        return dt_str.replace('T', ' ')
                    return dt_str
                
                # 插入时间段数据
                cursor.execute(insert_period_query, (
                    task_id,
                    format_datetime(start_datetime),
                    format_datetime(end_datetime)
                ))
            
                # 提交事务
            conn.commit()
        except Exception as e:
        # 发生错误时回滚
            conn.rollback()
            raise e
        finally:
            cursor.close()

    async def get_online_time_periods(
            self,
        userid:str, 
        target_times: List[str],
        conn )-> List[Dict[str, Any]]:
        all_periods = {}
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        for target_time in target_times:
        # 查询主表获取attendance_id
            query_main = f"""
            SELECT id FROM online_status
            WHERE userid = %s AND date = %s
            """
            cursor.execute(query_main, (userid, target_time))
            main_record = cursor.fetchone()
            
            if not main_record:
                print(f"未找到员工 {userid} 在 {target_time} 的记录")
                continue
            
            task_id = main_record['id']
            
            # 查询时间段子表
            query_periods = f"""
            SELECT start_datetime, end_datetime 
            FROM online_time_periods 
            WHERE task_id = %s 
            ORDER BY start_datetime
            """
            cursor.execute(query_periods, (task_id,))
            periods = []
            for period in cursor.fetchall():
                periods.append((period['start_datetime'], period['end_datetime']))
            all_periods[target_time] = periods
        
        return all_periods
