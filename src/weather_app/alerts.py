from .config import THRESHOLDS
def evaluate(current,daily,air=None,hourly=None,thresholds=None):
 t={**THRESHOLDS,**(thresholds or {})}; out=[]; hourly=hourly or []
 def add(code,label,severity,message): out.append({'code':code,'label':label,'severity':severity,'message':message})
 temp=current.get('temperature_2m')
 if temp is not None and temp>=t['heat_c']: add('heat','High temperature','high',f'{temp:.1f}°C: hydrate and limit strenuous outdoor activity.')
 tomorrow=daily.get('temperature_2m_max',[None,None]); tomorrow=tomorrow[1] if len(tomorrow)>1 else None
 if tomorrow is not None and tomorrow>=t['heat_wave_c']: add('heat_wave','Heatwave risk','critical',f'Tomorrow’s maximum may reach {tomorrow:.1f}°C. Avoid peak-hour exposure and follow local advisories.')
 humidity=current.get('relative_humidity_2m')
 if humidity is not None and humidity>=t['humidity_pct']: add('humidity','High humidity','moderate',f'Relative humidity is {humidity:.0f}%.')
 rain=daily.get('precipitation_probability_max',[None])[0]; amount=daily.get('precipitation_sum',[None])[0]; soon=[x.get('precipitation_probability') for x in hourly[:12] if x.get('precipitation_probability') is not None]
 if (rain is not None and rain>=t['rain_probability_pct']) or any(x>=t['rain_probability_pct'] for x in soon): add('rain','Rain likely','moderate',f'{(max(soon) if soon else rain):.0f}% chance in the near-term forecast; {amount or 0:.1f} mm expected today. Carry rain protection.')
 wind=daily.get('wind_max_ms',[None])[0]; gusts=[x.get('wind_gust_ms') for x in hourly[:24] if x.get('wind_gust_ms') is not None]
 peak=max([x for x in [wind,*gusts] if x is not None],default=None)
 if peak is not None and peak>=t['wind_ms']: add('wind','Strong wind','high',f'Peak forecast wind/gust reaches {peak:.1f} m/s ({peak*3.6:.0f} km/h). Secure loose outdoor items.')
 uv=daily.get('uv_index_max',[None])[0]
 if uv is not None and uv>=t['uv']: add('uv','High UV','moderate',f'UV index may reach {uv:.0f}; use sun protection outdoors.')
 codes=[x.get('weather_code') for x in hourly[:24] if x.get('weather_code') is not None]
 if any(x in (95,96,99) for x in codes): add('storm','Thunderstorm risk','high','Thunderstorms are present in the next 24-hour forecast. Review local advisories and avoid exposed areas.')
 visibility=[x.get('visibility') for x in hourly[:24] if x.get('visibility') is not None]
 if visibility and min(visibility)<t['fog_visibility_m']: add('fog','Low visibility / fog','moderate',f'Visibility may fall to {min(visibility)/1000:.1f} km. Allow extra travel time.')
 aqi=(air or {}).get('current',{}).get('european_aqi')
 if aqi is not None and aqi>=t['aqi']: add('aqi','Poor air quality','moderate',f'European AQI is {aqi:.0f}; reduce prolonged outdoor exertion.')
 return out

