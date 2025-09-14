from fastapi import FastAPI, HTTPException
import httpx
import json
import time
from typing import Optional
from pydantic import BaseModel

app = FastAPI(title="钉钉企业消息推送API", version="1.0.0")

DINGTALK_APP_KEY = "ding58btzmclcdgd18uu"
DINGTALK_APP_SECRET = "G3CsonOxr853FnDiEd3k0PaJOHBj6qCs-d9ILKsrVApZbyHE2Opp4E-yN-ljgrhT"

# 钉钉API端点
DINGTALK_ACCESS_TOKEN_URL = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
DINGTALK_ASYNC_SEND_URL = "https://api.dingtalk.com/v1.0/robot/asyncSend"

class message(BaseModel):
    msgtype:str
    content:str

class AsyncSendRequest(BaseModel):
    """异步发送消息请求模型"""
    agent_id :int# 消息模板变量
    userid_list: List[str]  # 消息类型
    msg:message


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
            raise HTTPException(status_code=500, detail=f"获取访问令牌失败: {str(e)}")

def reschedule_data(data:dict):
    final_data = []

@app.post("/async-send-message")
async def send_message(request: AsyncSendRequest):
    """
    异步发送企业会话消息
    
    参数:
    - msg_param: 消息模板变量，JSON格式
    - msg_key: 消息类型，如 "sampleText"、"sampleImageMsg"等
    - user_id: 接收人userId
    - robot_code: 机器人编码
    """
    try:
        # 1. 获取访问令牌
        access_token = await get_dingtalk_access_token()
        
        # 2. 构建请求头
        headers = {
            "Content-Type": "application/json",
            "x-acs-dingtalk-access-token": access_token
        }
        
        # 3. 构建请求体
        data = {
            "agent_id": 11,
            "to_all_user":True,
            "userid_list": request.msg_key,
            "msg":request.msg
        }
        
        # 4. 发送异步消息请求
        async with httpx.AsyncClient() as client:
            response = await client.post(
                DINGTALK_ASYNC_SEND_URL,
                headers=headers,
                json=data
            )
            
            response_data = response.json()
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response_data.get("message", "发送消息失败")
                )
            
            # 返回处理结果
            return {
                "success": True,
                "message": "消息已异步发送",
                "data": response_data,
                "processQueryKey": response_data.get("processQueryKey")
            }
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"网络请求错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)