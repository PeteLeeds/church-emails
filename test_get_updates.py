import unittest
from unittest.mock import MagicMock, patch

from freezegun import freeze_time

from get_updates import Update, create_update_email


@freeze_time("2025-06-01 03:21:34", tz_offset=0)
class UpdateTestCase(unittest.TestCase):
    def test_in_date_range(self):
        update_row = [
            "4/18/2025 16:58:08",
            "New Curate",
            "We have a new curate starting with us in July!",
            "6/5/2025",
        ]
        update = Update(update_row)
        self.assertEqual(update.in_date_range(), True)

    def test_not_in_date_range(self):
        update_row = [
            "4/18/2025 16:58:08",
            "New Curate",
            "We have a new curate starting with us in July!",
            "5/6/2025",
        ]
        update = Update(update_row)
        self.assertEqual(update.in_date_range(), False)

    def test_formatting_for_email(self):
        update_row = [
            "4/18/2025 16:58:08",
            "New Curate",
            "We have a new curate starting with us in July!",
            "6/5/2025",
        ]
        update = Update(update_row)
        formatted_update = update.format_for_email()
        self.assertIn("<h3>New Curate</h3>", formatted_update)
        self.assertIn(
            "<p>We have a new curate starting with us in July!<p>", formatted_update
        )


@freeze_time("2025-06-01 03:21:34", tz_offset=0)
class CreateUpdateEmailTest(unittest.TestCase):
    @patch("get_updates.get_update_objects")
    def test_return_values_in_date_range(self, update_objects_mock: MagicMock):
        update_1 = [
            "4/18/2025 16:58:08",
            "New Curate",
            "We have a new curate starting with us in July!",
            "5/6/2025",
        ]
        update_2 = [
            "4/18/2025 16:58:08",
            "Hot Meals Needed",
            "We are looking for people to cook hot meals.",
            "6/5/2025",
        ]
        update_objects_mock.return_value = [Update(update_1), Update(update_2)]
        update_email = create_update_email()
        self.assertIn("<h2>Updates and Notices</h2>", update_email)
        self.assertIn("<h3>Hot Meals Needed</h3>", update_email)
        self.assertNotIn("<h3>New Curate</h3>", update_email)

    @patch("get_updates.get_update_objects")
    def test_return_values_not_in_date_range(self, update_objects_mock: MagicMock):
        update = [
            "4/18/2025 16:58:08",
            "New Curate",
            "We have a new curate starting with us in July!",
            "5/6/2025",
        ]
        update_objects_mock.return_value = [Update(update)]
        update_email = create_update_email()
        self.assertEqual(update_email, "")
