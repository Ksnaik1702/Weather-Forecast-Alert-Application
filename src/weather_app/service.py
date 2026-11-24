from .provider import geocode,fetch_weather
from .alerts import evaluate
from .storage import save
from .models import WeatherBundle

def _rows(series,limit=None):
 times=series.get('time',[]); unique={}
 for i,stamp in enumerate(times):
  if not isinstance(stamp,str) or not stamp: continue
  row={k:v[i] for k,v in series.items() if isinstance(v,list) and i<len(v)}
  row['time']=stamp; unique[stamp]=row
 rows=[unique[k] for k in sorted(unique)]
 return rows[:limit] if limit else rows

def normalize(loc,res):
 raw=res['raw']; c=raw.get('current',{}); d=raw.get('daily',{}); h=raw.get('hourly',{})
 hourly=_rows(h,48); daily=_rows(d)
 for row in hourly:
  row['wind_speed_ms']=row.pop('wind_speed_10m',None)
  row['wind_gust_ms']=row.pop('wind_gusts_10m',None)
 for row in daily: row['wind_max_ms']=row.pop('wind_speed_10m_max',None)
 current={'time':c.get('time',''),'temperature_2m':c.get('temperature_2m'),'relative_humidity_2m':c.get('relative_humidity_2m'),'apparent_temperature':c.get('apparent_temperature'),'precipitation':c.get('precipitation'),'weather_code':c.get('weather_code'),'wind_speed_ms':c.get('wind_speed_10m'),'is_day':c.get('is_day')}
 daily_series={k:[row.get(k) for row in daily] for k in (daily[0] if daily else {})}
 b={'location':loc,'provider':'Open-Meteo','fetched_at':res['fetched_at'],'units':{'temperature':'°C','precipitation':'mm','wind':'m/s','visibility':'m'},'current':current,'hourly':hourly,'daily':daily,'air_quality':res.get('air_quality')}
 b['alerts']=evaluate(current,daily_series,res.get('air_quality'),hourly)
 return WeatherBundle.model_validate(b).model_dump()
async def live_location(loc):
 result=await fetch_weather(loc); b=normalize(loc,result); save(b,result['raw']); return b
async def live_weather(city): return await live_location(await geocode(city))
