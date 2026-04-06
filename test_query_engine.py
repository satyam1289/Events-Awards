import unittest
import os
import tempfile
import config

temp_dir = tempfile.mkdtemp()
config.QUERY_STATE_FILE = os.path.join(temp_dir, 'state.json')

from query_engine import QueryEngine
from datetime import datetime

class TestQueryEngine(unittest.TestCase):
    def setUp(self):
        self.engine = QueryEngine()
        
    def test_year_injection(self):
        q = self.engine.generate_tier_1(max_queries=1)[0]['query']
        self.assertIn(str(datetime.now().year), q)
        
    def test_total_queries_limit(self):
        t1 = self.engine.generate_tier_1(max_queries=3)
        self.assertLessEqual(len(t1), 3)
        
        t2 = self.engine.generate_tier_2(max_queries=13)
        self.assertLessEqual(len(t2), 13)
        
        t3 = self.engine.generate_tier_3(max_queries=30)
        self.assertLessEqual(len(t3), 30)

    def test_query_length_limit(self):
        long_q = "A" * 150
        truncated = self.engine._truncate_query(long_q)
        self.assertLessEqual(len(truncated), 128)

if __name__ == '__main__':
    unittest.main()
