from pydantic import BaseModel
from typing import List

class TextContent(BaseModel):
    content: str

class Message(BaseModel):
    msgtype: str
    text: TextContent 

class AsyncSendRequest(BaseModel):
    #�첽������Ϣ����ģ��
    agent_id: int  # Ӧ��ID
    userid_list: str # �û�ID,�ö��ŷָ�
    msg: Message