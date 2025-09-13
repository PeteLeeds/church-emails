import unittest

from icalendar import Event
import events
from sections import Section, populate_section_events
import datetime as dt


class SectionTestCase(unittest.TestCase):
    def setUp(self):
        mock_event_data = Event()
        mock_event_data.add("summary", "Test Event")
        mock_event_data.add("location", "All Saints' Church")
        mock_event_data.add("description", "Join us for a time of worship")
        mock_event_data.add(
            "dtstart", dt.datetime(2025, 6, 2, 10, 30, 0, tzinfo=dt.timezone.utc)
        )
        mock_event_data.add(
            "dtend", dt.datetime(2025, 6, 2, 11, 30, 0, tzinfo=dt.timezone.utc)
        )
        self.mock_event = events.Event(mock_event_data)

    def test_matches_matching_event(self):
        section = Section(
            {
                "title": "Services",
                "displayTitle": True,
                "default": False,
                "filters": ["Worship"],
            }
        )
        matches_event = section.matches_event(self.mock_event)
        self.assertEqual(matches_event, True)

    def test_matches_default_event(self):
        section = Section(
            {
                "title": "Other Events",
                "displayTitle": True,
                "default": True,
            }
        )
        matches_event = section.matches_event(self.mock_event)
        self.assertEqual(matches_event, True)

    def test_does_not_match_different_event(self):
        section = Section(
            {
                "title": "Outreach Events",
                "displayTitle": True,
                "default": False,
                "filters": ["outreach"],
            }
        )
        matches_event = section.matches_event(self.mock_event)
        self.assertEqual(matches_event, False)

    def test_adds_event(self):
        section = Section(
            {
                "title": "Services",
                "displayTitle": True,
                "default": False,
                "filters": ["outreach"],
            }
        )
        section.add_event(self.mock_event)
        self.assertEqual(section.events, [self.mock_event])

    def test_creates_section_email(self):
        section = Section(
            {
                "title": "Services",
                "displayTitle": True,
                "default": False,
                "filters": ["outreach"],
            }
        )
        section.add_event(self.mock_event)
        email_format = section.create_section_email()
        self.assertIn("Services", email_format)
        self.assertIn(self.mock_event.format_for_email(), email_format)

    def test_omits_header_when_specified(self):
        section = Section(
            {
                "title": "All Events",
                "displayTitle": False,
                "default": True,
            }
        )
        section.add_event(self.mock_event)
        email_format = section.create_section_email()
        self.assertNotIn("All Events", email_format)


class PopulateSectionEventsTestCase(unittest.TestCase):
    def setUp(self):
        mock_event_data = Event()
        mock_event_data.add("summary", "Test Event")
        mock_event_data.add("location", "All Saints' Church")
        mock_event_data.add("description", "Join us for a time of worship")
        mock_event_data.add(
            "dtstart", dt.datetime(2025, 6, 2, 10, 30, 0, tzinfo=dt.timezone.utc)
        )
        mock_event_data.add(
            "dtend", dt.datetime(2025, 6, 2, 11, 30, 0, tzinfo=dt.timezone.utc)
        )
        self.mock_event = events.Event(mock_event_data)

    def test_populates_first_matching_section(self):
        section_1 = Section(
            {
                "title": "Outreach",
                "displayTitle": False,
                "default": False,
                "filters": ["outreach"],
            }
        )

        section_2 = Section(
            {
                "title": "Services",
                "displayTitle": False,
                "default": False,
                "filters": ["worship"],
            }
        )
        section_3 = Section(
            {
                "title": "Other Events",
                "displayTitle": False,
                "default": True,
            }
        )
        populate_section_events([section_1, section_2], [self.mock_event])
        self.assertEqual(len(section_1.events), 0)
        self.assertEqual(len(section_2.events), 1)
        self.assertEqual(len(section_3.events), 0)
