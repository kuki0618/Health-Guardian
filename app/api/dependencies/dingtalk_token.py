# -*- coding: utf-8 -*-
from fastapi import FastAPI,HTTPException
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

DINGTALK_APP_KEY = os.getenv("DINGTALK_APP_KEY")
DINGTALK_APP_SECRET = os.getenv("DINGTALK_APP_SECRET")

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
            print(f"get access token data: {token_data}")
            return token_data["accessToken"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"fail to get access token: {str(e)}")
        
#https://api.dingtalk.com/v1.0/oauth2/accessToken