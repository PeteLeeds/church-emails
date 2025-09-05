import os
import icalendar
import requests
from datetime import datetime, timezone
from typing import List
from icalendar import Event as IcalEvent
from date_string import get_date_string

CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL")
CHURCH_ID = os.environ.get("CHURCH_ID")

if CHURCH_ID == None:
    raise Exception("Church ID is not defined")


def get_time_string(date: datetime) -> str:
    minute = date.minute if date.minute >= 10 else f"0{date.minute}"
    return f"{date.hour}:{minute}"


class Event:
    def __init__(self, ical_data: IcalEvent) -> None:
        self.title = ical_data.get("SUMMARY")
        self.dates = [
            {
                "start_time": ical_data.get("DTSTART").dt,
                "end_time": ical_data.get("DTEND").dt,
            }
        ]
        self.location = ical_data.get("LOCATION")
        self.description = ical_data.get("DESCRIPTION")

    def in_next_week(self) -> bool:
        now = datetime.now(timezone.utc)
        start_time = self.dates[0]["start_time"]
        return (start_time - now).days >= 0 and (start_time - now).days <= 7

    def in_mid_future(self) -> bool:
        now = datetime.now(timezone.utc)
        start_time = self.dates[0]["start_time"]
        return (start_time - now).days >= 0 and (start_time - now).days < 90

    def merge_event(self, new_event: "Event") -> None:
        self.dates += new_event.dates

    def get_datetime_string(self) -> str:
        if len(self.dates) == 1:
            start_time: datetime = self.dates[0]["start_time"]
            end_time: datetime = self.dates[0]["end_time"]
            # Option 1: One date
            if start_time.day == end_time.day and start_time.month == end_time.month:
                return f"{get_date_string(start_time)}, {get_time_string(start_time)} - {get_time_string(end_time)}"
            # Option 2: Multiple dates, one continuous event
            return f"{get_date_string(start_time)} {get_time_string(start_time)} - {get_date_string(end_time)} {get_time_string(end_time)}"
        # Option 3: Multiple events
        time_map: dict[str, list] = {}
        for date in self.dates:
            date_string = get_date_string(date["start_time"])
            time_string = f"{get_time_string(date['start_time'])} - {get_time_string(date['end_time'])}"
            if time_string in time_map:
                time_map[time_string].append(date_string)
            else:
                time_map[time_string] = [date_string]
        times = list(time_map.keys())
        datetime_string = ""
        for key in times:
            time_string = ""
            for date in time_map[key]:
                time_string += f"{date}, "
            time_string = f"{time_string[:-2]} at {key}"
            datetime_string += time_string
        return datetime_string

    def format_for_email(self) -> str:
        formatted_event = f"<h3>{self.title}</h3>"
        formatted_event += (
            f"<p><b>{self.location}, {self.get_datetime_string()}</b></p>"
        )
        formatted_event += f"<p>{self.description}<p>"
        return formatted_event


def get_this_weeks_events(events: List[Event]) -> List[Event]:
    events_this_week: List[Event] = []
    for event in events:
        if not event.in_next_week():
            continue
        new_event = True
        for event_to_compare in events_this_week:
            if event_to_compare.title == event.title:
                event_to_compare.merge_event(event)
                new_event = False
                continue
        if new_event:
            events_this_week.append(event)
    return events_this_week


def get_unique_future_events(
    events: List[Event], this_weeks_events: List[Event]
) -> List[Event]:
    unique_events: List[Event] = []
    this_weeks_event_titles = [event.title for event in this_weeks_events]
    for event in events:
        if not event.in_mid_future():
            continue
        if event.title in this_weeks_event_titles:
            continue
        new_event = True
        for event_to_compare in unique_events:
            if event_to_compare.title == event.title:
                event_to_compare.merge_event(event)
                new_event = False
                continue
        if new_event:
            unique_events.append(event)
    return unique_events


def create_event_email() -> str:
    text = requests.get(
        f"https://www.achurchnearyou.com/church/{CHURCH_ID}/service-and-events/feed/"
    ).text

    calendar = icalendar.Calendar.from_ical(text)
    events = [Event(eventData) for eventData in calendar.events]
    email = ""
    email += "<h2>This Week's Events</h2>"
    email += f"<p>For full details of all events, please see our website on <a href=https://www.achurchnearyou.com/church/{CHURCH_ID}/>A Church Near You.</a>"
    this_weeks_events = get_this_weeks_events(events)
    for event in this_weeks_events:
        email += event.format_for_email()
    email += "<h2>Future Events</h2>"
    for event in get_unique_future_events(events, this_weeks_events):
        email += event.format_for_email()
    email += f"<br/>If you have an event you would like to advertise, please contact the church at {CONTACT_EMAIL}"
    return email
