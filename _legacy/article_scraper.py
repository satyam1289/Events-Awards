"""
Article Scraper - Functional implementation to fetch full text
"""

import logging
import requests
from typing import Optional, Dict, List
import config
import time
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class ArticleScraper:
    """Scraper that fetches real content from URLs to ensure accurate extraction"""
    
    def __init__(self):
        from fake_useragent import UserAgent
        self.ua = UserAgent()
    
    def get_headers(self):
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def scrape(self, url: str) -> Optional[Dict]:
        """
        Fetch the full title and body text of an article for better event extraction.
        """
        try:
            logger.info(f"Fetching real content from: {url}")
            
            # Use newspaper3k if available, otherwise fallback to basic BeautifulSoup
            try:
                from newspaper import Article, Config
                
                # Configure newspaper with dynamic headers
                config_obj = Config()
                current_headers = self.get_headers()
                config_obj.browser_user_agent = current_headers['User-Agent']
                config_obj.request_timeout = 15
                config_obj.headers = current_headers
                
                article = Article(url, config=config_obj)
                article.download()
                
                if article.download_exception_msg:
                    raise Exception(f"Download failed: {article.download_exception_msg}")
                
                logger.info(f"Newspaper3k resolved URL: {article.url}")
                article.parse()
                title = article.title
                content = article.text
            except Exception as inner_e:
                logger.warning(f"Newspaper3k failed, falling back to BeautifulSoup: {inner_e}")
                
                # Check if it was a 429 and wait a bit
                if "429" in str(inner_e):
                    import random
                    wait_time = random.uniform(5, 10)
                    logger.info(f"Rate limited (429). Sleeping for {wait_time:.1f}s...")
                    time.sleep(wait_time)

                response = requests.get(url, headers=self.get_headers(), timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.title.string if soup.title else ""
                # Get all paragraph text
                content = "\n".join([p.get_text() for p in soup.find_all('p')])
            
            return {
                'url': url,
                'title': title or '',
                'content': content or '',
                'metadata': {},
                'pub_date': ''
            }
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")

            return {
                'url': url,
                'title': '',
                'content': '',
                'metadata': {},
                'pub_date': ''
            }
    
    def scrape_multiple(self, urls: List[str], delay_range: tuple = (1, 2)) -> List[Dict]:
        """
        Scrape multiple URLs with a polite delay.
        """
        results = []
        for i, url in enumerate(urls):
            logger.info(f"Scraping real content {i+1}/{len(urls)}")
            article_data = self.scrape(url)
            if article_data:
                results.append(article_data)
            
            time.sleep(1)
        
        return results
