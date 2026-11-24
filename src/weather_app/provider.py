from datetime import datetime,timezone
import asyncio
import httpx
BASE='https://api.open-meteo.com/v1/forecast'; GEO='https://geocoding-api.open-meteo.com/v1/search'; AIR='https://air-quality-api.open-meteo.com/v1/air-quality'
class WeatherProviderError(RuntimeError): pass
async def _json(client,url,params):
 for attempt in range(3):
  try:
   r=await client.get(url,params=params)
   if r.status_code==429 or r.status_code>=500:
    if attempt<2: await asyncio.sleep(1.5*(attempt+1)); continue
   r.raise_for_status(); return r.json()
  except httpx.HTTPError as e:
   if attempt==2: raise WeatherProviderError(f'Weather provider request failed: {e}') from e
   await asyncio.sleep(1.5*(attempt+1))
 raise WeatherProviderError('Weather provider remained unavailable after retries.')
async def geocode(city):
 try:
  async with httpx.AsyncClient(timeout=18) as c: data=await _json(c,GEO,{'name':city,'count':1,'language':'en','format':'json'})
 except WeatherProviderError as e: raise WeatherProviderError(f'Geocoding service unavailable: {e}') from e
 rows=data.get('results',[])
 if not rows: raise WeatherProviderError(f"No place found for '{city}'. Check spelling.")
 x=rows[0]; return {'name':', '.join(y for y in [x.get('name'),x.get('admin1'),x.get('country')] if y),'latitude':x['latitude'],'longitude':x['longitude'],'timezone':x.get('timezone','auto')}
async def fetch_weather(loc):
 p={'latitude':loc['latitude'],'longitude':loc['longitude'],'timezone':loc.get('timezone','auto'),'forecast_days':7,'wind_speed_unit':'ms','current':'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,is_day','hourly':'temperature_2m,apparent_temperature,precipitation_probability,precipitation,relative_humidity_2m,wind_speed_10m,wind_gusts_10m,cloud_cover,uv_index,pressure_msl,visibility,weather_code','daily':'weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,wind_speed_10m_max,uv_index_max,sunrise,sunset'}
 try:
  async with httpx.AsyncClient(timeout=25) as c: raw=await _json(c,BASE,p)
 except WeatherProviderError as e: raise WeatherProviderError(f'Weather request failed: {e}') from e
 aq=None
 try:
  async with httpx.AsyncClient(timeout=18) as c: aq=await _json(c,AIR,{'latitude':loc['latitude'],'longitude':loc['longitude'],'timezone':loc.get('timezone','auto'),'current':'european_aqi,pm2_5,pm10','hourly':'european_aqi'})
 except WeatherProviderError: pass
 return {'raw':raw,'air_quality':aq,'fetched_at':datetime.now(timezone.utc).isoformat()}

