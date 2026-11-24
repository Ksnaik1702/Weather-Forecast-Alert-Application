from .demo import simulated_weather
from .storage import save,export_csv
def main():
 city=input('City for offline simulation [New Delhi]: ').strip() or 'New Delhi'; b=simulated_weather(city); save(b); report=export_csv(b); c=b['current']
 print(f"\n{b['location']['name']} — {b['provider']}"); print(f"Current: {c['temperature_2m']}°C, humidity {c['relative_humidity_2m']}%, wind {c['wind_speed_ms']*3.6:.1f} km/h")
 print('\nAlerts:')
 for a in b['alerts']: print(f" [{a['severity'].upper()}] {a['label']}: {a['message']}")
 print(f'\nSeven-day forecast saved to: {report}')
if __name__=='__main__': main()
