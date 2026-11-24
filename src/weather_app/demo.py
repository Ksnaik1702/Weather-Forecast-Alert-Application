from datetime import date,timedelta,datetime,timezone
from .alerts import evaluate
def simulated_weather(city='New Delhi'):
 today=date.today(); daily=[]
 for i in range(7): daily.append({'time':(today+timedelta(days=i)).isoformat(),'weather_code':95 if i==0 else 2,'temperature_2m_max':38-i,'temperature_2m_min':27,'precipitation_probability_max':75 if i==0 else 20,'precipitation_sum':8.4 if i==0 else 0,'wind_max_ms':16.1 if i==0 else 7+i*.3,'uv_index_max':9 if i==0 else 5,'sunrise':'06:00','sunset':'18:00'})
 now=datetime.now(); current={'time':now.isoformat(timespec='minutes'),'temperature_2m':37.2,'relative_humidity_2m':88,'apparent_temperature':43.0,'precipitation':0.0,'weather_code':95,'wind_speed_ms':5.0,'is_day':1}
 hourly=[{'time':(now+timedelta(hours=i)).isoformat(timespec='minutes'),'temperature_2m':round(37.2-i*.25,1),'apparent_temperature':42-i*.2,'precipitation_probability':75 if i<5 else 15,'precipitation':1.2 if i<5 else 0,'relative_humidity_2m':88,'wind_speed_ms':5.0,'wind_gust_ms':16.1 if i<4 else 5.6,'cloud_cover':80,'uv_index':9 if i<5 else 4,'pressure_msl':1005,'visibility':800 if i<4 else 9000,'weather_code':95 if i<3 else 3} for i in range(48)]
 b={'location':{'name':city,'latitude':28.6139,'longitude':77.209,'timezone':'Asia/Kolkata'},'provider':'Built-in simulation','fetched_at':datetime.now(timezone.utc).isoformat(),'units':{'temperature':'°C','precipitation':'mm','wind':'m/s','visibility':'m'},'current':current,'hourly':hourly,'daily':daily,'air_quality':{'current':{'european_aqi':132,'pm2_5':38,'pm10':62}}}
 b['alerts']=evaluate(current,{k:[d[k] for d in daily] for k in daily[0]},b['air_quality'],hourly); return b
