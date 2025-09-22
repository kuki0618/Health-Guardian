import httpx
import json
import logging
from typing import Dict, Any,List
import pymysql.cursors

from api.dependencies.dingtalk_token import get_dingtalk_access_token
from api.models.user import UserDetailResponse

logger = logging.getLogger(__name__) 

class UserService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_user_details(self, userid: str) -> UserDetailResponse:
        #获取用户详情 - 服务层方法
        logger = logging.getLogger(__name__)
        try:
            access_token = await get_dingtalk_access_token()
            logger.info(f"获取到凭证:{access_token}")
            
            # 调用钉钉API
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
                
                # 验证响应
                if response_data.get('errcode') != 0:
                    error_msg = response_data.get('errmsg', 'Unknown error')
                    logger.error(f"调用用户信息API时错误: {error_msg}")
                    raise Exception(f"API fail: {error_msg}")
                
                # 转换数据格式
                user_info = self._transform_user_data(response_data)
                logger.info(f"获取到用户详情: {user_info}")
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
        #转换用户数据格式 - 业务逻辑
        result = response_data.get("result", {})
        
        # 处理extension字段
        extension_data = {}
        if "extension" in result:
           extension_data = result.pop("extension")  # 删除extension并获取其内容
           result.update(extension_data)  # 将extension内容合并到result中
        
        # 创建用户信息对象
        user_info = UserDetailResponse(
            userid=result.get("userid"),
            name=result.get("name"),
            unionid=result.get("unionid"),
            title=result.get("title", ""),
            hobby=extension_data.get("hobby",""),
            age=extension_data.get("age", "")
        )
        
        return user_info
    
    def add_employee_info(
        self,
        item: dict,
        conn
    ):
        cursor = None
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # 构建插入语句
            columns = ", ".join(item.keys())
            placeholders = ", ".join(["%s"] * len(item))
            values = tuple(item.values())

            # 检查是否已存在
            check_query = "SELECT userid FROM employees WHERE userid = %s"
            cursor.execute(check_query, (item['userid'],))
            existing = cursor.fetchone()
            if existing:
                logger.info(f"用户 {item['userid']}信息已存在")
            else:
                query = f"INSERT INTO employees ({columns}) VALUES ({placeholders})"
                cursor.execute(query, values)
                logger.info(f"用户 {item['userid']}信息添加成功")

            conn.commit()
            
        except Exception as e:
        # 发生错误时回滚
            conn.rollback()
            logger.error(f"插入用户信息失败: {e}")
            raise e
        finally:
            if cursor:
                cursor.close()
    def get_userinfo_from_database(
            self,
        userid:str, 
        conn 
        ) -> List[Dict[str, Any]]:
        cursor = None
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            # 查询主表获取attendance_id
            query_main = f"""
            SELECT name,title,hobby,age FROM employees
            WHERE userid = %s
            """
            cursor.execute(query_main, (userid,))
            user_record = cursor.fetchone()
            conn.commit()
            if user_record:
                return user_record
            else:
                logger.info(f"{userid} 有问题，找不到用户数据")
                return None
            
        except Exception as e:
        # 发生错误时回滚
            conn.rollback()
            logger.error(f"插入用户信息失败: {e}")
            raise e
        finally:
            if cursor:
                cursor.close()
        
        