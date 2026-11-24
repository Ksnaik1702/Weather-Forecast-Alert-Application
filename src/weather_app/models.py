from typing import Optional
from pydantic import BaseModel,ConfigDict
class Location(BaseModel):
 name:str; latitude:float; longitude:float; timezone:str='auto'
class CurrentWeather(BaseModel):
 time:str=''; temperature_2m:Optional[float]=None; relative_humidity_2m:Optional[float]=None; apparent_temperature:Optional[float]=None; precipitation:Optional[float]=None; weather_code:Optional[int]=None; wind_speed_ms:Optional[float]=None; is_day:Optional[int]=None
class Alert(BaseModel):
 code:str; label:str; severity:str; message:str
class WeatherBundle(BaseModel):
 model_config=ConfigDict(extra='ignore')
 location:Location; provider:str; fetched_at:str; units:dict={}; current:CurrentWeather; hourly:list[dict]; daily:list[dict]; air_quality:Optional[dict]=None; alerts:list[Alert]
