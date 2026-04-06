import datetime
import urllib.parse
import re
import logging
import json
import requests
from bs4 import BeautifulSoup
import config
from extractor import EventExtractor

logger = logging.getLogger(__name__)

class ResultProcessor:
    def __init__(self):
        self.extractor = EventExtractor()
        self.seen_urls_in_run = set()
    
    def process_results(self, raw_results, sector, city_context=None):
        processed = []
        for raw in raw_results:
            result = self.process_single(raw, sector, city_context)
            if result:
                processed.append(result)
        return processed

    def _elite_deep_fetch(self, url):
        """Elite Fetch: Visit the URL to extract precise dates and location from HTML."""
        data = {}
        try:
            headers = {"User-Agent": config.USER_AGENT}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return data
            
            soup = BeautifulSoup(resp.text, "html.parser")
            html_text = soup.get_text()
            
            # 1. Schema.org JSON-LD Event (Highest Priority)
            scripts = soup.find_all("script", type="application/ld+json")
            for script in scripts:
                try:
                    js = json.loads(script.string)
                    objects = js if isinstance(js, list) else [js]
                    for obj in objects:
                        if obj.get("@type") in ["Event", "BusinessEvent", "Festival"]:
                            data['event_name'] = obj.get('name')
                            sd = obj.get('startDate')
                            if sd:
                                # Standardize ISO date
                                try: data['date'] = datetime.datetime.fromisoformat(sd.split('T')[0]).strftime("%d/%m/%Y")
                                except: data['date'] = sd
                            loc = obj.get('location', {})
                            if isinstance(loc, dict):
                                data['location'] = loc.get('name') or loc.get('address', {}).get('addressLocality')
                            data['schema_found'] = True
                            return data
                except: continue

            # 2. Extract from Meta Tags
            meta_date = soup.find("meta", property="event:start_date") or soup.find("meta", name="date")
            if meta_date: data['date'] = self.extractor.extract_date(meta_date.get("content", ""))

            # 3. Extract from visible text if still missing
            if not data.get('date'):
                # Look for dates in the first 2000 chars of text
                data['date'] = self.extractor.extract_date(html_text[:3000])

        except Exception as e:
            logger.debug(f"Deep Fetch failed for {url}: {e}")
            
        return data

    def process_single(self, raw, sector, city_context=None):
        title = raw.get('title', '')
        snippet = raw.get('snippet', '')
        url = raw.get('link', '')
        display_link = raw.get('displayLink', '')
        
        combined_text = f"{title} {snippet}"
        
        # Step 1 Fast Reject Filter
        if not self._passes_fast_reject(title, snippet, combined_text, display_link, url):
            return None
        
        # Relevancy Strict Check (Fix: Accuracy Request)
        combined_text = f"{title} {snippet}"
        if not any(y in combined_text for y in ["2025", "2026", "2027"]):
            return None # Discard if no year found
            
        noise_signals = ["shares rise", "stock price", "quarterly profit", "pvt ltd", "registered office", "investors news"]
        if any(ns in combined_text.lower() for ns in noise_signals):
            return None
            
        title_lower = title.lower()
        if any(neg in title_lower for neg in config.NEGATIVE_INTENT_SIGNALS):
            return None

        # Accuracy Fix: Deep Fetch if date is missing in snippet
        event_data = {
            'sector': sector,
            'source_title': display_link or 'Google',
            'source_url': url,
            'scraped_at': datetime.datetime.now().isoformat(),
            'confidence': 40
        }

        # Step 2 Elite Deep Fetch (Proactive Date Discovery)
        snippet_date = self.extractor.extract_date(combined_text)
        is_known_platform = any(d in url.lower() for d in config.PLATINUM_DOMAINS)
        
        if (not snippet_date or is_known_platform) and url not in self.seen_urls_in_run:
            self.seen_urls_in_run.add(url)
            fetched = self._elite_deep_fetch(url)
            if fetched:
                if fetched.get('event_name'): event_data['event_name'] = fetched['event_name']
                if fetched.get('date'): event_data['date'] = fetched['date']
                if fetched.get('location'): event_data['location'] = fetched['location']
                if fetched.get('schema_found'):
                    event_data['confidence'] = 95
                    event_data['verified'] = True

        # Step 3 Precision Extraction
        if not event_data.get('event_name'):
            event_data['event_name'] = self.extractor.extract_name(title, snippet)
        
        if not event_data.get('date'):
            event_data['date'] = self.extractor.extract_date(combined_text)

        if not event_data.get('location'):
            event_data['location'] = self.extractor.extract_venue(combined_text)

        # Detect Type (Fix: Requested Column)
        event_data['event_type'] = self._detect_type(event_data['event_name'], combined_text)

        # Fix: Nomination Open detection
        if event_data['event_type'] == 'Awards':
            if any(kw in combined_text.lower() for kw in ["nomination open", "apply now", "call for nomination", "entries open", "nominat now"]):
                event_data['nomination_deadline'] = "Open"
                event_data['status'] = 'NOMINATIONS_OPEN'

        # Final Cleaning
        event_data['event_name'] = self._clean_final_name(event_data.get('event_name', ''))
        
        if not event_data['event_name'] or len(event_data['event_name']) < 5:
            return None

        # Confidence Scoring
        if not event_data.get('verified'):
            score = 30
            # Name Quality (avoid sentences)
            if 3 < len(event_data['event_name'].split()) < 10: score += 20
            if event_data.get('date'): score += 25
            if event_data.get('location') and event_data['location'] != "India": score += 15
            
            # Domain Trust Bonus
            if any(d in url.lower() for d in config.DEEP_FETCH_ALLOWLIST + config.PLATINUM_DOMAINS):
                score += 15
                
            event_data['confidence'] = score

        if event_data['confidence'] < config.MIN_STORAGE_CONFIDENCE:
            return None
            
        return event_data

    def _passes_fast_reject(self, title, snippet, combined_text, display_link, url):
        ct_lower = combined_text.lower()
        EVENT_SIGNALS = ["summit", "conference", "award", "expo", "forum", "conclave", "ceremony", "nomination", "prize"]
        if not any(s in ct_lower for s in EVENT_SIGNALS):
            return False
        if any(j in ct_lower for j in ["hiring", "apply for job", "vacancy", "salary"]):
            return False
        return True

    def _detect_type(self, name, combined):
        text = f"{name} {combined}".lower()
        if any(w in text for w in ["award", "honour", "prize", "recognit", "hall of fame", "medal"]): 
            return "Awards"
        return "Event"

    def _clean_final_name(self, name):
        # Remove noisy trailers
        name = re.sub(r'\s+[|:–-]\s+.*$', '', name)
        name = re.sub(r'(?i)\s+(Register Now|Join Us|Apply Now|2026)$', '', name)
        return name.strip()
