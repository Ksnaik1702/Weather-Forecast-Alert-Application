import time
from datetime import datetime,timezone,timedelta
from src.weather_app.storage import locations,latest_for_location
from src.weather_app.service import live_location
from src.weather_app.provider import WeatherProviderError
async def _refresh():
 for loc in locations():
  previous=latest_for_location(loc['id'])
  if previous and previous.get('provider')=='Built-in simulation': continue
  try:
   await live_location({'name':loc['name'],'latitude':loc['latitude'],'longitude':loc['longitude'],'timezone':loc['timezone']}); print(f"Refreshed {loc['name']}")
  except WeatherProviderError as exc: print(f"Could not refresh {loc['name']}: {exc}")
def refresh_all():
 import asyncio
 asyncio.run(_refresh())
def run_scheduler():
 import os
 from .notify import dispatch_all
 refresh_hours=max(1,int(os.getenv('WEATHER_REFRESH_HOURS','2'))); alert_minutes=max(5,int(os.getenv('WEATHER_ALERT_MINUTES','30')))
 refresh_due=datetime.now(timezone.utc); alert_due=refresh_due
 print(f'Scheduler active: refresh every {refresh_hours}h; check alerts every {alert_minutes}m. Press Ctrl+C to stop.')
 while True:
  now=datetime.now(timezone.utc)
  if now>=refresh_due: refresh_all(); refresh_due=now+timedelta(hours=refresh_hours)
  if now>=alert_due: dispatch_all(); alert_due=now+timedelta(minutes=alert_minutes)
  time.sleep(30)
if __name__=='__main__': run_scheduler()
