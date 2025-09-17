# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx
from datetime import date

from dependencies.dingtalk_token import get_dingtalk_access_token

app = FastAPI(title="service")

# 数据模型
class StepInfo(BaseModel):
    step_count: int  # 步数

class UserStepResponse(BaseModel):
    stepinfo_list: List[StepInfo]
    errcode:int

@app.get("/user/steps",response_model=UserStepResponse)
async def fetch_user_steps(
    object_id: str,
    stat_date: str,
    type:int=0,
) -> Dict[str, Any]:
    access_token = await get_dingtalk_access_token()
    api_url = "https://api.dingtalk.com/v1.0/contact/users/steps/statistics/query"
    params = {"accessToken": access_token}
    headers = {"Content-Type": "application/json"}
    data = {"object_id":object_id,
            "stat_dates":stat_date,
            "type":type}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, params=params, headers=headers,data=data,timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"API query fail: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API query fail: {e}")
