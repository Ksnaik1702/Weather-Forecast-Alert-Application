import asyncio
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from src.weather_app.service import live_weather
from src.weather_app.demo import simulated_weather
from src.weather_app.storage import export_csv
from src.weather_app.provider import WeatherProviderError

st.set_page_config(page_title='Weather • Fieldnote', page_icon='🌿', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{--forest:#12372a;--leaf:#2d6a4f;--moss:#52796f;--lime:#d8f3a5;--paper:#f5f7f2;--ink:#1b2b24;--muted:#718078;--line:#e2e9e1;--white:#fff}
.stApp{background:var(--paper);color:var(--ink);font-family:'DM Sans',sans-serif}
[data-testid="stHeader"]{background:rgba(245,247,242,.85)}
[data-testid="stSidebar"]{background:var(--forest)}
[data-testid="stSidebar"] *{color:#edf5ed!important}
[data-testid="stSidebar"] input{color:#1b2b24!important;background:#fff!important;border-radius:10px!important}
[data-testid="stSidebar"] [data-baseweb="radio"] label{background:rgba(255,255,255,.06);padding:9px 12px;border-radius:10px;margin:4px 0}
[data-testid="stSidebar"] [data-testid="stButton"] button,[data-testid="stSidebar"] [data-testid="stButton"] button *{background-color:#d8f3a5!important;color:#12372a!important;-webkit-text-fill-color:#12372a!important;border:0!important;border-radius:10px!important;font-weight:800!important}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover{background-color:#c5e894!important;box-shadow:0 5px 14px rgba(0,0,0,.18)!important}
.block-container{max-width:1450px;padding-top:2.5rem;padding-bottom:3rem}
h1,h2,h3{font-family:'Manrope',sans-serif!important;letter-spacing:-.035em;color:var(--forest)!important}
.hero{background:linear-gradient(118deg,#12372a 0%,#245b42 68%,#43835b 100%);padding:30px 34px;border-radius:22px;color:#f2f8eb;margin-bottom:24px;box-shadow:0 14px 34px rgba(18,55,42,.12);position:relative;overflow:hidden}
.hero:after{content:' ';position:absolute;width:230px;height:230px;border:1px solid rgba(216,243,165,.22);border-radius:50%;right:-38px;top:-94px;box-shadow:0 0 0 28px rgba(216,243,165,.06),0 0 0 58px rgba(216,243,165,.04)}
.hero-kicker{font-size:12px;letter-spacing:.15em;text-transform:uppercase;color:#d8f3a5;font-weight:700;margin-bottom:10px}.hero h1{color:#fff!important;font-size:clamp(30px,4vw,48px)!important;margin:0!important}.hero p{color:#dce9de;font-size:15px;margin:9px 0 0;max-width:620px}
.section-label{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#668073;font-weight:700;margin:22px 0 10px}
.kpi{height:142px;background:#fff;border:1px solid var(--line);border-radius:18px;padding:18px 20px;box-shadow:0 5px 16px rgba(20,50,35,.035);position:relative;overflow:hidden}
.kpi:before{content:'';position:absolute;top:0;left:0;right:0;height:4px;background:var(--leaf)}.kpi-label{font-size:13px;color:var(--muted);font-weight:600}.kpi-value{font-family:'Manrope',sans-serif;font-size:33px;line-height:1.25;font-weight:800;color:var(--forest);margin-top:13px}.kpi-note{font-size:12px;color:#6e8377;margin-top:4px}.kpi-icon{float:right;font-size:20px;background:#edf5e9;border-radius:12px;padding:6px 9px}
.alert-card{background:#fff;border:1px solid #e8e6d8;border-left:5px solid #d59a37;border-radius:12px;padding:13px 16px;margin:9px 0;color:#36473c;box-shadow:0 3px 12px rgba(30,45,35,.03)}.alert-card.high{border-left-color:#bf5b46}.alert-card.moderate{border-left-color:#d59a37}.alert-card.info{border-left-color:#4b8c70}.alert-title{font-weight:700;color:#243c30}.alert-copy{font-size:13px;color:#66746b;margin-top:4px}
[data-testid="stVerticalBlockBorderWrapper"]{background:white!important;border:1px solid var(--line)!important;border-radius:18px!important;padding:18px 20px!important}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px}
[data-testid="stAlert"]{border-radius:12px}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:14px;overflow:hidden}
.stButton>button,.stDownloadButton>button{border-radius:10px!important;font-weight:700!important;min-height:42px}
footer{visibility:hidden}
</style>''', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('### 🌿 FIELDNOTE')
    st.caption('WEATHER INTELLIGENCE')
    st.divider()
    city = st.text_input('LOCATION', 'New Delhi', help='Enter a city or town name.')
    mode = st.radio('FORECAST SOURCE', ['Simulation (offline)', 'Live forecast'], help='Simulation demonstrates alerts without internet.')
    if mode.startswith('Simulation'):
        st.caption('Offline sample conditions · not a live local forecast')
    else:
        st.caption('Live conditions retrieved for the selected city')
    fetch = st.button('Get forecast', type='primary', width='stretch')
    st.divider()
    st.markdown('**Alert thresholds**')
    st.caption('Heat ≥ 35°C · Humidity ≥ 85%\nRain chance ≥ 60% · Wind ≥ 50 km/h · AQI ≥ 100')
    st.markdown('<div style="font-size:11px;color:#c7dccb;margin-top:26px">OPEN-METEO · LOCAL REPORTS</div>', unsafe_allow_html=True)

if 'bundle' not in st.session_state: st.session_state.bundle = simulated_weather()
if fetch:
    try:
        with st.spinner('Reading the forecast…'):
            st.session_state.bundle = simulated_weather(city) if mode.startswith('Simulation') else asyncio.run(live_weather(city))
        st.session_state.csv_path = None
    except WeatherProviderError as exc:
        st.session_state.bundle = None
        st.error(f'Could not load a forecast for {city}: {exc}')
        st.stop()

b = st.session_state.bundle
if b is None:
    st.info('Enter a city and select Get forecast to load weather data.')
    st.stop()
c = b['current']
daily = pd.DataFrame(b['daily'])
hourly = pd.DataFrame(b['hourly'])
location = b['location']
place = location['name']
source = b['provider']

st.markdown(f'''<div class="hero"><div class="hero-kicker">LOCAL WEATHER BRIEF · {source.upper()}</div><h1>{place}</h1><p>Forecast signals and practical alerts to help you plan the day with confidence.</p></div>''', unsafe_allow_html=True)
st.markdown('<div class="section-label">Right now</div>', unsafe_allow_html=True)

def kpi(label, value, note, icon):
    st.markdown(f'<div class="kpi"><span class="kpi-icon">{icon}</span><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)
cols = st.columns(4, gap='medium')
with cols[0]: kpi('Temperature', f"{c.get('temperature_2m','—')}°", f"Feels like {c.get('apparent_temperature','—')}°C", '☀️')
with cols[1]: kpi('Humidity', f"{c.get('relative_humidity_2m','—')}%", 'Relative humidity', '◌')
with cols[2]:
    wind_ms = c.get('wind_speed_ms')
    if wind_ms is not None:
        wind_display = f'{wind_ms*3.6:.1f}'
        wind_note = 'km/h · stored in m/s'
    else:
        wind_display = str(c.get('wind_speed_10m','—'))
        wind_note = 'km/h · saved earlier'
    kpi('Wind speed', wind_display, wind_note, '↗')
with cols[3]: kpi('Rain chance', f"{daily.iloc[0].get('precipitation_probability_max',0)}%", f"{daily.iloc[0].get('precipitation_sum',0)} mm expected today", '☂')

st.markdown('<div class="section-label">Weather watch</div>', unsafe_allow_html=True)
if b['alerts']:
    alert_cols = st.columns(2, gap='small')
    for i, alert in enumerate(b['alerts']):
        with alert_cols[i % 2]:
            st.markdown(f'<div class="alert-card {alert["severity"]}"><div class="alert-title">{alert["severity"].upper()} &nbsp;·&nbsp; {alert["label"]}</div><div class="alert-copy">{alert["message"]}</div></div>', unsafe_allow_html=True)
else:
    st.success('No configured risk thresholds were crossed for this forecast.')

st.markdown('<div class="section-label">Plan ahead</div>', unsafe_allow_html=True)
left, right = st.columns([1.2, .8], gap='medium')
with left:
    with st.container(border=True):
        st.markdown('### Temperature trend')
        st.caption('Next 24 hours · local forecast time · °C')
        fig, ax = plt.subplots(figsize=(8, 3.2)); fig.patch.set_facecolor('#ffffff'); ax.set_facecolor('#ffffff')
        times = pd.to_datetime(hourly['time'].head(24)); temps = hourly['temperature_2m'].head(24)
        ax.plot(times, temps, color='#2d6a4f', linewidth=2.8, marker='o', markersize=3.5)
        ax.fill_between(times, temps, min(temps)-2, color='#74a989', alpha=.13)
        ax.spines[['top','right','left']].set_visible(False); ax.spines['bottom'].set_color('#dfe8df'); ax.grid(axis='y',color='#e9efe9',linewidth=.8); ax.tick_params(colors='#77857c',labelsize=9); ax.set_ylabel('°C',color='#627267'); fig.tight_layout(pad=1)
        st.pyplot(fig, width='stretch'); plt.close(fig)
with right:
    with st.container(border=True):
        st.markdown('### Rain outlook')
        st.caption('Daily expected rainfall · next 7 days · mm')
        fig, ax = plt.subplots(figsize=(6, 3.2)); fig.patch.set_facecolor('#ffffff'); ax.set_facecolor('#ffffff')
        days = pd.to_datetime(daily['time']).dt.strftime('%a')
        vals = daily['precipitation_sum'].fillna(0)
        ax.bar(days, vals, color='#78a987',width=.58,edgecolor='none'); ax.spines[['top','right','left']].set_visible(False); ax.spines['bottom'].set_color('#dfe8df'); ax.grid(axis='y',color='#e9efe9',linewidth=.8); ax.set_axisbelow(True); ax.tick_params(colors='#77857c',labelsize=9); ax.set_ylabel('mm',color='#627267'); fig.tight_layout(pad=1)
        st.pyplot(fig, width='stretch'); plt.close(fig)

with st.container(border=True):
    st.markdown('### Forecast map')
    st.caption(f"{place} · {location['latitude']:.3f}°, {location['longitude']:.3f}° · {location.get('timezone','local time')}")
    weather_map = folium.Map(location=[location['latitude'],location['longitude']],zoom_start=9,tiles='OpenStreetMap',control_scale=True,scrollWheelZoom=False)
    folium.CircleMarker(location=[location['latitude'],location['longitude']],radius=10,color='#1f513b',weight=3,fill=True,fill_color='#8bcf9b',fill_opacity=.95,tooltip=place).add_to(weather_map)
    st_folium(weather_map,height=430,use_container_width=True,returned_objects=[])

with st.container(border=True):
    st.markdown('### 7-day forecast')
    view = daily.rename(columns={'time':'Date','temperature_2m_max':'High °C','temperature_2m_min':'Low °C','precipitation_probability_max':'Rain chance %','precipitation_sum':'Rain mm'})
    view['Wind max km/h'] = (daily['wind_max_ms'] * 3.6).round(0) if 'wind_max_ms' in daily else daily.get('wind_speed_10m_max', pd.Series([None]*len(daily)))
    wanted = ['Date','High °C','Low °C','Rain chance %','Rain mm','Wind max km/h']
    st.dataframe(view[wanted], width='stretch', hide_index=True)

footer_col, report_col = st.columns([1,1])
with footer_col:
    st.caption(f"Updated {b['fetched_at']} · Source: {source} · Forecast times follow the location timezone.")
with report_col:
    csv_daily = daily.copy()
    if 'wind_max_ms' in csv_daily:
        csv_daily['wind_max_kmh'] = (csv_daily['wind_max_ms'] * 3.6).round(1)
    else:
        csv_daily['wind_max_kmh'] = csv_daily.get('wind_speed_10m_max', pd.Series([None]*len(csv_daily)))
    csv_columns = ['time','temperature_2m_max','temperature_2m_min','precipitation_probability_max','precipitation_sum','wind_max_kmh']
    csv = csv_daily[csv_columns].to_csv(index=False).encode('utf-8')
    st.download_button('↓  Download 7-day CSV', csv, file_name='weather_forecast.csv', mime='text/csv', width='stretch')



