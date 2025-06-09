import os
import icalendar
import requests
from datetime import datetime, timezone

CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL")
CHURCH_ID = os.environ.get("CHURCH_ID")

def create_email_message():
    text = requests.get(
        f"https://www.achurchnearyou.com/church/{CHURCH_ID}/service-and-events/feed/"
    ).text

    calendar = icalendar.Calendar.from_ical(text)
    email = ""
    for event in calendar.events:
        start_time = event.get("DTSTART").dt
        now = datetime.now(timezone.utc)
        if (start_time - now).days > 7:
            continue
        email += f"<h3>{event.get('SUMMARY')}</h3>"
        email += f"<p><b>{event.get('LOCATION')}, {start_time} - {event.get('DTEND').dt}</b></p>"
        email += f"<p>{event.get('DESCRIPTION')}<p>"
    email += f"<br/>If you have an event you would like to advertise, please contact the church at {CONTACT_EMAIL}"
    return email
