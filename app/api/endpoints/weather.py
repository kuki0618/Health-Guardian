# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query
from services.amap.weather_service import WeatherService
from api.models.weather import WeatherResponse
import os
from dotenv import load_dotenv

load_dotenv()

AMAP_API_KEY = os.getenv("AMAP_API_KEY")
    
router = APIRouter(prefix="/weather", tags=["weather"])

# 依赖项：获取天气服务实例
def get_weather_service(api_key: str = AMAP_API_KEY) -> WeatherService:
    print(f"get amap api key: {api_key}")
    return WeatherService(api_key)

@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    city: str = Query("320500", description="CityID"),
    weather_service: WeatherService = Depends(get_weather_service)
) -> WeatherResponse:
    #获取当前天气信息
    
    try:
        weather_data = await weather_service.get_weather_data(city)
        return weather_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"weather query fail: {str(e)}")