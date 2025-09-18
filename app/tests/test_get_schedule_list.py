# -*- coding: utf-8 -*-
import os
import sys
from fastapi import FastAPI,HTTPException
from datetime import date,datetime

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir) 
sys.path.insert(0, app_dir)  

from app.api.endpoints.Calendar import get_calendar_events

app.include_router(get_calendar_events.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,port=8000)