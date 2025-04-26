import icalendar
import requests

text = requests.get("https://www.achurchnearyou.com/church/18109/service-and-events/feed/").text

calendar = icalendar.Calendar.from_ical(text)

for event in calendar.events:
    print(event.get('SUMMARY'), '\n')
    print(f"{event.get('LOCATION')}, {event.get('DTSTART').dt} - {event.get('DTEND').dt}\n")
    print(event.get('DESCRIPTION'))
    print('--------------')