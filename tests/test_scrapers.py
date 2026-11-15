import unittest
from src.scrapers.aggregator import classify_priority


class TestScrapers(unittest.TestCase):
    def test_priority_classification(self):
        self.assertEqual(classify_priority("JEE Main 2027 Admit Card released on nta.ac.in"), "HIGH")
        self.assertEqual(classify_priority("NEET UG 2027 Exam Date Announced by NTA"), "HIGH")
        self.assertEqual(classify_priority("VITEEE 2027 Application Form Syllabus Details"), "MEDIUM")
        self.assertEqual(classify_priority("IIT Delhi alumni meeting scheduled for next month"), "LOW")


if __name__ == "__main__":
    unittest.main()
