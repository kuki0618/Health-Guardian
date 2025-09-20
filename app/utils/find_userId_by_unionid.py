import pymysql.cursors

from core import database

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
                # �ύ����
        except Exception as e:
        # ��������ʱ�ع�
            conn.rollback()
            raise e
        finally:
            cursor.close()