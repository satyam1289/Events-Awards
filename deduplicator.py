import difflib
import re
import logging
from storage import EventStorage
import config
from datetime import datetime

logger = logging.getLogger(__name__)

class Deduplicator:
    def __init__(self, storage: EventStorage):
        self.storage = storage
        self.exact_hashes = set()
        self.events_cache = []
        self._hydrate()

    def _hydrate(self):
        """Load all events from storage to build in-memory cache and exact hashes."""
        self.events_cache = self.storage.get_all_events()
        for event in self.events_cache:
            h = self._generate_exact_hash(event)
            self.exact_hashes.add(h)

    def _normalize(self, text):
        if not text:
            return ""
        text = text.lower()
        # strip punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # remove stopwords and ordinal prefixes
        words = text.split()
        stopwords = {"the", "of", "and", "india", "annual"}
        clean_words = []
        for w in words:
            if w in stopwords:
                continue
            # remove ordinal prefix: 1st, 2nd, 3rd, 4th, 12th
            if re.match(r'^\d+(st|nd|rd|th)$', w):
                continue
            clean_words.append(w)
        # collapse whitespace
        return " ".join(clean_words)

    def _generate_exact_hash(self, event):
        n_name = self._normalize(event.get('event_name', ''))
        n_date = self._normalize(event.get('date', ''))
        n_loc = self._normalize(event.get('location', ''))
        return f"{n_name}|{n_date}|{n_loc}"
        
    def _parse_date(self, date_str):
        if not date_str:
            return None
        try:
            import dateparser
            return dateparser.parse(date_str)
        except:
            return None

    def split_multi_city(self, event):
        """Splits multi-city events into separate records."""
        loc_str = event.get('location', '')
        if ',' in loc_str or ' and ' in loc_str.lower():
            cities = re.split(r',|\band\b', loc_str, flags=re.IGNORECASE)
            events = []
            for city in cities:
                city = city.strip()
                if city:
                    new_ev = event.copy()
                    new_ev['location'] = city
                    events.append(new_ev)
            return events
        return [event]

    def normalize_for_comparison(self, name: str) -> str:
        """Strip year, city, edition before comparing."""
        # Remove year
        name = re.sub(r'\b20\d{2}\b', '', name)
        # Remove edition number
        name = re.sub(r'\b\d+(st|nd|rd|th)\s+edition\b', '', name, flags=re.I)
        # Remove city names
        CITIES = ["Mumbai", "Delhi", "Bangalore", "Bengaluru", "Hyderabad", 
                  "Chennai", "Pune", "Ahmedabad", "Kolkata", "Gurgaon"]
        for city in CITIES:
            name = re.sub(rf'\b{city}\b', '', name, flags=re.I)
        # Collapse whitespace
        return re.sub(r'\s+', ' ', name).strip().lower()

    def process_event(self, new_event):
        """
        Process a new event. 
        Returns True if the event is NEW and should be passed to storage.add_event.
        Returns False if it's a duplicate or if the deduplicator handled the update itself.
        """
        # Pass 1: Exact Hash
        h = self._generate_exact_hash(new_event)
        if h in self.exact_hashes:
            return False

        # Pass 2: Fuzzy Match
        new_name_raw = new_event.get('event_name', '')
        new_name_comp = self.normalize_for_comparison(new_name_raw)
        new_sector = new_event.get('sector', '')
        new_loc = new_event.get('location', '').lower()
        new_date_str = new_event.get('date', '')
        
        new_date_obj = self._parse_date(new_date_str)

        for i, existing in enumerate(self.events_cache):
            if existing.get('sector', '') != new_sector:
                continue

            ex_name_raw = existing.get('event_name', '')
            ex_name_comp = self.normalize_for_comparison(ex_name_raw)
            
            # Match similarity
            sim = 0.0
            if new_name_comp and ex_name_comp:
                sim = difflib.SequenceMatcher(None, new_name_comp, ex_name_comp).ratio()
                
            if sim > config.FUZZY_MATCH_THRESHOLD:
                # Check location
                ex_loc = existing.get('location', '').lower()
                loc_match = False
                if ex_loc == new_loc or ex_loc == "india" or new_loc == "india":
                    loc_match = True
                    
                if loc_match:
                    # Check dates
                    ex_date_str = existing.get('date', '')
                    ex_date_obj = self._parse_date(ex_date_str)
                    
                    date_match = False
                    if not new_date_str or not ex_date_str:
                        date_match = True 
                    elif new_date_obj and ex_date_obj:
                        diff = abs((new_date_obj - ex_date_obj).days)
                        if diff <= 7:
                            date_match = True
                    else:
                        date_match = True
                        
                    if date_match:
                        # DUPLICATE
                        ex_conf = existing.get('confidence', 0)
                        new_conf = new_event.get('confidence', 0)
                        
                        replace = False
                        if new_conf > ex_conf:
                            replace = True
                        elif new_conf == ex_conf:
                            if not ex_date_str and new_date_str:
                                replace = True
                                
                        if replace:
                            logger.info(f"Fuzzy update: {new_event['event_name']} replacing {existing['event_name']}")
                            self.events_cache[i] = new_event
                            self.exact_hashes.add(h)
                            
                            # Write back entire cache
                            self.storage._write_events(self.events_cache)
                            
                        return False # Handle here
                        
        # Not a duplicate
        self.exact_hashes.add(h)
        self.events_cache.append(new_event)
        return True # Tell main.py to call storage.add_event(new_event)
