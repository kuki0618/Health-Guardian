# -*- coding: utf-8 -*-
from fastapi import FastAPI,HTTPException
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

DINGTALK_APP_KEY = os.getenv("DINGTALK_APP_KEY")
DINGTALK_APP_SECRET = os.getenv("DINGTALK_APP_SECRET")

async def get_dingtalk_access_token() -> str:
    url = "https://oapi.dingtalk.com/gettoken"
    params = {
        "appkey": DINGTALK_APP_KEY,
        "appsecret": DINGTALK_APP_SECRET
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            token_data = response.json()
            return token_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"fail to get access token: {str(e)}")
