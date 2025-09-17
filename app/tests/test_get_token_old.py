import os
import sys
from fastapi import FastAPI,HTTPException

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir) 
sys.path.insert(0, app_dir)  

from dependencies.dingtalk_token_old import get_dingtalk_access_token


@app.get("/test-token-old")
async def test_token():
    try:
        access_token = await get_dingtalk_access_token()
        return {"access_token": access_token}
    except HTTPException as e:
        return {"error": str(e.detail)}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1",port=8000)