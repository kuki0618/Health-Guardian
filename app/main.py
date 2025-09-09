from .services.dingtalk.get_user_info import get_user_details
from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from core import database
from repository import action

action.create_item()
action.get_tables(table_name="Allusers")

userids = ["zhangsan","lisi","zhaowu"]
for userid in userids:
    result = get_user_details(userid)
    action.create_item(table_name="Allusers",item=result)
    
