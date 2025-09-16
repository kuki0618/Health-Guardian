# -*- coding: utf-8 -*-
import os
import sys
from fastapi import FastAPI,HTTPException
from datetime import date

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir) 
sys.path.insert(0, app_dir)  

from services.dingtalk.get_sport_info import fetch_user_steps

@app.get("/sport-info")
async def get_sport_info():
    try:
        sport_data = await fetch_user_steps(object_id="manager4585",stat_date=date.today().strftime("%Y-%m-%d"))
        return sport_data
    except HTTPException as e:
        return {"error": str(e.detail)}
    
'''
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''