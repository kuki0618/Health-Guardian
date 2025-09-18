from pydantic import BaseModel
from typing import Optional

class UserDetailResponse(BaseModel):
    userid: str
    name: str
    title: Optional[str] = None
    hobby: Optional[str] = None
    age: Optional[str] = None
    unionid: str
    