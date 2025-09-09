from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from core import database

app = FastAPI()

# ��ȡ���б�
@app.get("/tables")
async def get_tables(conn = Depends(database.get_db)):
    #�������ݿ��α�
    cursor = conn.cursor(dictionary=True)
    #ִ�� SQL ��� "SHOW TABLES" ��ѯ���б�
    cursor.execute("SHOW TABLES")
    #��ȡ���в�ѯ���
    tables = cursor.fetchall()
    return {"tables": [table[f"Tables_in_{database.db_config['database']}"] for table in tables]}

# ��ȡ��ṹ
@app.get("/table/{table_name}/columns")
async def get_table_columns(table_name: str, conn = Depends(database.get_db)):
    cursor = conn.cursor(dictionary=True)
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
    cursor = conn.cursor(dictionary=True)
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
    cursor = conn.cursor(dictionary=True)
    
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

# ������ѯ
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

# ��������
@app.post("/{table_name}")
async def create_item(
    table_name: str,
    item: dict,
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(dictionary=True)
    
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

# ��������
@app.put("/{table_name}/{id}")
async def update_item(
    table_name: str,
    id: int,
    item: dict,
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(dictionary=True)
    
    # ��ȡ�����ֶ���
    cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
    primary_key = cursor.fetchone()
    if not primary_key:
        raise HTTPException(status_code=400, detail="No primary key found")
    
    pk_column = primary_key['Column_name']
    
    # �����������
    set_clause = ", ".join([f"{key} = %s" for key in item.keys()])
    values = tuple(item.values()) + (id,)
    
    query = f"UPDATE {table_name} SET {set_clause} WHERE {pk_column} = %s"
    cursor.execute(query, values)
    conn.commit()
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": "Item updated"}

# ɾ������
@app.delete("/{table_name}/{id}")
async def delete_item(
    table_name: str,
    id: int,
    conn = Depends(database.get_db)
):
    cursor = conn.cursor(dictionary=True)
    
    # ��ȡ�����ֶ���
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