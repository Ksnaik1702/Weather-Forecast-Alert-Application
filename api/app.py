from fastapi import FastAPI,HTTPException,Query
from fastapi.responses import FileResponse
from src.weather_app.service import live_weather
from src.weather_app.storage import history,export_csv,locations,latest_for_location,save
from src.weather_app.demo import simulated_weather
from src.weather_app.provider import WeatherProviderError
app=FastAPI(title='Weather Forecast & Alert API',version='1.0.0',description='Live and simulated weather, saved locations, alerts, and reports.')
@app.get('/health')
def health(): return {'status':'ok','service':'weather-api'}
@app.get('/locations')
def get_locations(): return locations()
@app.post('/locations')
async def add_location(city:str=Query(min_length=2,max_length=100),mode:str='live'):
 try:
  b=simulated_weather(city) if mode=='simulation' else await live_weather(city)
  if mode=='simulation': save(b)
  return {'location':b['location'],'locations':locations()}
 except WeatherProviderError as e: raise HTTPException(502,str(e)) from e
async def get_bundle(city,mode,location_id=None):
 if location_id is not None:
  b=latest_for_location(location_id)
  if b is None: raise HTTPException(404,'Saved location or forecast not found. Add it with POST /locations first.')
  return b
 if mode=='simulation':
  b=simulated_weather(city); save(b); return b
 if mode!='live': raise HTTPException(400,"mode must be 'live' or 'simulation'")
 return await live_weather(city)
@app.get('/weather')
async def weather(city:str=Query(default='New Delhi',min_length=2,max_length=100),mode:str='live'):
 try: return await get_bundle(city,mode)
 except WeatherProviderError as e: raise HTTPException(502,str(e)) from e
@app.get('/forecast/hourly')
async def hourly(city:str|None=None,location_id:int|None=None,hours:int=Query(default=24,ge=1,le=48),mode:str='live'):
 try: b=await get_bundle(city or 'New Delhi',mode,location_id); return b['hourly'][:hours]
 except WeatherProviderError as e: raise HTTPException(502,str(e)) from e
@app.get('/forecast/daily')
async def daily(city:str|None=None,location_id:int|None=None,days:int=Query(default=7,ge=1,le=7),mode:str='live'):
 try: b=await get_bundle(city or 'New Delhi',mode,location_id); return b['daily'][:days]
 except WeatherProviderError as e: raise HTTPException(502,str(e)) from e
@app.get('/alerts')
async def alerts(city:str|None=None,location_id:int|None=None,mode:str='live'):
 try:
  b=await get_bundle(city or 'New Delhi',mode,location_id); return {'location':b['location'],'alerts':b['alerts']}
 except WeatherProviderError as e: raise HTTPException(502,str(e)) from e
@app.get('/history')
def get_history(limit:int=Query(default=10,ge=1,le=100)): return history(limit)
@app.get('/report.csv')
async def report(city:str=Query(min_length=2),mode:str='live'):
 try: b=await get_bundle(city,mode); path=export_csv(b); return FileResponse(path,media_type='text/csv',filename='weather_forecast.csv')
 except WeatherProviderError as e: raise HTTPException(502,str(e)) from e
