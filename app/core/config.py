from fastapi import FastAPI, HTTPException, BackgroundTasks,Query
import uvicorn
from pydantic import BaseModel
import asyncio
from typing import Optional, List, Dict, Any
import httpx
import datetime
from datetime import time, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from dependencies.dingtalk_token import get_dingtalk_access_token
