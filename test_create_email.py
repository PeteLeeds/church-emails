from icalendar import Event
from freezegun import freeze_time
import datetime as dt

# import zoneinfo
import unittest
import create_email
from create_email import (
    get_date_string,
    get_time_string,
    get_this_weeks_events,
    get_unique_future_events,
)


def create_ical_event(
    summary, description, location, dtstart=None, dtend=None
) -> Event:
    event = Event()
    event.add("summary", summary)
    event.add("description", description)
    event.add("location", location)
    if dtstart:
        event.add("dtstart", dtstart)
    if dtend:
        event.add("dtend", dtend)
    return event


@freeze_time("2025-06-01 03:21:34", tz_offset=0)
class EventTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_event = create_ical_event(
            "Morning Worship",
            "Join us this morning for a time of worship",
            "All Saints Church",
        )

    def test_in_next_week(self):
        self.mock_event.add(
            "dtstart", dt.datetime(2025, 6, 2, 10, 30, 0, tzinfo=dt.timezone.utc)
        )
        self.mock_event.add(
            "dtend", dt.datetime(2025, 6, 2, 11, 30, 0, tzinfo=dt.timezone.utc)
        )
        event = create_email.Event(self.mock_event)
        self.assertEqual(event.in_next_week(), True)

    def test_not_in_next_week(self):
        self.mock_event.add(
            "dtstart", dt.datetime(2025, 6, 9, 10, 30, 0, tzinfo=dt.timezone.utc)
        )
        self.mock_event.add(
            "dtend", dt.datetime(2025, 6, 9, 11, 30, 0, tzinfo=dt.timezone.utc)
        )
        event = create_email.Event(self.mock_event)
        self.assertEqual(event.in_next_week(), False)

    def test_in_mid_future(self):
        self.mock_event.add(
            "dtstart", dt.datetime(2025, 6, 8, 10, 30, 0, tzinfo=dt.timezone.utc)
        )
        self.mock_event.add(
            "dtend", dt.datetime(2025, 6, 8, 11, 30, 0, tzinfo=dt.timezone.utc)
        )
        event = create_email.Event(self.mock_event)
        self.assertEqual(event.in_mid_future(), True)

    def test_not_in_mid_future(self):
        self.mock_event.add(
            "dtstart", dt.datetime(2025, 9, 8, 10, 30, 0, tzinfo=dt.timezone.utc)
        )
        self.mock_event.add(
            "dtend", dt.datetime(2025, 9, 8, 11, 30, 0, tzinfo=dt.timezone.utc)
        )
        event = create_email.Event(self.mock_event)
        self.assertEqual(event.in_mid_future(), False)

    def test_format_constituent_parts(self):
        self.mock_event.add(
            "dtstart", dt.datetime(2025, 6, 2, 10, 30, 0, tzinfo=dt.timezone.utc)
        )
        self.mock_event.add(
            "dtend", dt.datetime(2025, 6, 2, 11, 30, 0, tzinfo=dt.timezone.utc)
        )
        event = create_email.Event(self.mock_event)
        formatted_email = event.format_for_email()
        self.assertIn("Morning Worship", formatted_email)
        self.assertIn("Join us this morning for a time of worship", formatted_email)
        self.assertIn("All Saints Church", formatted_email)
        self.assertIn("2 June 2025, 10:30 - 11:30", formatted_email)

    def test_merged_event_time(self):
        self.mock_event.add(
            "dtstart", dt.datetime(2025, 6, 2, 10, 30, 0, tzinfo=dt.timezone.utc)
        )
        self.mock_event.add(
            "dtend", dt.datetime(2025, 6, 2, 11, 30, 0, tzinfo=dt.timezone.utc)
        )
        event = create_email.Event(self.mock_event)

        ical_event_to_merge = create_ical_event(
            "Morning Worship",
            "Join us this morning for a time of worship",
            "All Saints Church",
            dt.datetime(2025, 6, 3, 10, 30, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2025, 6, 3, 11, 30, 0, tzinfo=dt.timezone.utc),
        )
        event_to_merge = create_email.Event(ical_event_to_merge)
        event.merge_event(event_to_merge)
        formatted_email = event.format_for_email()
        self.assertIn("2 June 2025, 3 June 2025 at 10:30 - 11:30", formatted_email)


class TestDateFormatting(unittest.TestCase):
    def setUp(self):
        self.date = dt.datetime(2025, 7, 2, 10, 30, 0)

    def test_get_date_string(self):
        self.assertEqual(get_date_string(self.date), "2 July 2025")

    def test_get_time_string(self):
        self.assertEqual(get_time_string(self.date), "10:30")

    def test_get_time_string_single_digit(self):
        self.date = dt.datetime(2025, 7, 2, 10, 0, 0)
        self.assertEqual(get_time_string(self.date), "10:00")


@freeze_time("2025-06-01 03:21:34", tz_offset=0)
class TestFilterEvents(unittest.TestCase):
    def setUp(self):
        event_1_ical = create_ical_event(
            "Morning Worship",
            "Join us this morning for a time of worship",
            "All Saints Church",
            dt.datetime(2025, 6, 3, 10, 30, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2025, 6, 3, 11, 30, 0, tzinfo=dt.timezone.utc),
        )
        self.event_1 = create_email.Event(event_1_ical)

        event_2_ical = create_ical_event(
            "Evening Worship",
            "Join us this morning for a time of worship",
            "All Saints Church",
            dt.datetime(2025, 6, 3, 18, 30, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2025, 6, 3, 19, 30, 0, tzinfo=dt.timezone.utc),
        )
        self.event_2 = create_email.Event(event_2_ical)

        event_2_repeater_ical = create_ical_event(
            "Evening Worship",
            "Join us this morning for a time of worship",
            "All Saints Church",
            dt.datetime(2025, 6, 4, 18, 30, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2025, 6, 4, 19, 30, 0, tzinfo=dt.timezone.utc),
        )
        self.event_2_repeater = create_email.Event(event_2_repeater_ical)

        future_event_ical = create_ical_event(
            "Future Worship",
            "Join us in the future for a time of worship",
            "All Saints Church",
            dt.datetime(2025, 7, 4, 18, 30, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2025, 7, 4, 19, 30, 0, tzinfo=dt.timezone.utc),
        )
        self.future_event = create_email.Event(future_event_ical)

        past_event_ical = create_ical_event(
            "Past Worship",
            "Join us in the past for a time of worship",
            "All Saints Church",
            dt.datetime(2025, 5, 4, 18, 30, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2025, 5, 4, 19, 30, 0, tzinfo=dt.timezone.utc),
        )
        self.past_event = create_email.Event(past_event_ical)

    def test_get_this_weeks_events_merges_events(self):
        events = [self.event_1, self.event_2, self.event_2_repeater]
        this_weeks_events = get_this_weeks_events(events)
        self.assertEqual(len(this_weeks_events), 2)
        self.assertEqual(this_weeks_events[0].title, "Morning Worship")
        self.assertEqual(this_weeks_events[1].title, "Evening Worship")
        self.assertEqual(
            this_weeks_events[1].dates,
            [
                {
                    "start_time": dt.datetime(
                        2025, 6, 3, 18, 30, 0, tzinfo=dt.timezone.utc
                    ),
                    "end_time": dt.datetime(
                        2025, 6, 3, 19, 30, 0, tzinfo=dt.timezone.utc
                    ),
                },
                {
                    "start_time": dt.datetime(
                        2025, 6, 4, 18, 30, 0, tzinfo=dt.timezone.utc
                    ),
                    "end_time": dt.datetime(
                        2025, 6, 4, 19, 30, 0, tzinfo=dt.timezone.utc
                    ),
                },
            ],
        )

    def test_get_this_weeks_events_ignores_future_events(self):
        events = [self.event_1, self.future_event]
        this_weeks_events = get_this_weeks_events(events)
        self.assertEqual(len(this_weeks_events), 1)
        self.assertEqual(this_weeks_events[0].title, "Morning Worship")

    def test_get_this_weeks_events_ignores_past_events(self):
        events = [self.event_1, self.past_event]
        this_weeks_events = get_this_weeks_events(events)
        self.assertEqual(len(this_weeks_events), 1)
        self.assertEqual(this_weeks_events[0].title, "Morning Worship")

    def test_get_future_events_ignores_past_events(self):
        all_events = [self.event_1, self.past_event]
        this_weeks_events = get_unique_future_events(all_events, [])
        self.assertEqual(len(this_weeks_events), 1)
        self.assertEqual(this_weeks_events[0].title, "Morning Worship")

    def test_get_future_events_ignores_this_weeks_events(self):
        all_events = [self.event_1, self.future_event]
        this_weeks_events = [self.event_1]
        this_weeks_events = get_unique_future_events(all_events, [self.event_1])
        self.assertEqual(len(this_weeks_events), 1)
        self.assertEqual(this_weeks_events[0].title, "Future Worship")

    def test_get_future_events_merges_events(self):
        future_event_repeater_ical = create_ical_event(
            "Future Worship",
            "Join us in the future for a time of worship",
            "All Saints Church",
            dt.datetime(2025, 7, 5, 18, 30, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2025, 7, 5, 19, 30, 0, tzinfo=dt.timezone.utc),
        )
        future_event_repeater = create_email.Event(future_event_repeater_ical)

        events = [self.event_1, self.future_event, future_event_repeater]
        this_weeks_events = get_unique_future_events(events, [])
        self.assertEqual(len(this_weeks_events), 2)
        self.assertEqual(this_weeks_events[0].title, "Morning Worship")
        self.assertEqual(this_weeks_events[1].title, "Future Worship")
        self.assertEqual(
            this_weeks_events[1].dates,
            [
                {
                    "start_time": dt.datetime(
                        2025, 7, 4, 18, 30, 0, tzinfo=dt.timezone.utc
                    ),
                    "end_time": dt.datetime(
                        2025, 7, 4, 19, 30, 0, tzinfo=dt.timezone.utc
                    ),
                },
                {
                    "start_time": dt.datetime(
                        2025, 7, 5, 18, 30, 0, tzinfo=dt.timezone.utc
                    ),
                    "end_time": dt.datetime(
                        2025, 7, 5, 19, 30, 0, tzinfo=dt.timezone.utc
                    ),
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
