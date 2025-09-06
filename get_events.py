import os
import icalendar
import requests
from sections import get_sections, populate_section_events
from events import Event, get_this_weeks_events, get_unique_future_events

CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL")
CHURCH_ID = os.environ.get("CHURCH_ID")


def create_event_email() -> str:
    if CHURCH_ID == None:
        raise Exception("Church ID is not defined")
    text = requests.get(
        f"https://www.achurchnearyou.com/church/{CHURCH_ID}/service-and-events/feed/"
    ).text

    calendar = icalendar.Calendar.from_ical(text)
    events = [Event(eventData) for eventData in calendar.events]
    email = ""
    email += "<h1>This Week's Events</h1>"
    email += f"<p>For full details of all events, please see our website on <a href=https://www.achurchnearyou.com/church/{CHURCH_ID}/>A Church Near You.</a>"
    this_weeks_events = get_this_weeks_events(events)
    sections = get_sections()
    populate_section_events(sections, this_weeks_events)
    for section in sections:
        email += section.create_section_email()
    email += "<h1>Future Events</h1>"
    for event in get_unique_future_events(events, this_weeks_events):
        email += event.format_for_email()
    email += f"<br/>If you have an event you would like to advertise, please contact the church at {CONTACT_EMAIL}"
    return email
