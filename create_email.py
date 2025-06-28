import os
import icalendar
import requests
import calendar
from datetime import datetime, timezone

CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL")
CHURCH_ID = os.environ.get("CHURCH_ID")

if CHURCH_ID == None:
    raise Exception("Church ID is not defined")


def get_date_string(date):
    day = date.day
    month = calendar.month_name[date.month]
    year = date.year
    return f"{day} {month} {year}"


def get_time_string(date):
    minute = date.minute if date.minute >= 10 else f"0{date.minute}"
    return f"{date.hour}:{minute}"


class Event:
    def __init__(self, ical_data):
        self.title = ical_data.get("SUMMARY")
        self.start_time = ical_data.get("DTSTART").dt
        self.end_time = ical_data.get("DTEND").dt
        self.location = ical_data.get("LOCATION")
        self.description = ical_data.get("DESCRIPTION")

    def in_next_week(self):
        now = datetime.now(timezone.utc)
        return (self.start_time - now).days >= 0 and (self.start_time - now).days < 6

    def get_datetime_string(self):
        if (
            self.start_time.day == self.end_time.day
            and self.start_time.month == self.end_time.month
        ):
            return f"{get_date_string(self.start_time)}, {get_time_string(self.start_time)} - {get_time_string(self.end_time)}"
        else:
            return f"{get_date_string(self.start_time)} {get_time_string(self.start_time)} - {get_date_string(self.end_time)} {get_time_string(self.end_time)}"

    def format_for_email(self):
        formatted_event = f"<h3>{self.title}</h3>"
        formatted_event += (
            f"<p><b>{self.location}, {self.get_datetime_string()}</b></p>"
        )
        formatted_event += f"<p>{self.description}<p>"
        return formatted_event


def get_unique_future_events(events):
    duplicate_event_names = []
    current_unique_events = []
    for event in events:
        if event.title in duplicate_event_names:
            continue
        duplicate = False
        for i in range(len(current_unique_events)):
            event_to_compare = current_unique_events[i]
            if event_to_compare.title == event.title:
                current_unique_events.pop(i)
                duplicate_event_names.append(event.title)
                duplicate = True
                break
        if not duplicate:
            current_unique_events.append(event)
    return current_unique_events


def create_email_message():
    text = requests.get(
        f"https://www.achurchnearyou.com/church/{CHURCH_ID}/service-and-events/feed/"
    ).text

    calendar = icalendar.Calendar.from_ical(text)
    events = [Event(eventData) for eventData in calendar.events]
    email = "<p>Please see below for this week's events:</p>"
    email += f"<p>For full details of all future events, please see our website on <a href=https://www.achurchnearyou.com/church/{CHURCH_ID}/>A Church Near You</a>"
    for event in events:
        if event.in_next_week():
            email += event.format_for_email()
    email += f"<br/>If you have an event you would like to advertise, please contact the church at {CONTACT_EMAIL}"
    return email
