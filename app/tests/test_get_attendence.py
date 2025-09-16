# -*- coding: utf-8 -*-
import os
import sys
from fastapi import FastAPI,HTTPException
from datetime import date,datetime

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir) 
sys.path.insert(0, app_dir)  

from services.dingtalk.get_attendence import process_attendance_for_user

@app.get("/attendence-info")
async def test_token():
    try:
        attendence_data = await process_attendance_for_user("manager4585",datetime(2025,9,10),datetime(2025,9,11))
        return attendence_data
    except HTTPException as e:
        return {"error": str(e.detail)}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)