from core.config import FastAPI,HTTPException,BaseModel,List,httpx,Dict,Any

app = FastAPI(title="钉钉运动步数查询服务")

DINGTALK_APP_KEY = "ding58btzmclcdgd18uu"
DINGTALK_APP_SECRET = "G3CsonOxr853FnDiEd3k0PaJOHBj6qCs-d9ILKsrVApZbyHE2Opp4E-yN-ljgrhT"

# 数据模型
class StepInfo(BaseModel):
    step_count: int  # 步数

class UserStepResponse(BaseModel):
    stepinfo_list: List[StepInfo]
    errcode:int

'''获取凭证信息'''
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

@app.get("/user/steps",response_model=UserStepResponse)
async def fetch_user_steps(
    object_id: str,
    stat_date: str,
    type:int=0,
) -> Dict[str, Any]:
    """
    获取个人钉钉运动步数
    """
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
        raise HTTPException(status_code=e.response.status_code, detail=f"API请求失败: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"请求异常: {e}")
    
#外部函数示例
async def get_sport_info(user_id:str):
    sport_data = await fetch_user_steps(object_id=user_id,stat_date=date.today().strftime("%Y-%m-%d"))
    return sport_data