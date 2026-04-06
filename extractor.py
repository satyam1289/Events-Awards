import re
import logging
import dateparser
from datetime import datetime
import config

logger = logging.getLogger(__name__)

class EventExtractor:
    """Refined Event Extractor focused on Name, Date, and Venue (v5.6 Precision)."""

    def __init__(self):
        self.year = "2026"
        self.event_keywords = ["summit", "conference", "award", "expo", "forum", "conclave", 
                               "ceremony", "workshop", "hackathon", "convention", "festival",
                               "meetup", "webinar", "roundtable", "exhibition"]

    def extract_name(self, title: str, snippet: str = "") -> str:
        """Extract a clean event name by looking for Capitalized Clusters around keywords."""
        text = f"{title} {snippet}"
        # Remove SEO noise
        clean_text = re.sub(r'\s+[|:–-]\s+.*$', '', title)
        
        # 1. Search for keyword-centered clusters
        for kw in self.event_keywords:
            if kw.lower() in clean_text.lower():
                # Find the keyword
                match = re.search(re.escape(kw), clean_text, re.IGNORECASE)
                if not match: continue
                
                # Look back for capitalized words (Proper Nouns)
                before = clean_text[:match.start()].strip().split()
                name_parts = []
                for word in reversed(before):
                    if word and (word[0].isupper() or word.lower() in ['and', 'of', 'the', '&', 'for']):
                        name_parts.insert(0, word)
                    else:
                        break
                
                # Look forward for year or edition
                after = clean_text[match.end():].strip().split()
                after_parts = []
                for word in after:
                    if re.match(r'^(20\d{2}|\d\.\d|Edition)$', word) or word[0].isupper():
                        after_parts.append(word)
                    else:
                        break
                
                name = " ".join(name_parts + [match.group(0)] + after_parts)
                if len(name.split()) >= 2:
                    return name.strip()

        # 2. Fallback: Take the first 5-7 words if they look like a title
        words = clean_text.split()
        return " ".join(words[:min(len(words), 7)]).strip()

    def extract_date(self, text: str) -> str:
        """Multi-format date extraction with high-precision normalization for 2026."""
        # 1. Normalize year 2026 consistency (ignore 2025/2024 for this engine)
        text = text.replace("2025", "2026").replace("2027", "2026")
        
        # 2. Comprehensive High-Precision Patterns
        patterns = [
            # Full Range: 24-26 March 2026 or 24 to 26 March 2026
            r'\b(\d{1,2}(?:\s*[-–]| to )\d{1,2})\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+2026\b',
            # Full Date: 24 March 2026 or 24th March 2026
            r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+,?\s*2026\b',
            # Month First: March 24, 2026 or March 24-26 2026
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:\s*[-–]\s*\d{1,2})?,?\s+2026\b',
            # Slash/Dot Formats: 24/03/2026 or 24.03.2026
            r'\b\d{1,2}[./-]\d{1,2}[./-]2026\b'
        ]
        
        for p in patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                raw_date = match.group(0)
                # If it's a range (24-26 March), dateparser might struggle, so take the first day
                range_match = re.search(r'(\d{1,2})[-– to]+', raw_date)
                if range_match and "OR" not in raw_date:
                    first_day = range_match.group(1)
                    clean_date = re.sub(r'\d{1,2}(?:\s*[-–]| to )\d{1,2}', first_day, raw_date)
                    parsed = dateparser.parse(clean_date)
                else:
                    parsed = dateparser.parse(raw_date)
                
                if parsed:
                    return parsed.strftime("%d/%m/%Y")
        
        # 3. Fallback: Month + Year
        month_year = re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+2026\b', text, re.IGNORECASE)
        if month_year:
            parsed = dateparser.parse(month_year.group(0))
            if parsed:
                return parsed.strftime("01/%m/%Y") # Default to 1st
        
        # 4. Final Fallback: Search for "starting [Month]"
        start_month = re.search(r'starting\s+(?:in\s+)?([A-Z][a-z]+)\s+2026', text, re.IGNORECASE)
        if start_month:
            parsed = dateparser.parse(f"01 {start_month.group(1)} 2026")
            if parsed:
                return parsed.strftime("01/%m/%Y")

        return ""

    def extract_venue(self, text: str) -> str:
        """Extract specific venue names using 'at/in [Venue]' patterns."""
        venue_patterns = [
            r'(?:at|venue|location)\s+:?\s*([A-Z][a-z]+\s+(?:Hotel|Convention|Centre|Center|Hall|Arena|Stadium|Palace|Grounds|Expo))',
            r'(?:held at|taking place at)\s+([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        
        for p in venue_patterns:
            match = re.search(p, text)
            if match:
                return match.group(1).strip()
                
        # Fallback to direct city check
        for city in config.CITIES:
            if city.lower() in text.lower():
                return city
        
        return "India"

    def refine_all(self, title: str, snippet: str, url: str = "") -> dict:
        """Consolidated extraction for daily discovery."""
        combined = f"{title} {snippet}"
        return {
            "event_name": self.extract_name(title, snippet),
            "date": self.extract_date(combined),
            "venue": self.extract_venue(combined),
            "source_url": url
        }
