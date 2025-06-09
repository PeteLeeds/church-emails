import os
import icalendar
import requests
from datetime import datetime, timezone

CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL")

def create_email_message():
    text = requests.get(
        "https://www.achurchnearyou.com/church/18109/service-and-events/feed/"
    ).text

    calendar = icalendar.Calendar.from_ical(text)
    email = ""
    for event in calendar.events:
        start_time = event.get("DTSTART").dt
        now = datetime.now(timezone.utc)
        if (start_time - now).days > 7:
            continue
        email += f"{event.get('SUMMARY')}\n"
        email += f"{event.get('LOCATION')}, {start_time} - {event.get('DTEND').dt}\n\n"
        email += f"{event.get('DESCRIPTION')}\n"
        email += "--------------\n\n"
    email += f"If you have an event you would like to advertise, please contact the church at {CONTACT_EMAIL}"
    return email
