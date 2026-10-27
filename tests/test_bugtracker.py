from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

import bugtracker  # noqa: E402


class BugTrackerTests(unittest.TestCase):
    def test_import_and_list_open_bugs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "tracker.db"
            with patch.object(bugtracker, "DB_PATH", database):
                bugtracker.init_db()
                count = bugtracker.import_csv(ROOT / "data" / "bugs.csv")
                open_bugs = bugtracker.list_open(limit=10)

        with (ROOT / "data" / "bugs.csv").open(newline="", encoding="utf-8") as stream:
            expected_count = len(list(csv.DictReader(stream)))
        self.assertEqual(count, expected_count)
        self.assertLessEqual(len(open_bugs), 10)
        self.assertTrue(all(row[4] in {"Open", "In Progress", "Blocked"} for row in open_bugs))

    def test_add_bug_uses_database_generated_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(bugtracker, "DB_PATH", Path(directory) / "tracker.db"):
                bugtracker.init_db()
                first = bugtracker.add_bug("Checkout", "High", "QA", "Dev 1", "Missing validation", "Example")
                second = bugtracker.add_bug("Cart", "Low", "QA", "Dev 2", "Wrong total", "Example")
                rows = bugtracker.list_open(limit=10)

        self.assertGreater(second, first)
        self.assertEqual(len(rows), 2)

    def test_import_rejects_duplicate_ids_before_writing(self) -> None:
        fields = [
            "bug_id", "created_date", "resolved_date", "module", "severity",
            "status", "reported_by", "assigned_to", "title", "description",
        ]
        row = {
            "bug_id": "1", "created_date": "2025-01-01", "resolved_date": "",
            "module": "Cart", "severity": "High", "status": "Open",
            "reported_by": "QA", "assigned_to": "Dev", "title": "Issue",
            "description": "Example issue",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "bad.csv"
            with source.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerow(row)
                writer.writerow(row)
            with patch.object(bugtracker, "DB_PATH", root / "tracker.db"):
                bugtracker.init_db()
                with self.assertRaisesRegex(ValueError, "unique"):
                    bugtracker.import_csv(source)
                rows = bugtracker.list_open(limit=10)

        self.assertEqual(rows, [])

    def test_list_open_requires_positive_limit(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            bugtracker.list_open(limit=0)


if __name__ == "__main__":
    unittest.main()
