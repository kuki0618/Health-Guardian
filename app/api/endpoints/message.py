# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime

from services.dingtalk.message_service import SendMessageService
from api.models.message import AsyncSendRequest,Message,TextContent
from repository import database
from core.config import AGENT_ID
router = APIRouter(prefix="/message", tags=["message"])

#
def get_send_message_service():
    return SendMessageService()

@router.post("/async-send/")
async def async_send_message(
    request: AsyncSendRequest,
    send_message_service: SendMessageService = Depends(get_send_message_service)
):
    
    #异步发送企业会话消息
    
    try:
        # 调用服务层发送消息
        response_data = await send_message_service.async_send_message(request)
        
        # 返回成功响应
        return {
            "success": True,
            "message": "message sent successfully",
            "data": response_data,
            "processQueryKey": response_data.get("processQueryKey")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"send message failed: {str(e)}"
        )
    
@router.get("/mock-send/{userid}")
async def async_send_message(
    userid:str,
    send_message_service: SendMessageService = Depends(get_send_message_service)
):
   
    #异步发送消息接口
    
    try:
        request = AsyncSendRequest(
            userid_list=userid,
            agent_id = int(AGENT_ID),
            msg=Message(
                msgtype="text",
                text=TextContent(
                    content="照顾好自己"
                )
            )
        )
        # 调用服务层发送消息
        response_data = await send_message_service.async_send_message(request)
        
        # 返回成功响应
        return {
            "success": True,
            "message": "message sent successfully",
            "data": response_data,
            "processQueryKey": response_data.get("processQueryKey")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"send message failed: {str(e)}"
        )
@router.get("/test-add-records")
async def test_add_attendance_records(
    send_message_service: SendMessageService = Depends(get_send_message_service),
    conn = Depends(database.get_db)
):
    mock_records =[
        {"userId":"manager4585",
         "health_msg":"2025-09-20",
        "time":datetime.now(),
        }]
  
    #测试添加考勤记录到数据库
    try:
        # 调用服务层的方法
        await send_message_service.insert_health_message(mock_records, conn)
        return {
            "message": "freebusy records add successed",
            "records": mock_records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"attendance records add failed: {str(e)}")
