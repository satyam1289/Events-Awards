"""
Google News Scraper - Fetches search results using RSS and GDELT
"""

import requests
import time
import logging
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
import urllib.parse
import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class GoogleNewsScraper:
    """Uses RSS and GDELT instead of scraping HTML."""
    
    def search(self, query: str, num_pages: int = 1) -> List[Dict]:
        """
        Search for a query using RSS and GDELT 
        (num_pages is ignored as we rely on APIs now)
        """
        results = []
        
        # 1. Fetch from Google News RSS
        rss_results = self._fetch_rss(query)
        logger.info(f"Found {len(rss_results)} results from RSS for '{query}'")
        results.extend(rss_results)
        
        # 2. Fetch from GDELT DOC API (Article List mode)
        gdelt_results = self._fetch_gdelt(query)
        logger.info(f"Found {len(gdelt_results)} results from GDELT for '{query}'")
        results.extend(gdelt_results)
        
        return results

    def _fetch_rss(self, query: str) -> List[Dict]:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
        results = []
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            root = ET.fromstring(r.text)
            
            items = []
            for item in root.findall('.//item'):
                title = item.findtext('title')
                link = item.findtext('link')
                pubDate = item.findtext('pubDate')
                description = item.findtext('description')
                source = item.findtext('source')
                if title and link:
                    items.append({
                        'title': title,
                        'link': link,
                        'description': description or '',
                        'source': source or 'Google News RSS',
                        'date_str': pubDate or ''
                    })
            
            # Resolve redirects concurrently
            import concurrent.futures
            
            def resolve_link(item_dict):
                link = item_dict['link']
                final_link = link
                if 'news.google.com' in link:
                    try:
                        with requests.get(link, allow_redirects=True, timeout=5, stream=True) as res:
                            final_link = res.url
                        
                        # Only log every 10th one to avoid log spam, but we are resolving all
                        if final_link != link and random.random() < 0.1:
                            logger.info(f"🔗 Resolved: {link[:30]}... -> {final_link}")
                    except Exception as res_e:
                        pass
                item_dict['link'] = final_link
                return item_dict
                
            import random
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                resolved_items = list(executor.map(resolve_link, items))
                
            results = resolved_items
            
        except Exception as e:
            logger.error(f"Error fetching RSS for {query}: {e}")
            
        return results
        
    def _fetch_gdelt(self, query: str) -> List[Dict]:
        url = "https://api.gdeltproject.org/api/v2/doc/doc"
        results = []
        params = {
            'query': query,
            'mode': 'artlist',
            'format': 'json',
            'maxrecords': 250,
            'sort': 'datedesc'
        }
        try:
            r = requests.get(url, params=params, timeout=30)
            if r.status_code == 200:
                data = r.json()
                if 'articles' in data:
                    for art in data['articles']:
                        results.append({
                            'title': art.get('title', ''),
                            'link': art.get('url', ''),
                            'description': art.get('seendescription', '') or art.get('title', ''),
                            'source': art.get('domain', 'GDELT'),
                            'date_str': art.get('seendate', '')
                        })
        except Exception as e:
            logger.error(f"Error fetching GDELT for {query}: {e}")
            
        return results

    def search_multiple_queries(self, queries: List[str], max_pages: int = 1) -> List[Dict]:
        all_results = []
        seen_links = set()
        
        for query in queries:
            results = self.search(query, num_pages=max_pages)
            for result in results:
                if result['link'] not in seen_links:
                    seen_links.add(result['link'])
                    all_results.append(result)
            time.sleep(1)
            
            # Using EventBrite logic inside the scraper too to boost count
            eventbrite_res = self._fetch_eventbrite(query)
            for result in eventbrite_res:
                if result['link'] not in seen_links:
                    seen_links.add(result['link'])
                    all_results.append(result)
                    
        return all_results

    def _fetch_eventbrite(self, query: str) -> List[Dict]:
        results = []
        try:
            # Note: Eventbrite v3 API uses OAuth tokens
            token = "HA5T7HOEBOM7I25OM5HN"  # Provided Private Token
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            # Remove "India" from query to make it a better keyword search
            clean_query = query.replace(" India", "").replace(" 2026", "")
            
            # Note: Eventbrite's event search might require Organization ID or specific endpoints based on current API scopes
            # The general event search endpoint is often deprecated or restricted.
            # Using the /v3/events/search/ if it's available for the token, or handling gracefully.
            res = requests.get(
                "https://www.eventbriteapi.com/v3/events/search/",
                headers=headers,
                params={"q": clean_query, "location.address": "India"},
                timeout=10
            )

            if res.status_code == 200:
                data = res.json()
                events = data.get("events", [])
                for evt in events:
                    title = evt.get("name", {}).get("text", "")
                    url = evt.get("url", "")
                    description = evt.get("description", {}).get("text", "")
                    date_val = evt.get("start", {}).get("local", "")
                    
                    if title and url:
                        results.append({
                            'title': title,
                            'link': url,
                            'description': description or title,
                            'source': 'Eventbrite',
                            'date_str': date_val
                        })
            else:
                logger.debug(f"Eventbrite API warning: {res.status_code} - {res.text}")
        except Exception as e:
            logger.error(f"Error fetching Eventbrite: {str(e)}")
            
        return results

def test_scraper():
    """Test the scraper with a simple query"""
    scraper = GoogleNewsScraper()
    results = scraper.search("AI conference India", num_pages=1)
    print(f"Found {len(results)} results")
    for r in results[:3]:
        print(f"Title: {r.get('title')}")
        print(f"Link: {r.get('link')}")
        print(f"Description: {r.get('description')}")
        print("---")

if __name__ == "__main__":
    test_scraper()

