from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUTPUT=ROOT/'outputs'; DATA=ROOT/'data'; DB=DATA/'weather.db'
OUTPUT.mkdir(exist_ok=True); DATA.mkdir(exist_ok=True)
THRESHOLDS={'heat_c':35.0,'heat_wave_c':40.0,'humidity_pct':85.0,'rain_probability_pct':60.0,'wind_ms':15.0,'aqi':100,'uv':8.0,'fog_visibility_m':1000.0}


