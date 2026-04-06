
import requests
from bs4 import BeautifulSoup
import time
import random
import logging
import urllib.parse
import re
import config
from storage import EventStorage
import xml.etree.ElementTree as ET
from typing import List, Dict, Set

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class SERPDiscovery:
    """Discovers event URLs via Google Search results with aggressive fallbacks"""
    
    def __init__(self):
        self.storage = EventStorage()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
        ]
        self.blacklist = [
            'youtube.com', 'facebook.com', 'instagram.com', 'twitter.com', 'linkedin.com',
            'wikipedia.org', 'pinterest.com', 'amazon.', 'flipkart.com', 'maps.google.com',
            'shopping.google.com', '.pdf', '.docx', '.pptx', 'google.com/search'
        ]
        # Refresh seen URLs from storage
        self.seen_urls = self._load_seen_urls()

    def _load_seen_urls(self) -> Set[str]:
        """Load already processed URLs to avoid duplicates"""
        events = self.storage.get_all_events()
        return {e.get('source_url') for e in events if e.get('source_url')}

    def generate_queries(self) -> List[str]:
        """Generate high-potential search queries based on config"""
        queries = []
        event_types = ['summit', 'conference', 'expo', 'forum', 'awards', 'exhibition', 'symposium']
        sectors = list(config.SECTORS.keys())
        cities = config.CITIES
        
        # Shuffle for variety
        random.shuffle(sectors)
        random.shuffle(cities)
        random.shuffle(event_types)
        
        patterns = [
            "{sector} {event_type} {location} 2026",
            "{sector} event {location} 2026",
            "upcoming {sector} {event_type} India",
            "{sector} awards ceremony India 2026",
            "{sector} {event_type} Bangalore Mumbai Delhi"
        ]
        
        for sector in sectors[:10]:
            for location in cities[:5]:
                pattern = random.choice(patterns)
                query = pattern.format(
                    sector=sector,
                    event_type=random.choice(event_types),
                    location=location
                )
                queries.append(query)
                
        random.shuffle(queries)
        return list(set(queries)) # Unique queries

    def fetch_serp(self, query: str, page: int = 1) -> List[Dict]:
        """
        Fetch search results with multiple fallback strategies
        1. Organic Google Search (HTML)
        2. Google News RSS (XML) - Highly reliable fallback
        """
        results = []
        
        # Strategy 1: Attempt Organic HTML (often blocked but has more variety)
        # We use a slight variation to avoid simple bot detection
        start = (page - 1) * 10
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&start={start}&hl=en"
        
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        }
        
        try:
            time.sleep(random.uniform(2, 5))
            response = requests.get(search_url, headers=headers, timeout=15)
            
            if response.status_code == 200 and "div" in response.text:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Google changes classes but <h3> inside <a> or near it is stable
                for h3 in soup.find_all('h3'):
                    # Find the nearest <a> tag
                    link_tag = h3.find_parent('a') or h3.find_next_sibling('a') or (h3.parent.find('a') if h3.parent else None)
                    
                    if link_tag and link_tag.has_attr('href'):
                        url = link_tag['href']
                        # Handle Google redirect links
                        if url.startswith('/url?q='):
                            url = url.split('/url?q=')[1].split('&')[0]
                            url = urllib.parse.unquote(url)
                            
                        if self._is_valid_url(url):
                            results.append({
                                'url': url,
                                'title': h3.get_text(),
                                'snippet': "" # Extracting snippet accurately from changing HTML is hard
                            })
                            
            if results:
                logger.info(f"   [Organic] Found {len(results)} results for '{query}'")
                return results
                
        except Exception as e:
            logger.debug(f"Organic search failed for {query}: {e}")

        # Strategy 2: Google RSS Fallback (Technically still Google Search results)
        if not results:
            rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
            try:
                r = requests.get(rss_url, timeout=10)
                if r.status_code == 200:
                    root = ET.fromstring(r.text)
                    for item in root.findall('.//item'):
                        url = item.findtext('link')
                        title = item.findtext('title')
                        if url and self._is_valid_url(url):
                            results.append({
                                'url': url,
                                'title': title,
                                'snippet': item.findtext('description') or ""
                            })
                    if results:
                        logger.info(f"   [RSS-Fallback] Found {len(results)} results for '{query}'")
            except Exception as e:
                logger.error(f"RSS fallback failed for {query}: {e}")
                
        return results

    def _is_valid_url(self, url: str) -> bool:
        """Filter out garbage tags and blacklisted domains"""
        if not url or not url.startswith('http'):
            return False
        if any(bad in url.lower() for bad in self.blacklist):
            return False
        if url in self.seen_urls:
            return False
        return True

    def run_discovery(self, query_limit: int = 10) -> List[Dict]:
        """Main execution loop for SERP discovery"""
        queries = self.generate_queries()
        logger.info(f"Generated {len(queries)} potential queries. Running {query_limit}...")
        
        discovered_urls = []
        
        for query in queries[:query_limit]:
            logger.info(f"🔍 Discovery Search: '{query}'")
            # We only do 1 page for now to maximize query variety
            page_results = self.fetch_serp(query, page=1)
            discovered_urls.extend(page_results)
            
            # Avoid rapid fire
            time.sleep(random.uniform(3, 6))
            
            # Update seen list to avoid duplicate discovery in same run
            for item in page_results:
                self.seen_urls.add(item['url'])
            
        logger.info(f"Discovery phase complete. Total unique URLs discovered: {len(discovered_urls)}")
        return discovered_urls

if __name__ == "__main__":
    discovery = SERPDiscovery()
    # Test run
    discovery.run_discovery(query_limit=2)
