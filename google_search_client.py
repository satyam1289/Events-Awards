import os
import time
import json
import logging
import threading
import datetime
import html
import requests
import config

logger = logging.getLogger(__name__)

# Single lock for quota and query state files
_meta_lock = threading.Lock()

class GoogleSearchClient:
    """Client for Google Custom Search JSON API with quota management and rate limiting."""
    
    def __init__(self):
        self.api_key = config.GOOGLE_API_KEY
        self.cse_events = config.GOOGLE_CSE_ID_EVENTS
        self.cse_awards = config.GOOGLE_CSE_ID_AWARDS
        
        if not self.api_key or not self.cse_events:
            raise EnvironmentError("GOOGLE_API_KEY not set. Please set environment variables before running.")
            
        if self.cse_events == self.cse_awards and getattr(self, '_logged_warning', False) is False:
            logger.warning("GOOGLE_CSE_ID_EVENTS and GOOGLE_CSE_ID_AWARDS are identical. Using same CSE for both.")
            GoogleSearchClient._logged_warning = True
            
        self.endpoint = "https://www.googleapis.com/customsearch/v1"
        self._last_call_time = 0

    def get_quota_info(self):
        """Reads quota usage from disk securely."""
        with _meta_lock:
            if not os.path.exists(config.QUOTA_FILE):
                return {"date": str(datetime.datetime.now(datetime.timezone.utc).date()), "daily_count": 0, "quota_exhausted": False}
                
            try:
                with open(config.QUOTA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Reset if it's a new UTC day
                current_utc_date = str(datetime.datetime.now(datetime.timezone.utc).date())
                if data.get("date") != current_utc_date:
                    data = {"date": current_utc_date, "daily_count": 0, "quota_exhausted": False}
                    self._save_quota_info_unlocked(data)
                    
                return data
            except Exception as e:
                logger.error(f"Error reading quota file: {e}")
                return {"date": str(datetime.datetime.now(datetime.timezone.utc).date()), "daily_count": 0, "quota_exhausted": False}

    def _save_quota_info_unlocked(self, data):
        """Saves quota usage to disk (caller must hold _meta_lock)."""
        try:
            with open(config.QUOTA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing quota file: {e}")

    def increment_quota(self, exhausted=False):
        """Increments the daily quota counter."""
        with _meta_lock:
            if not os.path.exists(config.QUOTA_FILE):
                data = {"date": str(datetime.datetime.now(datetime.timezone.utc).date()), "daily_count": 0, "quota_exhausted": False}
            else:
                try:
                    with open(config.QUOTA_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    current_utc_date = str(datetime.datetime.now(datetime.timezone.utc).date())
                    if data.get("date") != current_utc_date:
                        data = {"date": current_utc_date, "daily_count": 0, "quota_exhausted": False}
                except:
                    data = {"date": str(datetime.datetime.now(datetime.timezone.utc).date()), "daily_count": 0, "quota_exhausted": False}
            
            if not exhausted:
                data['daily_count'] += 1
            if exhausted:
                data['quota_exhausted'] = True
                
            self._save_quota_info_unlocked(data)
            
            if data['daily_count'] == config.QUOTA_WARNING_THRESHOLD:
                logger.critical(f"WARNING: Quota limit reaching soon. Used: {data['daily_count']}")

    def enforce_rate_limit(self):
        """Sleeps to maintain 10 requests / second with 0.12s wait."""
        elapsed = time.time() - self._last_call_time
        if elapsed < 0.12:
            time.sleep(0.12 - elapsed)
        self._last_call_time = time.time()

    def search(self, query: str, use_awards_cse: bool = False, date_restrict: str = None) -> list:
        """Executes a search against the Google Custom Search API."""
        quota_data = self.get_quota_info()
        
        if quota_data.get('quota_exhausted'):
            logger.warning("Quota exhausted for the day. Skipping query.")
            return []
            
        if quota_data.get('daily_count', 0) >= config.MAX_DAILY_QUERIES + 5:
            logger.warning("Hard stop limit of 95 queries/day reached. Skipping query.")
            return []

        cx = self.cse_awards if use_awards_cse and self.cse_awards else self.cse_events

        params = {
            'key': self.api_key,
            'cx': cx,
            'q': query,
            'num': 10
        }
        if date_restrict:
            params['dateRestrict'] = date_restrict

        retries = 3
        backoffs = [2, 4, 8]
        
        for attempt in range(retries + 1):
            self.enforce_rate_limit()
            
            try:
                response = requests.get(self.endpoint, params=params, timeout=15)
                
                if response.status_code == 200:
                    self.increment_quota()
                    data = response.json()
                    return self._parse_results(data)
                    
                elif response.status_code == 400:
                    logger.error(f"HTTP 400 Bad Query: {query}")
                    self.increment_quota()
                    return []
                    
                elif response.status_code == 403:
                    logger.error("HTTP 403 Quota Exceeded. Disabling further requests for today.")
                    self.increment_quota(exhausted=True)
                    return []
                    
                elif response.status_code in [429, 503]:
                    logger.warning(f"HTTP {response.status_code} received. Attempt {attempt+1} of {retries}.")
                    if attempt < retries:
                        time.sleep(backoffs[attempt])
                        continue
                    else:
                        logger.error(f"Max retries reached for query: {query}")
                        self.increment_quota()
                        return []
                else:
                    logger.error(f"Unexpected HTTP {response.status_code}: {response.text}")
                    self.increment_quota()
                    return []
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Network error on attempt {attempt+1}: {e}")
                if attempt < retries:
                    time.sleep(backoffs[attempt])
                else:
                    self.increment_quota()
                    return []
                    
        return []

    def _parse_results(self, data: dict) -> list:
        parsed = []
        if 'items' not in data:
            return parsed
            
        for item in data['items']:
            raw_title = item.get('title', '')
            parsed.append({
                'title': html.unescape(raw_title) if raw_title else '',
                'snippet': html.unescape(item.get('snippet', '') or ''),
                'link': item.get('link', ''),
                'displayLink': item.get('displayLink', ''),
                'pagemap': item.get('pagemap', {})
            })
        return parsed
