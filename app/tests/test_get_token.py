from fastapi import FastAPI,HTTPException
from dependencies.dingtalk_token import get_dingtalk_access_token

app = FastAPI()

@app.get("/test-token")
async def test_token():
    try:
        access_token = await get_dingtalk_access_token()
        return {"access_token": access_token}
    except HTTPException as e:
        return {"error": str(e.detail)}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
