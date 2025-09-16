# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import httpx
import json
from dependencies.dingtalk_token import get_dingtalk_access_token

app = FastAPI(title="API", version="1.0.0")

class UserIdRequest(BaseModel):
    userid: str = Query(..., description="ID")

class Result(BaseModel):
    userid:str
    name:str
    title:str
    extension:str

class UserDetailResponse(BaseModel):
    errcode:int
    result:Result
    
        
@app.post("/v1.0/contact/users/get",response_model=UserDetailResponse)
async def get_user_details(userid:str):
    try:
        access_token = await get_dingtalk_access_token()
        
        # 调用钉钉API
        url = "https://oapi.dingtalk.com/topapi/v2/user/get"
        data = {
            "userid": userid,
            "language": "zh_CN"  # 添加语言参数
        }
        params = {
            "access_token": access_token
        }
        headers = {
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params, headers=headers,json=data)
            response.raise_for_status()
            #从JSON字符串转换为Python字典/对象
            response = response.json()
            print(f"={json.dumps(response, ensure_ascii=False, indent=2)}")
            if response.get('errcode') != 0:
                error_msg = response.get('errmsg', 'Unknown error')
                raise HTTPException(status_code=400, detail=f"call dingtalk api failed: {error_msg}")

            if "extension" in response["result"]:
                extension_data = response["result"].pop("extension")  # 删除extension并获取其内容
                response["result"].update(extension_data)  # 将extension内容合并到result中
            #response["hobby"] = response["result"].get("爱好", "")
            #response["age"] = response["result"].get("年龄", "")
            return response
    except httpx.HTTPStatusError as e:
        print(f"http error: {e.response.status_code},{e.response.text}")
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="user no exist")
        else:
            error_detail = e.response.json().get("errmsg", "call dingtalk api failed")
            raise HTTPException(status_code=e.response.status_code, detail=error_detail)
    except Exception as e:
        print(f"other errors: {str(e)}")
        raise HTTPException(status_code=500, detail=f" call dingtalk api failed: {str(e)}")
