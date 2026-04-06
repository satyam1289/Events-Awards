import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, quote
import logging
import config

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": config.USER_AGENT
}

# Fix 5 — List of known event listing pages
FREE_SOURCES = [
    {"name": "10times", "url": "https://10times.com/india"},
    {"name": "nasscom", "url": "https://nasscom.in/events"},
    {"name": "ficci", "url": "https://ficci.in/events.asp"},
    {"name": "inc42", "url": "https://inc42.com/events/"},
    {"name": "yourstory", "url": "https://yourstory.com/events"},
    {"name": "cii", "url": "https://www.cii.in/Events.aspx"}
]

def scrape_free_source(source: dict) -> list:
    """Fetch known event listing pages and extract headings (Fix 5)."""
    results = []
    logger.info(f"🔍 Scraping free source: {source['name']}...")
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return results
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Extract headings that contain event words
        EVENT_SIGNALS = ["summit", "conference", "award", "expo", "forum", "conclave", "ceremony", "workshop", "hackathon"]
        
        for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
            text = heading.get_text(strip=True)
            if any(s in text.lower() for s in EVENT_SIGNALS) and len(text) > 5 and len(text) < 150:
                # Extract surrounding text (parents/siblings) for context
                parent = heading.parent
                context = parent.get_text(separator=" ", strip=True) if parent else text
                
                # Link extraction
                link_tag = heading.find("a") or (heading.parent.find("a") if heading.parent else None)
                link = link_tag["href"] if link_tag and link_tag.get("href") else source["url"]
                if link.startswith("/"):
                    base = urlparse(source["url"])
                    link = f"{base.scheme}://{base.netloc}{link}"
                
                results.append({
                    "title": text,
                    "snippet": context[:400],
                    "link": link,
                    "displayLink": source["name"],
                    "free_source": True,
                    "source_type": "free_scrape",
                    "confidence": 60 # Base confidence for free-scrape items
                })
    except Exception as e:
        logger.error(f"Free source {source['name']} failed: {e}")
    return results

def scrape_google_news_rss() -> list:
    """Use Google News RSS for free real-time context (Fix 5)."""
    all_results = []
    logger.info("🔍 Fetching Google News RSS...")
    
    # Fix 8 — Year 2026
    year = "2026"
    NEWS_QUERIES = [
        f"India awards {year} nominations open",
        f"NASSCOM FICCI CII events {year}",
        f"Economic Times awards {year}",
        f"startup awards India {year}"
    ]
    
    for query in NEWS_QUERIES:
        encoded = quote(query)
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            root = ET.fromstring(resp.content)
            for item in root.iter("item"):
                title = item.findtext("title", "")
                description = item.findtext("description", "")
                link = item.findtext("link", "")
                
                EVENT_SIGNALS = ["summit", "conference", "award", "expo", "forum", "conclave", "ceremony", "workshop", "hackathon", "nomination", "register"]
                if any(s in (title + description).lower() for s in EVENT_SIGNALS):
                    all_results.append({
                        "title": title,
                        "snippet": description[:300],
                        "link": link,
                        "displayLink": "news.google.com",
                        "free_source": True,
                        "source_type": "rss",
                        "confidence": 40 # Lower base for RSS snippets
                    })
        except Exception as e:
            logger.error(f"Google News RSS failed for '{query}': {e}")
            
    return all_results

from concurrent.futures import ThreadPoolExecutor

def scrape_all_free_sources() -> list:
    """Run all free discovery layers (Fix 5)."""
    all_results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 1. Scrape known platforms
        futures_scrape = [executor.submit(scrape_free_source, s) for s in FREE_SOURCES]
        # 2. Scrape News RSS
        future_news = executor.submit(scrape_google_news_rss)
        
        for future in futures_scrape:
            all_results.extend(future.result())
        all_results.extend(future_news.result())
            
    return all_results
