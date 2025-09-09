from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from core import database

app = FastAPI()

# 获取所有表
@app.get("/tables")
async def get_tables(conn = Depends(database.get_db)):
    #创建数据库游标
    cursor = conn.cursor(dictionary=True)
    #执行 SQL 语句 "SHOW TABLES" 查询所有表
    cursor.execute("SHOW TABLES")
    #获取所有查询结果
    tables = cursor.fetchall()
    return {"tables": [table[f"Tables_in_{database.db_config['database']}"] for table in tables]}

# 获取表结构
@app.get("/table/{table_name}/columns")
async def get_table_columns(table_name: str, conn = Depends(database.get_db)):
    cursor = conn.cursor(dictionary=True)
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
    cursor = conn.cursor(dictionary=True)
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
    cursor = conn.cursor(dictionary=True)
    
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

# 条件查询
@app.get("/{table_name}/search")
async def search_items(
    table_name: str,
    field: str,
    value: str,
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(dictionary=True)
    query = f"SELECT * FROM {table_name} WHERE {field} LIKE %s"
    cursor.execute(query, (f"%{value}%",))
    rows = cursor.fetchall()
    return {"data": rows}

# 插入数据
@app.post("/{table_name}")
async def create_item(
    table_name: str,
    item: dict,
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(dictionary=True)
    
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

# 更新数据
@app.put("/{table_name}/{id}")
async def update_item(
    table_name: str,
    id: int,
    item: dict,
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(dictionary=True)
    
    # 获取主键字段名
    cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
    primary_key = cursor.fetchone()
    if not primary_key:
        raise HTTPException(status_code=400, detail="No primary key found")
    
    pk_column = primary_key['Column_name']
    
    # 构建更新语句
    set_clause = ", ".join([f"{key} = %s" for key in item.keys()])
    values = tuple(item.values()) + (id,)
    
    query = f"UPDATE {table_name} SET {set_clause} WHERE {pk_column} = %s"
    cursor.execute(query, values)
    conn.commit()
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": "Item updated"}

# 删除数据
@app.delete("/{table_name}/{id}")
async def delete_item(
    table_name: str,
    id: int,
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(dictionary=True)
    
    # 获取主键字段名
    cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
    primary_key = cursor.fetchone()
    if not primary_key:
        raise HTTPException(status_code=400, detail="No primary key found")
    
    pk_column = primary_key['Column_name']
    
    query = f"DELETE FROM {table_name} WHERE {pk_column} = %s"
    cursor.execute(query, (id,))
    conn.commit()
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": "Item deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)