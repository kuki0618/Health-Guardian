# -*- coding: utf-8 -*-
import os
import sys
from fastapi import FastAPI,HTTPException

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir) 
sys.path.insert(0, app_dir)  

from services.dingtalk.get_user_info import get_user_details

@app.get("/user-info")
async def test_token():
    try:
        user_info = await get_user_details(userid="manager4585")
        return user_info
    except HTTPException as e:
        return {"error": str(e.detail)}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)