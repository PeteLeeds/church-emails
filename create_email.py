import os
import icalendar
import requests
import calendar
from datetime import datetime, timezone

CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL")
CHURCH_ID = os.environ.get("CHURCH_ID")


def in_next_week(event):
    start_time = event.get("DTSTART").dt
    now = datetime.now(timezone.utc)
    return (start_time - now).days > 0 and (start_time - now).days < 6

def get_date_string(date):
    day = date.day
    month = calendar.month_name[date.month]
    year = date.year
    return f'{day} {month} {year}'

def get_time_string(date):
    minute = date.minute if date.minute >= 10 else f'0{date.minute}'
    return f'{date.hour}:{minute}'

def get_datetime_string(startDate, endDate):
    if (startDate.day == endDate.day and startDate.month == endDate.month):
        return f'{get_date_string(startDate)}, {get_time_string(startDate)} - {get_time_string(endDate)}'
    else:
        return f'{get_date_string(startDate)} {get_time_string(startDate)} - {get_date_string(startDate)} {get_time_string(endDate)}'

def format_event_for_email(event):
    formatted_event = f"<h3>{event.get('SUMMARY')}</h3>"
    formatted_event += f"<p><b>{event.get('LOCATION')}, {get_datetime_string(event.get('DTSTART').dt, event.get('DTEND').dt)}</b></p>"
    formatted_event += f"<p>{event.get('DESCRIPTION')}<p>"
    return formatted_event


def create_email_message():
    text = requests.get(
        f"https://www.achurchnearyou.com/church/{CHURCH_ID}/service-and-events/feed/"
    ).text

    calendar = icalendar.Calendar.from_ical(text)
    email = "<p>Please see below for this week's events:</p>"
    email += f"<p>For full details of all future events, please see our website on <a href=https://www.achurchnearyou.com/church/{CHURCH_ID}/>A Church Near You</a>"
    for event in calendar.events:
        if in_next_week(event):
            email += format_event_for_email(event)
    email += f"<br/>If you have an event you would like to advertise, please contact the church at {CONTACT_EMAIL}"
    return email
