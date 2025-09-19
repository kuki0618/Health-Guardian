# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing import Optional

class WeatherResponse(BaseModel):
    temperature: str 
    weather: str 
    humidity: str 
    windpower: str 
    
