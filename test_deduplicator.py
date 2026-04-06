import unittest
from deduplicator import Deduplicator
from unittest.mock import MagicMock

class TestDeduplicator(unittest.TestCase):
    def setUp(self):
        self.mock_storage = MagicMock()
        self.mock_storage.get_all_events.return_value = [
            {
                'event_name': 'Global Tech Summit',
                'sector': 'Technology',
                'date': '15 March 2026',
                'location': 'Bangalore',
                'confidence': 80
            }
        ]
        self.dedup = Deduplicator(self.mock_storage)

    def test_exact_hash(self):
        new_ev = {
            'event_name': 'global tech summit',
            'sector': 'Technology',
            'date': '15 march 2026',
            'location': 'bangalore'
        }
        self.assertFalse(self.dedup.process_event(new_ev))

    def test_fuzzy_match_above_threshold(self):
        new_ev = {
            'event_name': 'The Global Tech Summit 2026',
            'sector': 'Technology',
            'date': '14 March 2026',
            'location': 'Bangalore',
            'confidence': 60
        }
        self.assertFalse(self.dedup.process_event(new_ev))

    def test_fuzzy_match_below_threshold(self):
        new_ev = {
            'event_name': 'Quantum Computing Conference',
            'sector': 'Technology',
            'date': '15 March 2026',
            'location': 'Bangalore'
        }
        self.assertTrue(self.dedup.process_event(new_ev))

    def test_multi_city_split(self):
        ev = {
            'event_name': 'Startup Roadshow',
            'location': 'Delhi, Mumbai and Bengaluru'
        }
        splits = self.dedup.split_multi_city(ev)
        self.assertEqual(len(splits), 3)
        self.assertEqual(splits[0]['location'].strip(), 'Delhi')
        self.assertEqual(splits[1]['location'].strip(), 'Mumbai')
        self.assertEqual(splits[2]['location'].strip(), 'Bengaluru')

if __name__ == '__main__':
    unittest.main()
