from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import httpx

from dependencies.dingtalk_token import get_dingtalk_access_token

app = FastAPI(title="钉钉用户信息API", version="1.0.0")

class UserIdRequest(BaseModel):
    userid: str = Query(..., description="用户ID")

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
    """
    获取用户详情信息
    - access_token: 查询参数中的访问令牌
    - userid: 请求体中的用户ID
    """
    access_token = await get_dingtalk_access_token()
    
    # 调用钉钉API
    url = "https://api.dingtalk.com/v1.0/contact/users/get"
    params = {"accessToken": access_token}
    headers = {"Content-Type": "application/json"}
    data = {"userid": userid}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, params=params,headers=headers,json=data)
            response.raise_for_status()
            #从JSON字符串转换为Python字典/对象
            response = response.json()
            if "extension" in data["result"]:
                extension_data = data["result"].pop("extension")  # 删除extension并获取其内容
                data["result"].update(extension_data)  # 将extension内容合并到result中
            data["hobby"] = data["result"].pop("爱好")
            data["age"] = data["result"].pop("年龄")
        except httpx.HTTPStatusError as e:  
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="用户不存在")
            else:
                error_detail = e.response.json().get("message", "钉钉API调用失败")
                raise HTTPException(status_code=e.response.status_code, detail=error_detail)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"调用钉钉API失败: {str(e)}")
