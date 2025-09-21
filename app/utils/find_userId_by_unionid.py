import pymysql.cursors

async def find_userid_by_unionid(
        unionid: str,
        conn
        ):
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            select_query = """
            SELECT userid FROM employees WHERE unionid = %s
            """
            cursor.execute(select_query, (unionid,))
            result= cursor.fetchone()
            conn.commit()
            return result['userid'] if result else None
                # 提交事务
        except Exception as e:
        # 发生错误时回滚
            conn.rollback()
            raise e
        finally:
            cursor.close()
    
async def find_unionid_by_userId(
        userId: str,
        conn
        ):
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            select_query = """
            SELECT unionid FROM employees WHERE userid = %s
            """
            cursor.execute(select_query, (userId,))
            result= cursor.fetchone()
            conn.commit()
            return result['unionid'] if result else None
                # 提交事务
        except Exception as e:
        # 发生错误时回滚
            conn.rollback()
            raise e
        finally:
            cursor.close()