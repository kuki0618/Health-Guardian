# -*- coding: utf-8 -*-
import os
import sys
from fastapi import FastAPI,HTTPException

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir) 
sys.path.insert(0, app_dir)  

from api.endpoints import message

app.include_router(message.router)
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)