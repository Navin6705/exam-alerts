import unittest
from src.formatters.message_formatter import (
    format_single_article_message,
    format_digest_message,
    get_exam_emoji,
    get_priority_badge
)


class TestMessageFormatter(unittest.TestCase):
    def test_single_article_formatting(self):
        article = {
            "title": "VITEEE 2027 Application Form Released",
            "url": "https://viteee.vit.ac.in/",
            "source": "Official VIT Portal",
            "exam_category": "VITEEE",
            "priority": "HIGH",
            "published_date": "2026-11-15"
        }
        msg = format_single_article_message(article)
        self.assertIn("VITEEE", msg)
        self.assertIn("https://viteee.vit.ac.in/", msg)
        self.assertIn("URGENT ALERT", msg)
        self.assertIn("Mera Exam Bot", msg)

    def test_digest_formatting(self):
        articles = [
            {
                "title": "JEE Main Session 1 Dates Announced",
                "url": "https://jeemain.nta.nic.in/",
                "exam_category": "JEE",
                "priority": "HIGH"
            },
            {
                "title": "NEET UG Advisory Released",
                "url": "https://neet.nta.nic.in/",
                "exam_category": "NEET",
                "priority": "MEDIUM"
            }
        ]
        digest = format_digest_message(articles)
        self.assertIn("EDUALERT: 2 NEW ADMISSIONS NOTICES", digest)
        self.assertIn("[JEE]", digest)
        self.assertIn("[NEET]", digest)
        self.assertIn("https://jeemain.nta.nic.in/", digest)

    def test_emojis_and_badges(self):
        self.assertEqual(get_exam_emoji("JEE"), "📐")
        self.assertEqual(get_exam_emoji("NEET"), "🩺")
        self.assertEqual(get_exam_emoji("VITEEE"), "🏛️")
        self.assertEqual(get_exam_emoji("ACPC"), "🦁")
        self.assertEqual(get_exam_emoji("DAIICT"), "💻")
        self.assertIn("URGENT", get_priority_badge("HIGH"))


if __name__ == "__main__":
    unittest.main()
