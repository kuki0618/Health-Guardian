from fastapi import FastAPI,HTTPException,httpx

DINGTALK_APP_KEY = "ding58btzmclcdgd18uu"
DINGTALK_APP_SECRET = "G3CsonOxr853FnDiEd3k0PaJOHBj6qCs-d9ILKsrVApZbyHE2Opp4E-yN-ljgrhT"

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
