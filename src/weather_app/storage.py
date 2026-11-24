import csv,json,sqlite3
from datetime import datetime,timezone
from .config import DB,OUTPUT
from .migration import migrate
def _con():
 migrate(); c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON')
 c.executescript('''
 CREATE TABLE IF NOT EXISTS locations(id INTEGER PRIMARY KEY,name TEXT NOT NULL,lat REAL NOT NULL,lon REAL NOT NULL,tz TEXT NOT NULL,UNIQUE(lat,lon));
 CREATE TABLE IF NOT EXISTS snapshots(id INTEGER PRIMARY KEY,location_id INTEGER,city TEXT,fetched_at TEXT,payload TEXT NOT NULL,FOREIGN KEY(location_id) REFERENCES locations(id));
 CREATE TABLE IF NOT EXISTS weather_raw(id INTEGER PRIMARY KEY,location_id INTEGER NOT NULL,fetched_at TEXT NOT NULL,scope TEXT NOT NULL,provider TEXT NOT NULL,payload TEXT NOT NULL,FOREIGN KEY(location_id) REFERENCES locations(id));
 CREATE TABLE IF NOT EXISTS weather_hourly(location_id INTEGER NOT NULL,ts TEXT NOT NULL,temp_c REAL,feels_c REAL,humidity REAL,wind_ms REAL,wind_gust_ms REAL,precip_mm REAL,precip_prob REAL,cloud_pct REAL,uv REAL,pressure_hpa REAL,visibility_km REAL,weather_code INTEGER,PRIMARY KEY(location_id,ts),FOREIGN KEY(location_id) REFERENCES locations(id));
 CREATE TABLE IF NOT EXISTS weather_daily(location_id INTEGER NOT NULL,date TEXT NOT NULL,tmax_c REAL,tmin_c REAL,rain_mm REAL,rain_prob REAL,wind_max_ms REAL,uv_max REAL,sunrise TEXT,sunset TEXT,weather_code INTEGER,PRIMARY KEY(location_id,date),FOREIGN KEY(location_id) REFERENCES locations(id));
 CREATE TABLE IF NOT EXISTS alert_log(id INTEGER PRIMARY KEY,location_id INTEGER NOT NULL,code TEXT NOT NULL,sent_at TEXT NOT NULL,UNIQUE(location_id,code,sent_at),FOREIGN KEY(location_id) REFERENCES locations(id));
 '''); return c
def save(bundle,raw_payload=None):
 loc=bundle['location']; con=_con()
 try:
  con.execute('INSERT INTO locations(name,lat,lon,tz) VALUES(?,?,?,?) ON CONFLICT(lat,lon) DO UPDATE SET name=excluded.name,tz=excluded.tz',(loc['name'],loc['latitude'],loc['longitude'],loc.get('timezone','auto')))
  lid=con.execute('SELECT id FROM locations WHERE lat=? AND lon=?',(loc['latitude'],loc['longitude'])).fetchone()['id']
  con.execute('INSERT INTO snapshots(location_id,city,fetched_at,payload) VALUES(?,?,?,?)',(lid,loc['name'],bundle['fetched_at'],json.dumps(bundle)))
  if raw_payload is not None: con.execute('INSERT INTO weather_raw(location_id,fetched_at,scope,provider,payload) VALUES(?,?,?,?,?)',(lid,bundle['fetched_at'],'full',bundle['provider'],json.dumps(raw_payload)))
  for h in bundle.get('hourly',[]):
   con.execute('''INSERT OR REPLACE INTO weather_hourly(location_id,ts,temp_c,feels_c,humidity,wind_ms,wind_gust_ms,precip_mm,precip_prob,cloud_pct,uv,pressure_hpa,visibility_km,weather_code) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(lid,h.get('time'),h.get('temperature_2m'),h.get('apparent_temperature'),h.get('relative_humidity_2m'),h.get('wind_speed_ms'),h.get('wind_gust_ms'),h.get('precipitation'),h.get('precipitation_probability'),h.get('cloud_cover'),h.get('uv_index'),h.get('pressure_msl'),(h.get('visibility')/1000 if h.get('visibility') is not None else None),h.get('weather_code')))
  for d in bundle.get('daily',[]):
   con.execute('''INSERT OR REPLACE INTO weather_daily(location_id,date,tmax_c,tmin_c,rain_mm,rain_prob,wind_max_ms,uv_max,sunrise,sunset,weather_code) VALUES(?,?,?,?,?,?,?,?,?,?,?)''',(lid,d.get('time'),d.get('temperature_2m_max'),d.get('temperature_2m_min'),d.get('precipitation_sum'),d.get('precipitation_probability_max'),d.get('wind_max_ms'),d.get('uv_index_max'),d.get('sunrise'),d.get('sunset'),d.get('weather_code')))
  con.commit(); return lid
 finally: con.close()
def history(limit=25):
 c=_con()
 try: return [json.loads(x['payload']) for x in c.execute('SELECT payload FROM snapshots ORDER BY id DESC LIMIT ?',(limit,)).fetchall()]
 finally: c.close()
def locations():
 c=_con()
 try: return [dict(x) for x in c.execute('SELECT id,name,lat AS latitude,lon AS longitude,tz AS timezone FROM locations ORDER BY name').fetchall()]
 finally: c.close()
def latest_for_location(location_id):
 c=_con()
 try:
  row=c.execute('SELECT payload FROM snapshots WHERE location_id=? ORDER BY id DESC LIMIT 1',(location_id,)).fetchone(); return json.loads(row['payload']) if row else None
 finally: c.close()
def export_csv(bundle):
 path=OUTPUT/f"forecast_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.csv"; fields=['date','temp_max_c','temp_min_c','rain_probability_pct','rain_mm','wind_max_ms','uv_max','weather_code']
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
  for d in bundle['daily']: w.writerow({'date':d.get('time'),'temp_max_c':d.get('temperature_2m_max'),'temp_min_c':d.get('temperature_2m_min'),'rain_probability_pct':d.get('precipitation_probability_max'),'rain_mm':d.get('precipitation_sum'),'wind_max_ms':d.get('wind_max_ms'),'uv_max':d.get('uv_index_max'),'weather_code':d.get('weather_code')})
 return str(path)
