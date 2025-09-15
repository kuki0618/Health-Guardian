# -*- coding: utf-8 -*-
from fastapi import FastAPI,HTTPException
import httpx
import os

DINGTALK_APP_KEY = os.getenv("DINGTALK_APP_KEY")
DINGTALK_APP_SECRET = os.getenv("DINGTALK_APP_SECRET")

app = FastAPI()
async def get_dingtalk_access_token() -> str:
    url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
    data = {
        "appKey": DINGTALK_APP_KEY,
        "appSecret": DINGTALK_APP_SECRET
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data)
            response.raise_for_status()
            token_data = response.json()
            return token_data["accessToken"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"fail to get access token: {str(e)}")
        
@app.get("/test-token")
async def test_token():
    try:
        access_token = await get_dingtalk_access_token()
        return {"access_token": access_token}
    except HTTPException as e:
        return {"error": str(e.detail)}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
