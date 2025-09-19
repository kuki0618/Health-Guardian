from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from core import database
from datetime import datetime

app = FastAPI()

# ��ȡ���б�
@app.get("/tables")
async def get_tables(conn = Depends(database.get_db)):
    #�������ݿ��α�
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    #ִ�� SQL ��� "SHOW TABLES" ��ѯ���б�
    cursor.execute("SHOW TABLES")
    #��ȡ���в�ѯ���
    tables = cursor.fetchall()
    return {"tables": [table[f"Tables_in_{database.db_config['database']}"] for table in tables]}

# ��ȡ��ṹ
@app.get("/table/{table_name}/columns")
async def get_table_columns(table_name: str, conn = Depends(database.get_db)):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(f"DESCRIBE {table_name}")
    #tables = cursor.fetchall()
    columns = cursor.fetchall()
    return {"columns": columns}

# ��ѯ���е���������
@app.get("/{table_name}")
async def get_table_data(
    table_name: str,
    limit: int = 100,
    offset: int = 0,
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = f"SELECT * FROM {table_name} LIMIT %s OFFSET %s"
    cursor.execute(query, (limit, offset))
    rows = cursor.fetchall()
    return {"data": rows, "table": table_name}

# ����ID��ѯ������¼
@app.get("/{table_name}/{id}")
async def get_item_by_id(
    table_name: str,
    id: int,
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # �Ȼ�ȡ�����ֶ���
    cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
    primary_key = cursor.fetchone()
    if not primary_key:
        raise HTTPException(status_code=400, detail="No primary key found")
    
    pk_column = primary_key['Column_name']
    query = f"SELECT * FROM {table_name} WHERE {pk_column} = %s"
    cursor.execute(query, (id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return row

# ��ѯĳ�������������ֵ
@app.get("/{table_name}/values")
async def get_primary_values(table_name:str,conn = Depends(database.get_db)):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
    pk_column = cursor.fetchone()[4]  # Column_name�ǵ�5���ֶ�

    cursor.execute(f"SELECT {pk_column} FROM {table_name}")
    pk_values = [row[0] for row in cursor.fetchall()]
    return pk_values

# ��������
@app.post("/{table_name}")
async def create_item(
    table_name: str,
    item: dict,
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # �����������
    columns = ", ".join(item.keys())
    placeholders = ", ".join(["%s"] * len(item))
    values = tuple(item.values())
    
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, values)
    conn.commit()
    
    # ��ȡ�����ID
    if cursor.lastrowid:
        return {"message": "Item created", "id": cursor.lastrowid}
    return {"message": "Item created"}

#�������ݵ�������
async def insert_online_item(
    father_table_name: str,
    son_table_name:str,
    data_list: List[dict],
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    for data in data_list:
        user_id = data['user_id']
        date = data['date']
        start_datetime = data['start_datetime']
        end_datetime = data['end_datetime']
        
        # ��һ������������ online_status����ȡattendance_id
        insert_main_query = f"""
        INSERT INTO {father_table_name} (userid, date) 
        VALUES (%s, %s)
        """
        cursor.execute(insert_main_query, (user_id, date))
        
        # ��ȡ�ղ��������ID
        attendance_id = cursor.lastrowid
        
        # �ڶ����������ӱ� online_time_periods
        insert_period_query = f"""
        INSERT INTO {son_table_name} (attendance_id, start_datetime, end_datetime) 
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
            attendance_id,
            format_datetime(start_datetime),
            format_datetime(end_datetime)
        ))
    
        # �ύ����
        conn.commit()
    '''
    if cursor.lastrowid:
        return {"message": "Item created", "id": cursor.lastrowid}
    return {"message": "Item created"}
    '''
#��ȡָ��Ա�������ڵ�����ʱ�������
def get_online_time_periods(
        userid:str, 
        target_times: List[str],
        conn = Depends(database.get_db)) -> List[Dict[str, Any]]:
        all_periods = {}
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        for target_time in target_times:
        # ��ѯ�����ȡattendance_id
            query_main = f"""
            SELECT id FROM online_status
            WHERE userid = %s AND date = %s
            """
            cursor.execute(query_main, (userid, target_time))
            main_record = cursor.fetchone()
            
            if not main_record:
                print(f"δ�ҵ�Ա�� {userid} �� {target_time} �ļ�¼")
                return []
            
            task_id = main_record['id']
            
            # ��ѯʱ����ӱ�
            query_periods = f"""
            SELECT start_datetime, end_datetime 
            FROM online_time_periods 
            WHERE task_id = %s 
            ORDER BY start_datetime
            """
            cursor.execute(query_periods, (task_id,))
            all_periods[target_time] = cursor.fetchall()
        
        return all_periods

#���뽡���������ݵ����ѱ�
async def insert_health_msg(
    user_id: str,
    msg:str,
    Time:datetime,
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    date = Time.strftime("%Y-%m-%d")

    # ��һ������������ online_status����ȡattendance_id
    insert_main_query = f"""
    INSERT INTO online_status (userid, date) 
    VALUES (%s, %s)
    """
    cursor.execute(insert_main_query, (user_id, date))
    
    # ��ȡ�ղ��������ID
    main_id = cursor.lastrowid
    time = Time.strftime("%Y-%m-%d %H:%M:%S")

    # �ڶ����������ӱ� online_time_periods
    insert_period_query = f"""
    INSERT INTO health_msg (msg_id,data_time,msg) 
    VALUES (%s, %s, %s)
    """
    cursor.execute(insert_period_query, (main_id, time, msg))

    # �ύ����
    conn.commit()
'''
if cursor.lastrowid:
    return {"message": "Item created", "id": cursor.lastrowid}
return {"message": "Item created"}
'''
#����ǩ�����ݵ���ر�
def add_attendence_info(
        all_data:List[dict],
        conn = Depends(database.get_db)
        ):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    for data in all_data:
        user_id = data['user_id']
        date = data['date']

        # ��һ������������ online_status����ȡattendance_id
        insert_main_query = f"""
        INSERT INTO online_status (userid, date) 
        VALUES (%s, %s)
        """
        cursor.execute(insert_main_query, (user_id, date))
        
        # ��ȡ�ղ��������ID
        main_id = cursor.lastrowid

        time = data['datetime']
        checkType = data['checkType']
        # �ڶ����������ӱ� online_time_periods
        insert_period_query = f"""
        INSERT INTO attendence_data (task_id,userCheckTime,checkType) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_period_query, (main_id, time, checkType))

        # �ύ����
    conn.commit()
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
