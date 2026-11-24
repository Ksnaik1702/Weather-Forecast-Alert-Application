import sqlite3
from .config import DB
def migrate():
 if not DB.exists(): return
 con=sqlite3.connect(DB)
 snapshots={r[1] for r in con.execute('PRAGMA table_info(snapshots)').fetchall()}
 if snapshots and 'location_id' not in snapshots: con.execute('ALTER TABLE snapshots ADD COLUMN location_id INTEGER')
 hourly={r[1] for r in con.execute('PRAGMA table_info(weather_hourly)').fetchall()}
 if hourly and 'wind_ms' not in hourly:
  con.execute('ALTER TABLE weather_hourly ADD COLUMN wind_ms REAL')
  if 'wind_kmh' in hourly: con.execute('UPDATE weather_hourly SET wind_ms=wind_kmh/3.6 WHERE wind_ms IS NULL')
 if hourly and 'wind_gust_ms' not in hourly:
  con.execute('ALTER TABLE weather_hourly ADD COLUMN wind_gust_ms REAL')
  if 'wind_gust_kmh' in hourly: con.execute('UPDATE weather_hourly SET wind_gust_ms=wind_gust_kmh/3.6 WHERE wind_gust_ms IS NULL')
 daily={r[1] for r in con.execute('PRAGMA table_info(weather_daily)').fetchall()}
 if daily and 'wind_max_ms' not in daily:
  con.execute('ALTER TABLE weather_daily ADD COLUMN wind_max_ms REAL')
  if 'wind_max_kmh' in daily: con.execute('UPDATE weather_daily SET wind_max_ms=wind_max_kmh/3.6 WHERE wind_max_ms IS NULL')
 con.commit(); con.close()
