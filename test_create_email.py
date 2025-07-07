from icalendar import Event
from freezegun import freeze_time
import datetime as dt

# import zoneinfo
import unittest
import create_email
from create_email import get_date_string, get_time_string


@freeze_time("2025-06-01 03:21:34", tz_offset=0)
class EventTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_event = Event()
        self.mock_event.add("summary", "Morning Worship")
        self.mock_event.add("description", "Join us this morning for a time of worship")
        self.mock_event.add("location", "All Saints Church")

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
            "dtstart", dt.datetime(2025, 6, 8, 10, 30, 0, tzinfo=dt.timezone.utc)
        )
        self.mock_event.add(
            "dtend", dt.datetime(2025, 6, 8, 11, 30, 0, tzinfo=dt.timezone.utc)
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


if __name__ == "__main__":
    unittest.main()
