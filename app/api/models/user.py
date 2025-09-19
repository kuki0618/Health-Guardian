from pydantic import BaseModel
from typing import Optional

class UserDetailResponse(BaseModel):
    userid: str
    name: str
    title: Optional[str] = None
    hobby: Optional[str] = None
    age: Optional[str] = None
    unionid: str
    '''
    {"userid":"manager4585",
    "name":"173******04",
    "title":"","hobby":"","age":"",
    "unionid":"6kPiPK8K1yV8lDlRc50TKFwiEiE"}
    '''
    