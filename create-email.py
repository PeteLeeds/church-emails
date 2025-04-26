import icalendar
import requests

text = requests.get("https://www.achurchnearyou.com/church/18109/service-and-events/feed/").text

calendar = icalendar.Calendar.from_ical(text)
print(calendar.events[0])