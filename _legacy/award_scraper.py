"""
Award Scraper - Scrapes awards directly from official award portals (ET BrandEquity, Afaqs, etc.)
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict
import config
import re

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class DirectAwardScraper:
    """Scrapes awards directly from known award listing websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT
        })

    def scrape_et_brandequity(self) -> List[Dict]:
        """Scrape awards from ET BrandEquity"""
        url = "https://brandequity.economictimes.indiatimes.com/awards"
        awards = []
        try:
            logger.info(f"Direct scraping ET BrandEquity Awards: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Subagent pattern: a.awards-with-editions__item--top
            items = soup.select('a.awards-with-editions__item--top')
            
            for item in items:
                title_elem = item.find('h3')
                if not title_elem: continue
                
                title = title_elem.get_text(strip=True)
                link = item['href']
                if not link.startswith('http'):
                    link = "https://brandequity.economictimes.indiatimes.com" + link
                
                # Try to find date next to description
                parent = item.find_parent('div')
                date_str = ""
                if parent:
                    # Look for date patterns (e.g., "Nominations open till Mar 10 2026")
                    text = parent.get_text(separator=' ', strip=True)
                    date_match = re.search(r'(?:Nominations|Open|till|on)\s*(?:\w+,\s*)?\d{1,2}\s+\w+\s+\d{4}', text, re.I)
                    if date_match:
                        date_str = date_match.group(0)
                
                awards.append({
                    'event_name': title,
                    'sector': 'Marketing & MarTech', # ET BrandEquity is marketing focused
                    'type': 'Award',
                    'date': date_str,
                    'location': 'India',
                    'source_title': 'ET BrandEquity Awards',
                    'source_url': link,
                    'confidence': 100
                })
        except Exception as e:
            logger.error(f"ET BrandEquity direct scrape failed: {e}")
            
        return awards

    def scrape_afaqs(self) -> List[Dict]:
        """Scrape awards from afaqs! events"""
        url = "https://events.afaqs.com/"
        awards = []
        try:
            logger.info(f"Direct scraping afaqs! Awards: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Subagent pattern: .card
            cards = soup.select('.card')
            
            for card in cards:
                img = card.find('img')
                title = img['alt'] if img and img.has_attr('alt') else "Afaqs Award"
                
                category = card.find('h5')
                if category and "Awards" not in category.get_text():
                    # If it's a summit only, we still include if name implies award
                    pass
                
                link_elem = card.select_one('a.btn-dark')
                link = link_elem['href'] if link_elem else url
                
                date_elem = card.find('p')
                date_str = date_elem.get_text(strip=True) if date_elem else ""
                
                awards.append({
                    'event_name': title,
                    'sector': 'Media',
                    'type': 'Award',
                    'date': date_str,
                    'location': 'India',
                    'source_title': 'afaqs! Events',
                    'source_url': link,
                    'confidence': 100
                })
        except Exception as e:
            logger.error(f"afaqs! direct scrape failed: {e}")
            
        return awards

    def scrape_all(self) -> List[Dict]:
        """Run all direct award scrapers"""
        all_awards = []
        all_awards.extend(self.scrape_et_brandequity())
        all_awards.extend(self.scrape_afaqs())
        return all_awards
