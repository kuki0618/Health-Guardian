from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from core import database
from datetime import datetime

app = FastAPI()

# 获取所有表
@app.get("/tables")
async def get_tables(conn = Depends(database.get_db)):
    #创建数据库游标
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    #执行 SQL 语句 "SHOW TABLES" 查询所有表
    cursor.execute("SHOW TABLES")
    #获取所有查询结果
    tables = cursor.fetchall()
    return {"tables": [table[f"Tables_in_{database.db_config['database']}"] for table in tables]}

# 获取表结构
@app.get("/table/{table_name}/columns")
async def get_table_columns(table_name: str, conn = Depends(database.get_db)):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(f"DESCRIBE {table_name}")
    #tables = cursor.fetchall()
    columns = cursor.fetchall()
    return {"columns": columns}

# 查询表中的所有数据
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

# 根据ID查询单条记录
@app.get("/{table_name}/{id}")
async def get_item_by_id(
    table_name: str,
    id: int,
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 先获取主键字段名
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

# 查询某个表的所有主键值
@app.get("/{table_name}/values")
async def get_primary_values(table_name:str,conn = Depends(database.get_db)):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
    pk_column = cursor.fetchone()[4]  # Column_name是第5个字段

    cursor.execute(f"SELECT {pk_column} FROM {table_name}")
    pk_values = [row[0] for row in cursor.fetchall()]
    return pk_values

# 插入数据
@app.post("/{table_name}")
async def create_item(
    table_name: str,
    item: dict,
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 构建插入语句
    columns = ", ".join(item.keys())
    placeholders = ", ".join(["%s"] * len(item))
    values = tuple(item.values())
    
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, values)
    conn.commit()
    
    # 获取插入的ID
    if cursor.lastrowid:
        return {"message": "Item created", "id": cursor.lastrowid}
    return {"message": "Item created"}

#插入数据到关联表
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
        
        # 第一步：插入主表 online_status，获取attendance_id
        insert_main_query = f"""
        INSERT INTO {father_table_name} (userid, date) 
        VALUES (%s, %s)
        """
        cursor.execute(insert_main_query, (user_id, date))
        
        # 获取刚插入的主键ID
        attendance_id = cursor.lastrowid
        
        # 第二步：插入子表 online_time_periods
        insert_period_query = f"""
        INSERT INTO {son_table_name} (attendance_id, start_datetime, end_datetime) 
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
            attendance_id,
            format_datetime(start_datetime),
            format_datetime(end_datetime)
        ))
    
        # 提交事务
        conn.commit()
    '''
    if cursor.lastrowid:
        return {"message": "Item created", "id": cursor.lastrowid}
    return {"message": "Item created"}
    '''
#获取指定员工和日期的在线时间段数据
def get_online_time_periods(
        userid:str, 
        target_times: List[str],
        conn = Depends(database.get_db)) -> List[Dict[str, Any]]:
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
                return []
            
            task_id = main_record['id']
            
            # 查询时间段子表
            query_periods = f"""
            SELECT start_datetime, end_datetime 
            FROM online_time_periods 
            WHERE task_id = %s 
            ORDER BY start_datetime
            """
            cursor.execute(query_periods, (task_id,))
            all_periods[target_time] = cursor.fetchall()
        
        return all_periods

#插入健康提醒数据到提醒表
async def insert_health_msg(
    user_id: str,
    msg:str,
    Time:datetime,
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    date = Time.strftime("%Y-%m-%d")

    # 第一步：插入主表 online_status，获取attendance_id
    insert_main_query = f"""
    INSERT INTO online_status (userid, date) 
    VALUES (%s, %s)
    """
    cursor.execute(insert_main_query, (user_id, date))
    
    # 获取刚插入的主键ID
    main_id = cursor.lastrowid
    time = Time.strftime("%Y-%m-%d %H:%M:%S")

    # 第二步：插入子表 online_time_periods
    insert_period_query = f"""
    INSERT INTO health_msg (msg_id,data_time,msg) 
    VALUES (%s, %s, %s)
    """
    cursor.execute(insert_period_query, (main_id, time, msg))

    # 提交事务
    conn.commit()
'''
if cursor.lastrowid:
    return {"message": "Item created", "id": cursor.lastrowid}
return {"message": "Item created"}
'''
#插入签到数据到相关表
def add_attendence_info(
        all_data:List[dict],
        conn = Depends(database.get_db)
        ):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    for data in all_data:
        user_id = data['user_id']
        date = data['date']

        # 第一步：插入主表 online_status，获取attendance_id
        insert_main_query = f"""
        INSERT INTO online_status (userid, date) 
        VALUES (%s, %s)
        """
        cursor.execute(insert_main_query, (user_id, date))
        
        # 获取刚插入的主键ID
        main_id = cursor.lastrowid

        time = data['datetime']
        checkType = data['checkType']
        # 第二步：插入子表 online_time_periods
        insert_period_query = f"""
        INSERT INTO attendence_data (task_id,userCheckTime,checkType) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_period_query, (main_id, time, checkType))

        # 提交事务
    conn.commit()
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
