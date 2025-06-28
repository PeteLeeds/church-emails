import os
import icalendar
import requests
import calendar
from datetime import datetime, timezone

CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL")
CHURCH_ID = os.environ.get("CHURCH_ID")

if (CHURCH_ID == None):
    raise Exception('Church ID is not defined')


def get_date_string(date):
    day = date.day
    month = calendar.month_name[date.month]
    year = date.year
    return f'{day} {month} {year}'

def get_time_string(date):
    minute = date.minute if date.minute >= 10 else f'0{date.minute}'
    return f'{date.hour}:{minute}'

class Event:
    def __init__(self, icalData):
        self.icalData = icalData

    def in_next_week(self):
        start_time = self.icalData.get("DTSTART").dt
        now = datetime.now(timezone.utc)
        return (start_time - now).days >= 0 and (start_time - now).days < 6

    def get_datetime_string(self):
        startDate = self.icalData.get("DTSTART").dt
        endDate = self.icalData.get("DTEND").dt
        if startDate.day == endDate.day and startDate.month == endDate.month:
            return f"{get_date_string(startDate)}, {get_time_string(startDate)} - {get_time_string(endDate)}"
        else:
            return f"{get_date_string(startDate)} {get_time_string(startDate)} - {get_date_string(startDate)} {get_time_string(endDate)}"

    def format_for_email(self):
        formatted_event = f"<h3>{self.icalData.get('SUMMARY')}</h3>"
        formatted_event += f"<p><b>{self.icalData.get('LOCATION')}, {self.get_datetime_string()}</b></p>"
        formatted_event += f"<p>{self.icalData.get('DESCRIPTION')}<p>"
        return formatted_event


def get_unique_future_events(events):
    duplicate_event_names = []
    current_unique_events = []
    for eventData in events:
        name = eventData.get("SUMMARY")
        if name in duplicate_event_names:
            continue
        duplicate = False
        for i in range(len(current_unique_events)):
            event = current_unique_events[i]
            if event.get("SUMMARY") == name:
                current_unique_events.pop(i)
                duplicate_event_names.append(event.get("SUMMARY"))
                duplicate = True
                break
        if not duplicate:
            current_unique_events.append(eventData)
    for event in current_unique_events:
        print(event.get("SUMMARY"))
    return current_unique_events


def create_email_message():
    text = requests.get(
        f"https://www.achurchnearyou.com/church/{CHURCH_ID}/service-and-events/feed/"
    ).text

    calendar = icalendar.Calendar.from_ical(text)
    email = "<p>Please see below for this week's events:</p>"
    email += f"<p>For full details of all future events, please see our website on <a href=https://www.achurchnearyou.com/church/{CHURCH_ID}/>A Church Near You</a>"
    for eventData in calendar.events:
        event = Event(eventData)
        if event.in_next_week():
            email += event.format_for_email()
    email += f"<br/>If you have an event you would like to advertise, please contact the church at {CONTACT_EMAIL}"
    return email
