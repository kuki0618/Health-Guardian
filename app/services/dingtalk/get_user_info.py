from core.config import FastAPI,HTTPException,BaseModel,Optional,Dict,Any,get_dingtalk_access_token,httpx,Query

app = FastAPI(title="�����û���ϢAPI", version="1.0.0")

class UserIdRequest(BaseModel):
    userid: str = Query(..., description="�û�ID")

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
    ��ȡ�û�������Ϣ
    - access_token: ��ѯ�����еķ�������
    - userid: �������е��û�ID
    """
    access_token = await get_dingtalk_access_token()
    
    # ���ö���API
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
                raise HTTPException(status_code=404, detail="�û�������")
            else:
                error_detail = e.response.json().get("message", "����API����ʧ��")
                raise HTTPException(status_code=e.response.status_code, detail=error_detail)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"���ö���APIʧ��: {str(e)}")
