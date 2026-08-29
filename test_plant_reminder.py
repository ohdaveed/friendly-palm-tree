"""Tests for plant_reminder.py"""

import json
import os
import sys
import tempfile
import unittest
from datetime import date, timedelta
from unittest.mock import patch

# Ensure the module under test is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import plant_reminder


class PlantReminderTests(unittest.TestCase):
    def setUp(self):
        # Redirect DATA_FILE to a temporary file for isolation
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.tmp.close()
        os.unlink(self.tmp.name)  # remove so load_plants sees "no file"
        self.orig = plant_reminder.DATA_FILE
        plant_reminder.DATA_FILE = self.tmp.name

    def tearDown(self):
        plant_reminder.DATA_FILE = self.orig
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    # --- load / save ---
    def test_load_plants_empty(self):
        self.assertEqual(plant_reminder.load_plants(), {})

    def test_save_and_load(self):
        data = {"Cactus": {"interval_days": 14, "last_watered": "2026-01-01"}}
        plant_reminder.save_plants(data)
        self.assertEqual(plant_reminder.load_plants(), data)

    # --- add ---
    def test_add_plant(self):
        with patch("plant_reminder.date") as mock_date:
            mock_date.today.return_value = date(2026, 1, 15)
            mock_date.fromisoformat = date.fromisoformat
            plant_reminder.add_plant("Fern", 3)

        plants = plant_reminder.load_plants()
        self.assertIn("Fern", plants)
        self.assertEqual(plants["Fern"]["interval_days"], 3)
        self.assertEqual(plants["Fern"]["last_watered"], "2026-01-15")

    # --- water ---
    def test_water_plant(self):
        plant_reminder.save_plants(
            {"Basil": {"interval_days": 2, "last_watered": "2026-01-01"}}
        )
        with patch("plant_reminder.date") as mock_date:
            mock_date.today.return_value = date(2026, 1, 10)
            mock_date.fromisoformat = date.fromisoformat
            plant_reminder.water_plant("Basil")

        plants = plant_reminder.load_plants()
        self.assertEqual(plants["Basil"]["last_watered"], "2026-01-10")

    def test_water_unknown_plant(self):
        import io
        with patch("sys.stdout", new_callable=io.StringIO) as out:
            plant_reminder.water_plant("Ghost Plant")
        self.assertIn("not found", out.getvalue())

    # --- remove ---
    def test_remove_plant(self):
        plant_reminder.save_plants(
            {"Mint": {"interval_days": 1, "last_watered": "2026-01-01"}}
        )
        plant_reminder.remove_plant("Mint")
        self.assertNotIn("Mint", plant_reminder.load_plants())

    # --- reminders ---
    def test_check_reminders_overdue(self):
        import io
        past = (date.today() - timedelta(days=5)).isoformat()
        plant_reminder.save_plants(
            {"Rose": {"interval_days": 2, "last_watered": past}}
        )
        with patch("sys.stdout", new_callable=io.StringIO) as out:
            plant_reminder.check_reminders()
        self.assertIn("Rose", out.getvalue())

    def test_check_reminders_up_to_date(self):
        import io
        today = date.today().isoformat()
        plant_reminder.save_plants(
            {"Cactus": {"interval_days": 30, "last_watered": today}}
        )
        with patch("sys.stdout", new_callable=io.StringIO) as out:
            plant_reminder.check_reminders()
        self.assertIn("up to date", out.getvalue())


if __name__ == "__main__":
    unittest.main()
