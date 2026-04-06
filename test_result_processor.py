import unittest
from result_processor import ResultProcessor
from datetime import datetime

class TestResultProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = ResultProcessor()
        self.curr_year = str(datetime.now().year)
        self.next_year = str(datetime.now().year + 1)

    def test_fast_reject_filter(self):
        passing = [
            ("Top AI Summit in India " + self.curr_year, "Join the best AI minds for the upcoming conference."),
            ("Awards Gala " + self.next_year, "We are accepting nominations for the digital excellence awards."),
            ("Tech Expo " + self.curr_year, "A great exhibition of future technologies in Bangalore."),
            ("Healthcare Conclave " + self.curr_year, "Doctors and scientists gather to speak about the future."),
            ("Fintech Startup Meet " + self.curr_year, "New startups pitch to VCs.")
        ]
        
        for t, s in passing:
            res = self.processor._passes_fast_reject(t, s, t+" "+s, "gooddomain.com", "http://gooddomain.com/1")
            self.assertTrue(res, f"Should pass: {t}")

        rejecting = [
            ("No year in this title", "And no year in snippet either. Very sad."),
            ("Tech Summit " + self.curr_year, "The event was held last week and concluded on Friday."),
            ("Secret Meet " + self.curr_year, "This is an invitation only internal meeting."),
            ("Short " + self.curr_year, "Hi"),
            ("Great Event " + self.curr_year, "Join us", "reddit.com")
        ]
        
        for idx, item in enumerate(rejecting):
            if len(item) == 2:
                t, s = item
                res = self.processor._passes_fast_reject(t, s, t+" "+s, "gooddomain.com", "http://gooddomain.com/1")
                self.assertFalse(res, f"Should reject: {t}")
            else:
                t, s, domain = item
                res = self.processor._passes_fast_reject(t, s, t+" "+s, domain, f"http://{domain}/1")
                self.assertFalse(res, f"Should reject domain: {t}")

    def test_schema_fast_path(self):
        raw = {
            'title': 'Test',
            'snippet': 'Test snippet ' + self.curr_year,
            'pagemap': {
                'event': [{
                    'name': 'Official Event ' + self.curr_year,
                    'startdate': '2026-10-10',
                    'location': 'Mumbai'
                }]
            }
        }
        res = self.processor.process_single(raw, "Technology")
        self.assertIsNotNone(res)
        self.assertEqual(res['event_name'], "Official Event " + self.curr_year)
        self.assertEqual(res['confidence'], 95)
        self.assertEqual(res['date'], '2026-10-10')

if __name__ == '__main__':
    unittest.main()
