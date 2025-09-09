from core.config import FastAPI,HTTPException,BaseModel,Optional,Dict,Any,get_dingtalk_access_token,httpx,Query

app = FastAPI(title="钉钉用户信息API", version="1.0.0")

class UserIdRequest(BaseModel):
    userid: str = Query(..., description="用户ID")

class UserDetailResponse(BaseModel):
    userid: str
    unionid: Optional[str] = None
    name: str
    avatar: Optional[str] = None
    state_code: str
    manager_userid: Optional[str] = None
    mobile: Optional[str] = None
    hide_mobile: Optional[bool] = None
    telephone: Optional[str] = None
    job_number: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    work_place: Optional[str] = None
    remark: Optional[str] = None
    org_email: Optional[str] = None
    dept_id_list: Optional[list] = None
    dept_order_list: Optional[list] = None
    extension: Optional[str] = None
    hired_date: Optional[int] = None
    active: Optional[bool] = None
    real_authed: Optional[bool] = None
    admin: Optional[bool] = None
    boss: Optional[bool] = None
    exclusive_account: Optional[bool] = None
    login_id: Optional[str] = None
    exclusive_account_type: Optional[str] = None
        
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
            return response.json()
        except httpx.HTTPStatusError as e:  
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="用户不存在")
            else:
                error_detail = e.response.json().get("message", "钉钉API调用失败")
                raise HTTPException(status_code=e.response.status_code, detail=error_detail)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"调用钉钉API失败: {str(e)}")
