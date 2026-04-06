import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import json
import config

temp_dir = tempfile.mkdtemp()
config.QUOTA_FILE = os.path.join(temp_dir, 'quota_test.json')
config.GOOGLE_API_KEY = "test_key"
config.GOOGLE_CSE_ID_EVENTS = "test_cse"

from google_search_client import GoogleSearchClient

class TestGoogleClient(unittest.TestCase):
    def setUp(self):
        self.client = GoogleSearchClient()
        if os.path.exists(config.QUOTA_FILE):
            os.remove(config.QUOTA_FILE)

    @patch('google_search_client.requests.get')
    def test_success_increment(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'items': [{'title': 'Test &amp; Co', 'snippet': 'Hello'}]}
        mock_get.return_value = mock_resp
        
        results = self.client.search("test query")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Test & Co')
        
        q_info = self.client.get_quota_info()
        self.assertEqual(q_info['daily_count'], 1)
        self.assertFalse(q_info['quota_exhausted'])

    @patch('google_search_client.time.sleep', return_value=None)
    @patch('google_search_client.requests.get')
    def test_retry_on_429(self, mock_get, mock_sleep):
        mock_429 = MagicMock()
        mock_429.status_code = 429
        mock_200 = MagicMock()
        mock_200.status_code = 200
        mock_200.json.return_value = {}
        
        mock_get.side_effect = [mock_429, mock_429, mock_200]
        
        results = self.client.search("test")
        self.assertEqual(mock_get.call_count, 3)

    @patch('google_search_client.requests.get')
    def test_hard_stop_403(self, mock_get):
        mock_403 = MagicMock()
        mock_403.status_code = 403
        mock_get.return_value = mock_403
        
        results = self.client.search("test")
        self.assertEqual(len(results), 0)
        
        q_info = self.client.get_quota_info()
        self.assertTrue(q_info['quota_exhausted'])
        
        mock_get.reset_mock()
        self.client.search("test again")
        self.assertEqual(mock_get.call_count, 0)

    @patch('google_search_client.requests.get')
    def test_empty_result(self, mock_get):
        mock_200 = MagicMock()
        mock_200.status_code = 200
        mock_200.json.return_value = {}
        mock_get.return_value = mock_200
        
        results = self.client.search("empty")
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
