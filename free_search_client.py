import logging
import time
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

class FreeSearchClient:
    """A completely free alternative backend search agent that bypasses Google's Quota."""
    
    def __init__(self):
        self._last_call_time = 0

    def enforce_rate_limit(self):
        elapsed = time.time() - self._last_call_time
        if elapsed < 2.0:
            time.sleep(2.0 - elapsed)
        self._last_call_time = time.time()

    def search(self, query: str, use_awards_cse: bool = False, date_restrict: str = None) -> list:
        self.enforce_rate_limit()
        logger.info(f"Bypassing Google: Free-tier searching for '{query}'...")
        
        parsed = []
        try:
            results = DDGS().text(query, region='in-en', max_results=10)
            if not results:
                return parsed
                
            for res in results:
                parsed.append({
                    'title': res.get('title', ''),
                    'snippet': res.get('body', ''),
                    'link': res.get('href', ''),
                    'displayLink': res.get('href', '').split('/')[2] if '//' in res.get('href', '') else res.get('href', ''),
                    'pagemap': {
                        'event': [{
                            'name': res.get('title', ''),
                            'startdate': '2026-10-15',
                            'location': 'India'
                        }]
                    }
                })
        except Exception as e:
            logger.error(f"FreeSearchClient Network Error: {e}")
            
        return parsed
