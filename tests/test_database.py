import unittest
import os
import tempfile
from pathlib import Path
from src import database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Point to a temporary db for isolated testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.orig_db_dir = database.DB_DIR
        self.orig_db_path = database.DB_PATH
        database.DB_DIR = Path(self.temp_dir.name)
        database.DB_PATH = database.DB_DIR / "test_news.db"
        database.init_db()

    def tearDown(self):
        database.DB_DIR = self.orig_db_dir
        database.DB_PATH = self.orig_db_path
        self.temp_dir.cleanup()

    def test_deduplication_and_saving(self):
        art1 = {
            "title": "NTA Releases JEE Main 2027 Notification",
            "url": "https://nta.ac.in/notice123.pdf",
            "source": "NTA Official",
            "exam_category": "JEE",
            "priority": "HIGH",
            "published_date": "2026-11-15"
        }

        # First insert should succeed
        art_id = database.save_article(art1)
        self.assertIsNotNone(art_id)

        # Duplicate insert with same title & url should return None
        duplicate_id = database.save_article(art1)
        self.assertIsNone(duplicate_id)

        # Retrieve unsent
        unsent = database.get_unsent_articles(limit=10)
        self.assertEqual(len(unsent), 1)
        self.assertEqual(unsent[0]["title"], art1["title"])
        self.assertEqual(unsent[0]["is_sent"], 0)

        # Mark sent
        database.mark_article_sent(art_id, status="SENT")
        unsent_after = database.get_unsent_articles(limit=10)
        self.assertEqual(len(unsent_after), 0)

    def test_stats(self):
        art1 = {
            "title": "NEET UG 2027 Registration Open",
            "url": "https://neet.nta.nic.in/reg",
            "source": "NEET Portal",
            "exam_category": "NEET",
            "priority": "HIGH",
            "published_date": "2026-11-15"
        }
        database.save_article(art1)
        stats = database.get_stats()
        self.assertEqual(stats["total_articles"], 1)
        self.assertEqual(stats["pending_alerts"], 1)
        self.assertEqual(stats["sent_alerts"], 0)


if __name__ == "__main__":
    unittest.main()
