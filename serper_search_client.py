import logging
import time
import json
import http.client
import os
from datetime import datetime
import query_cache

logger = logging.getLogger(__name__)

class SerperSearchClient:
    """The unlimited Free-Tier proxy connecting directly to Google Search Engine."""
    
    def __init__(self):
        # Must load from environment to show up in USER's serper dashboard
        self.api_key = os.getenv("SERPER_API_KEY")
        if not self.api_key:
            logger.error("🛑 SERPER_API_KEY not found in .env! Searching will fail.")
        self._last_call_time = 0
        self.calls_in_run = 0 # Fix 3 — Current run counter

    def log_credit_used(self, query):
        """Log Serper API usage for credit tracking."""
        log_file = "data/credit_log.json"
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        
        log = {"daily": {}, "monthly": {}}
        if os.path.exists(log_file):
            try:
                with open(log_file) as f:
                    log = json.load(f)
            except:
                pass
        
        log["daily"][today] = log["daily"].get(today, 0) + 1
        log["monthly"][month] = log["monthly"].get(month, 0) + 1
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, "w") as f:
            json.dump(log, f, indent=2)

    def enforce_rate_limit(self):
        elapsed = time.time() - self._last_call_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self._last_call_time = time.time()

    def search(self, query: str, use_awards_cse: bool = False, date_restrict: str = None, force_no_cache: bool = False) -> list:
        if not self.api_key:
            return []

        # Fix 3 — Hard cap of 80 queries per single run
        if self.calls_in_run >= 80:
            logger.warning(f"🛑 RUN CAP REACHED: Stopping Serper API calls after 80 queries this run.")
            return []
        
        # Fix 4 — 48-hour Query Cache (MD5 based)
        if not force_no_cache and query_cache.is_cached(query):
            logger.info(f"💾 CACHE HIT: Skipping API call for '{query}' (Requested in last 48h)")
            return []
        
        self.enforce_rate_limit()
        logger.info(f"🚀 [Serper Proxy] Attempting API Call #{self.calls_in_run + 1}")
        logger.info(f"🚀 [Serper Proxy] Fetching live Google data for: '{query}'...")
        
        parsed = []
        try:
            conn = http.client.HTTPSConnection("google.serper.dev")
            payload = json.dumps({
              "q": query,
              "gl": "in" # Strict Indian Geolocation
            })
            headers = {
              'X-API-KEY': self.api_key.strip(),
              'Content-Type': 'application/json'
            }
            conn.request("POST", "/search", payload, headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            
            json_response = json.loads(data)
            
            # Update counter on successful attempt or limit message
            self.calls_in_run += 1

            # Error handling for limits or invalid key
            if "message" in json_response:
                error_msg = json_response["message"]
                if "credits" in error_msg.lower() or "limit" in error_msg.lower():
                    logger.error(f"🛑 SERPER API LIMIT REACHED: {error_msg}")
                    return []
                elif "invalid" in error_msg.lower():
                    logger.error(f"🛑 SERPER API KEY INVALID: {error_msg}")
                    return []
                
            if "organic" not in json_response:
                logger.warning(f"Serper API returned no organic results for: {query}")
                return parsed
                
            for result in json_response["organic"]:
                parsed.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'link': result.get('link', ''),
                    'displayLink': result.get('link', '').split('/')[2] if '//' in result.get('link', '') else result.get('link', ''),
                })
            
            # Save to cache and log credit usage after successful call
            query_cache.save_to_cache(query, parsed)
            self.log_credit_used(query)
            
        except Exception as e:
            logger.error(f"Serper API Critical Error: {e}")
            
        return parsed
