import unittest
from src.weather_app.alerts import evaluate
from src.weather_app.service import normalize
class AlertRuleChecks(unittest.TestCase):
 def test_heat_humidity_and_rain_rules(self):
  daily={'precipitation_probability_max':[80],'precipitation_sum':[5],'wind_max_ms':[5],'uv_index_max':[3]}
  codes={a['code'] for a in evaluate({'temperature_2m':37,'relative_humidity_2m':90},daily,hourly=[{'precipitation_probability':70}])}
  self.assertTrue({'heat','humidity','rain'} <= codes)
 def test_wind_uv_storm_and_fog_rules(self):
  daily={'precipitation_probability_max':[10],'precipitation_sum':[0],'wind_max_ms':[15.3],'uv_index_max':[9]}
  codes={a['code'] for a in evaluate({'temperature_2m':20,'relative_humidity_2m':50},daily,hourly=[{'weather_code':95,'wind_gust_ms':16.1,'visibility':500}])}
  self.assertTrue({'wind','uv','storm','fog'} <= codes)
 def test_next_day_heatwave_alert(self):
  daily={'temperature_2m_max':[35,41],'precipitation_probability_max':[10,5],'precipitation_sum':[0,0],'wind_max_ms':[5,5],'uv_index_max':[4,4]}
  codes={a['code'] for a in evaluate({'temperature_2m':30},daily)}
  self.assertIn('heat_wave',codes)
 def test_missing_values_are_skipped(self):
  daily={'precipitation_probability_max':[None],'precipitation_sum':[None],'wind_max_ms':[None],'uv_index_max':[None]}
  self.assertEqual([],evaluate({},daily))
 def test_normalizer_sorts_and_deduplicates_hours_in_meters_per_second(self):
  t1='2026-11-24T10:00'; t2='2026-11-24T11:00'
  raw={'current':{'time':t1,'temperature_2m':20,'wind_speed_10m':4},'hourly':{'time':[t2,t1,t2],'temperature_2m':[22,20,23],'wind_speed_10m':[5,4,6],'wind_gusts_10m':[7,6,8]},'daily':{'time':['2026-11-24'],'temperature_2m_max':[24],'temperature_2m_min':[15],'precipitation_probability_max':[10],'precipitation_sum':[0],'wind_speed_10m_max':[8],'uv_index_max':[4]}}
  bundle=normalize({'name':'Pune','latitude':18.52,'longitude':73.85,'timezone':'Asia/Kolkata'},{'raw':raw,'air_quality':None,'fetched_at':'2026-11-24T00:00:00+00:00'})
  self.assertEqual([t1,t2],[x['time'] for x in bundle['hourly']]); self.assertEqual(23,bundle['hourly'][1]['temperature_2m']); self.assertEqual(4,bundle['current']['wind_speed_ms']); self.assertEqual(8,bundle['daily'][0]['wind_max_ms'])
if __name__=='__main__': unittest.main()
