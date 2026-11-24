import os
from pathlib import Path
import httpx
from dotenv import load_dotenv
from src.weather_app.storage import locations,latest_for_location,_con
load_dotenv(Path(__file__).resolve().parents[1]/'.env')
def dispatch_if_new(location_id,bundle):
 token=os.getenv('TELEGRAM_BOT_TOKEN'); chat=os.getenv('TELEGRAM_CHAT_ID')
 if not token or not chat: return 0
 sent=0; db=_con()
 try:
  for a in bundle.get('alerts',[]):
   row=db.execute("SELECT 1 FROM alert_log WHERE location_id=? AND code=? AND datetime(sent_at)>=datetime('now','-12 hours')",(location_id,a['code'])).fetchone()
   if row: continue
   message=f"Weather alert · {bundle['location']['name']}\n{a['severity'].upper()} — {a['label']}\n{a['message']}"
   try:
    response=httpx.post(f'https://api.telegram.org/bot{token}/sendMessage',json={'chat_id':chat,'text':message},timeout=12); response.raise_for_status()
   except httpx.HTTPError as exc:
    print(f"Telegram delivery failed for {a['code']}: {exc}"); continue
   db.execute('INSERT INTO alert_log(location_id,code,sent_at) VALUES(?,?,datetime(\'now\'))',(location_id,a['code'])); sent+=1
  db.commit()
 finally: db.close()
 return sent
def dispatch_all():
 for loc in locations():
  b=latest_for_location(loc['id'])
  if b and b.get('provider')!='Built-in simulation': dispatch_if_new(loc['id'],b)
