from pydantic import BaseModel
from typing import List

class TextContent(BaseModel):
    content: str

class Message(BaseModel):
    msgtype: str
    text: TextContent 

class AsyncSendRequest(BaseModel):
    #异步发送消息请求模型
    agent_id: int  # 应用ID
    userid_list: str # 用户ID,用逗号分割
    msg: Message