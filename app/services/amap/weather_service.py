#coding=utf-8
import requests
from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging
from core import config

AMAP_API_KEY =config.AMAP_API_KEY

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.amap_api_key = AMAP_API_KEY
        self.base_url = "https://restapi.amap.com/v3/weather/weatherInfo"

    async def get_weather_data(self, city: str, extensions: str = "base") -> Dict[str, Any]:
        
        #��ȡ�ߵµ�ͼ��������
        
        params = {
            "key": self.amap_api_key,
            "city": city,
            "extensions": extensions,
            "output": "JSON"
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            weather_data = response.json()

            if weather_data["status"] != "1":
                error_msg = f"API check fail:{weather_data.get('info', 'unknown error')}"
                logger.error(error_msg)
                raise HTTPException(status_code=400, detail=error_msg)

            # ��ʽ����������
            return self._format_weather_data(weather_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Internet quary fail:{str(e)}")
            raise HTTPException(status_code=503)
        except Exception as e:
            logger.error(f"Weather data quary fail: {str(e)}")
            raise HTTPException(status_code=500)

    def _format_weather_data(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
            #��ʽ����������
            live_data = weather_data["lives"][0]
            
            return {
                "temperature": live_data["temperature"],      # �¶�(��)
                "weather": live_data["weather"],              # ����״��
                "humidity": live_data["humidity"],            # ʪ��(%)
                "windpower": live_data["windpower"],          # ����
            }