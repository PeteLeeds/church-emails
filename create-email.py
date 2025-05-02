import icalendar
import requests
from datetime import datetime, timezone

text = requests.get("https://www.achurchnearyou.com/church/18109/service-and-events/feed/").text

calendar = icalendar.Calendar.from_ical(text)

for event in calendar.events:
    start_time = event.get('DTSTART').dt
    now = datetime.now(timezone.utc)
    if ((start_time - now).days > 7):
        continue
    print(event.get('SUMMARY'), '\n')
    print(f"{event.get('LOCATION')}, {start_time} - {event.get('DTEND').dt}\n")
    print(event.get('DESCRIPTION'))
    print('--------------')