"""
Direct Scraper - Scrapes events directly from official industrial bodies (CII, FICCI, NASSCOM)
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict
from datetime import datetime
import config
import re

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class DirectScraper:
    """Scrapes events directly from known official websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT
        })

    def scrape_nasscom(self) -> List[Dict]:
        """Scrape events from NASSCOM"""
        url = "https://nasscom.in/events"
        events = []
        try:
            logger.info(f"📡 REAL-TIME: Scrutinizing Institutional Calendar -> NASSCOM: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            logger.info("✅ Success: Connection established with NASSCOM.")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find event cards - based on subagent analysis
            # Selector derived from subagent: .forthcoming-events .card or similar
            cards = soup.select('.views-element-container .card') or soup.find_all('div', class_='card')
            
            for card in cards:
                title_elem = card.find('h3') or card.find('a', href=True)
                if not title_elem: continue
                
                title = title_elem.get_text(strip=True)
                link = ""
                if card.find('a', href=True):
                    link = card.find('a', href=True)['href']
                    if not link.startswith('http'):
                        link = "https://nasscom.in" + link
                
                # Date and location are often in specific divs or spans
                date_str = ""
                location = ""
                
                details = card.find('div', class_='event-details') or card
                text = details.get_text(separator=' ', strip=True)
                
                # Attempt regex for date (e.g., "6 May 2026")
                date_match = re.search(r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}', text)
                if date_match:
                    date_str = date_match.group(0)
                
                # Simple city check for location
                if hasattr(config, 'CITIES'):
                    for city in config.CITIES:
                        if city.lower() in text.lower():
                            location = city
                            break
                
                events.append({
                    'event_name': title,
                    'sector': 'Technology', # NASSCOM is tech-focused
                    'date': date_str,
                    'location': location or 'India',
                    'source_title': 'NASSCOM Official',
                    'source_url': link or url,
                    'confidence': 100 # Direct source
                })
        except Exception as e:
            logger.error(f"NASSCOM direct scrape failed: {e}")
            
        return events

    def scrape_cii(self) -> List[Dict]:
        """Scrape events from CII"""
        url = "https://www.cii.in/CII_Events.aspx"
        events = []
        try:
            logger.info(f"📡 REAL-TIME: Scrutinizing Institutional Calendar -> CII: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            logger.info("✅ Success: Connection established with CII.")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Subagent found a table: #GdvEvents
            table = soup.find('table', id=lambda x: x and 'GdvEvents' in x)
            if not table:
                # Fallback to any table if ID search fails
                table = soup.find('table')
                
            if table:
                rows = table.find_all('tr')[1:] # Skip header
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        title_elem = cols[1].find('a')
                        title = title_elem.get_text(strip=True) if title_elem else cols[1].get_text(strip=True)
                        link = title_elem['href'] if title_elem and 'href' in title_elem.attrs else url
                        if link != url and not link.startswith('http'):
                            link = "https://www.cii.in/" + link
                            
                        date_val = cols[2].get_text(strip=True)
                        location_val = cols[3].get_text(strip=True)
                        
                        events.append({
                            'event_name': title,
                            'sector': 'General Business',
                            'date': date_val,
                            'location': location_val,
                            'source_title': 'CII Official',
                            'source_url': link,
                            'confidence': 100
                        })
        except Exception as e:
            logger.error(f"CII direct scrape failed: {e}")
            
        return events

    def scrape_ficci(self) -> List[Dict]:
        """Scrape events from FICCI"""
        url = "https://ficci.in/event"
        events = []
        try:
            logger.info(f"📡 REAL-TIME: Scrutinizing Institutional Calendar -> FICCI: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            logger.info("✅ Success: Connection established with FICCI.")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Subagent analysis: .event-card-wrapper
            card_wrappers = soup.select('.event-card-wrapper') or soup.find_all('div', class_='events-list')
            
            for wrapper in card_wrappers:
                title_elem = wrapper.find('h3')
                if not title_elem: continue
                
                title = title_elem.get_text(strip=True)
                link_elem = wrapper.find('a', href=True)
                link = link_elem['href'] if link_elem else url
                if link != url and not link.startswith('http'):
                    link = "https://ficci.in" + link
                
                # Details box usually contains P tags with info
                details = wrapper.select('.details-box p') or wrapper.find_all('p')
                date_val = ""
                location_val = ""
                
                if len(details) >= 1:
                    date_val = details[0].get_text(strip=True)
                if len(details) >= 2:
                    location_val = details[1].get_text(strip=True)
                
                events.append({
                    'event_name': title,
                    'sector': 'General Business',
                    'date': date_val,
                    'location': location_val,
                    'source_title': 'FICCI Official',
                    'source_url': link,
                    'confidence': 100
                })
        except Exception as e:
            logger.error(f"FICCI direct scrape failed: {e}")
            
        return events

    def scrape_all(self) -> List[Dict]:
        """Run all direct scrapers"""
        all_events = []
        all_events.extend(self.scrape_nasscom())
        all_events.extend(self.scrape_cii())
        all_events.extend(self.scrape_ficci())
        return all_events
