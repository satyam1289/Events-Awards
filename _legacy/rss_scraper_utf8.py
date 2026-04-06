"""
RSS Feed Scraper - Uses RSS feeds to fetch event-related news
"""

import requests
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict
from datetime import datetime
import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class RSSScraper:
    """Scraper using RSS feeds"""
    
    # Indian news RSS feeds relevant to events
    RSS_FEEDS = {
        'Artificial Intelligence': [
            'https://venturebeat.com/category/ai/feed/',
            'https://www.technologyreview.com/topic/artificial-intelligence/feed/',
            'https://ai.googleblog.com/feeds/posts/default',
            'https://www.scmp.com/rss/318217/feed',
            'https://spectrum.ieee.org/rss/robotics/fulltext',
            'https://inside.com/ai/feed',
            'https://www.artificialintelligence-news.com/feed/',
            'https://www.analyticsvidhya.com/feed/',
            'https://machinelearningmastery.com/feed/',
        ],
        'Technology': [
            'https://tech.economictimes.indiatimes.com/rssfeedstopstories',
            'https://www.gadgets360.com/rss',
            'https://www.medianama.com/feed/',
            'https://yourstory.com/feed',
            'https://www.techcircle.in/rss/news',
            'https://www.hindustantimes.com/rss/tech/rssfeed.xml',
            'https://entrackr.com/feed/',
            'https://digit.in/feed/',
            'https://www.livemint.com/rss/technology',
            'https://www.news18.com/rss/tech.xml',
            'https://cxotoday.com/feed/',
            'https://www.expresscomputer.in/feed/',
            'https://www.dqindia.com/feed/',
            'https://techgraph.co/feed/',
            'https://trak.in/feed/',
            'https://in.eventfaqs.com/feed/',
            'https://theprint.in/category/tech/feed/',
            'https://telecom.economictimes.indiatimes.com/rss/topstories',
            'https://www.ciol.com/feed/',
            'https://www.crn.in/feed/',
        ],
        'Events & Awards': [
            'https://in.eventfaqs.com/feed/',
            'http://everythingexperiential.businessworld.in/feed/',
            'https://www.exchange4media.com/rss/news.xml',
            'https://www.adgully.com/rss',
            'https://www.afaqs.com/rss',
            'https://www.campaignindia.in/rss',
            'https://www.medianews4u.com/feed/',
            'https://india.entrepreneur.com/feed',
            'https://www.prlog.org/in/rss.xml',
            'https://www.businesswireindia.com/rss-feeds.html', # Conceptual PR feed
            'https://www.aninews.in/rss/feed/category/business/',
        ],
        'BFSI & Fintech': [
            'https://economictimes.indiatimes.com/rssfeedtopstories.cms',
            'https://www.livemint.com/rss/markets',
            'https://www.thehindubusinessline.com/markets/stock-markets/feeder/default.rss',
            'https://bfsi.economictimes.indiatimes.com/rss/topstories',
            'https://bankingfrontiers.com/feed/',
            'https://www.financialexpress.com/business/banking-finance/feed/',
            'https://www.moneycontrol.com/rss/business.xml',
            'https://www.business-standard.com/rss/finance-103.rss',
            'https://www.bloombergquint.com/business/rss',
            'https://www.cnbctv18.com/api/v1/rss/personal-finance.xml',
            'https://www.indiainfoline.com/rss/finance',
        ],
        'Healthcare': [
            'https://health.economictimes.indiatimes.com/rssfeedstopstories',
            'https://www.financialexpress.com/lifestyle/healthcare/feed/',
            'https://www.biovoicenews.com/feed/',
            'https://www.pharmabiz.com/rss/news.xml',
            'https://www.biospectrumindia.com/rss_feed',
            'https://www.expresshealthcare.in/feed/',
            'https://medicaldialogues.in/rss.xml',
            'https://www.thehindu.com/sci-tech/health/feeder/default.rss',
        ],
        'Startups': [
            'https://startup.economictimes.indiatimes.com/rssfeedstopstories',
            'https://inc42.com/feed/',
            'https://yourstory.com/category/startups/feed',
            'https://www.indianstartupnews.com/feed',
            'https://entrackr.com/category/startups/feed/',
            'https://www.startup-times.com/feed/',
            'https://startuptalky.com/feed/',
            'https://www.vccircle.com/feed',
            'https://www.businessinsider.in/business/startups/rssfeed.cms',
            'https://pitchbook.com/rss/news',
            'https://www.nextbigwhat.com/feed/',
        ],
        'Retail & eCommerce': [
            'https://retail.economictimes.indiatimes.com/rssfeedstopstories',
            'https://www.indianretailer.com/rss/news.xml',
            'https://www.ecommercetimes.com/perl/syndication/rssfull.pl',
            'https://www.indiaretailing.com/feed/',
            'https://www.thehindubusinessline.com/economy/logistics/feeder/default.rss',
        ],
        'Marketing & MarTech': [
            'https://brandequity.economictimes.indiatimes.com/rss/topstories',
            'https://www.exchange4media.com/rss/news.xml',
            'https://marketing.economictimes.indiatimes.com/rss/topstories',
            'https://www.socialsamosa.com/feed/',
            'https://bestmediainfo.com/rss',
            'https://www.campaignindia.in/rss',
            'https://www.adgully.com/rss',
            'https://www.martechvibe.com/feed/',
            'https://www.impactonnet.com/rss/all.xml',
        ],
        'Human Resources': [
            'https://hr.economictimes.indiatimes.com/rss/topstories',
            'https://www.peoplematters.in/feeder/all',
            'https://www.shrm.org/rss/hrnews.xml',
            'https://www.hcamag.com/in/rss',
            'https://sightsinplus.com/feed/',
        ],
        'Automotive & Transport': [
            'https://auto.economictimes.indiatimes.com/rss/topstories',
            'https://www.carandbike.com/news/rss',
            'https://www.zigwheels.com/rss/news.xml',
            'https://www.autocarindia.com/rss/news.xml',
            'https://www.rushlane.com/feed',
            'https://www.motorbeam.com/feed/',
            'https://energy.economictimes.indiatimes.com/rss/topstories',
        ],
        'Government & Policy': [
            'https://cfo.economictimes.indiatimes.com/rss/topstories',
            'https://www.thehindu.com/news/national/feeder/default.rss',
            'https://pib.gov.in/rss/1.xml',
            'https://www.newindianexpress.com/Nation/rssfeed/?id=170&getXmlFeed=true',
            'https://www.prsindia.org/rss/all.xml',
        ],
        'Education': [
            'https://thehindu.com/education/feeder/default.rss',
            'https://indianexpress.com/section/education/feed/',
            'https://www.edexlive.com/rss/1',
            'https://www.freepressjournal.in/education/rss',
            'https://theprint.in/category/education/feed/',
            'https://www.careers360.com/news/feed',
        ],
        'Real Estate': [
            'https://realty.economictimes.indiatimes.com/rss/topstories',
            'https://www.magicbricks.com/blog/rss/',
            'https://www.propertytimes.in/feed/',
            'https://www.financialexpress.com/money/real-estate/feed/',
            'https://www.moneycontrol.com/rss/realestate.xml',
        ],
        'Entertainment': [
            'https://www.bollywoodhungama.com/rss/news.xml',
            'https://economictimes.indiatimes.com/magazines/panache/rssfeedstopstories.cms',
            'https://www.pinkvilla.com/rss.xml',
            'https://www.koimoi.com/feed/',
            'https://indianexpress.com/section/entertainment/feed/',
            'https://www.thehindu.com/entertainment/feeder/default.rss',
        ],
        'Sustainability & Agriculture': [
            'https://energy.economictimes.indiatimes.com/rss/topstories',
            'https://agri.economictimes.indiatimes.com/rss/topstories',
            'https://www.krishijagran.com/rss/agriculture-news',
            'https://www.downtoearth.org.in/rss.xml',
            'https://mercomindia.com/feed/',
            'https://www.saurenergy.com/feed',
        ],
        'Regional & Cities': [
            'https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms', # Mumbai
            'https://timesofindia.indiatimes.com/rssfeeds/1702690.cms', # Delhi
            'https://timesofindia.indiatimes.com/rssfeeds/3942697.cms', # Bangalore
            'https://timesofindia.indiatimes.com/rssfeeds/30359473.cms', # Hyderabad
            'https://timesofindia.indiatimes.com/rssfeeds/2950627.cms', # Chennai
            'https://timesofindia.indiatimes.com/rssfeeds/3947726.cms', # Pune
            'https://timesofindia.indiatimes.com/rssfeeds/-2128821151.cms', # Ahmedabad
            'https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms', # Kochi
            'https://timesofindia.indiatimes.com/rssfeeds/3947060.cms', # Lucknow
            'https://indianexpress.com/section/cities/mumbai/feed/',
            'https://indianexpress.com/section/cities/pune/feed/',
            'https://indianexpress.com/section/cities/bangalore/feed/',
            'https://indianexpress.com/section/cities/chennai/feed/',
            'https://www.rajasthanchronicle.com/rss/category/Jaipur',
            'https://www.amarujala.com/rss/lucknow.xml',
            'https://www.tribuneindia.com/rss/chandigarh',
            'https://deccanchronicle.com/rss', # South India Focus
        ],
        'General': [
            'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
            'https://www.indianexpress.com/rss/latest-news.xml',
            'https://www.thehindu.com/feeder/default.rss',
            'https://www.news18.com/rss/india.xml',
            'https://www.deccanherald.com/rss/national.rss',
            'https://www.firstpost.com/rss/india.xml',
            'https://www.business-standard.com/rss/latest.rss',
            'https://www.wionews.com/feeds/news/india.xml',
            'https://english.jagran.com/rss/india',
            'https://www.ndtv.com/rss/topstories',
            'https://thewire.in/rss',
            'https://scroll.in/rozetl/feed',
        ]
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT
        })
    
    def fetch_feed(self, url: str) -> List[Dict]:
        """Fetch and parse a single RSS feed"""
        articles = []
        try:
            logger.info(f"📡 REAL-TIME: Fetching RSS feed -> {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            parsed_count = 0
            # Handle RSS 2.0
            if root.tag == 'rss' or 'rss' in root.tag:
                channel = root.find('channel')
                if channel is not None:
                    for item in channel.findall('item'):
                        article = self._parse_rss_item(item)
                        if article:
                            articles.append(article)
                            parsed_count += 1
            
            # Handle Atom
            elif 'feed' in root.tag:
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    article = self._parse_atom_entry(entry)
                    if article:
                        articles.append(article)
                        parsed_count += 1
            
            logger.info(f"✅ Success: Parsed {parsed_count} items from {url}")
            
        except Exception as e:
            logger.error(f"❌ Error fetching {url}: {e}")
        
        return articles
    
    def _decode_google_news_url(self, link: str) -> str:
        """Decode Google News obfuscated URLs to their original source"""
        if 'news.google.com/rss/articles' in link or 'news.google.com/articles' in link:
            try:
                from googlenewsdecoder import new_decoderv1
                decoded = new_decoderv1(link)
                if decoded and isinstance(decoded, dict) and decoded.get('status'):
                    return decoded.get('decoded_url')
            except ImportError:
                logger.debug("googlenewsdecoder not installed. Falling back to original URL.")
            except Exception as e:
                logger.debug(f"Failed to decode google news url {link}: {e}")
        return link
        
    
    def _parse_rss_item(self, item) -> Dict:
        """Parse RSS item element"""
        try:
            title = item.findtext('title', '')
            link = self._decode_google_news_url(item.findtext('link', ''))
            
            # Try to get full content from namespaces often used in RSS
            content_encoded = item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded')
            if content_encoded:
                description = content_encoded
            else:
                description = item.findtext('description', '')
                
            pub_date = item.findtext('pubDate', '')
            
            # Additional clean up on description
            dec_clean = self._clean_html(description)
            # Ensure it's substantial, otherwise it might just be a headline repeated
            if len(dec_clean) < 50:
                 dec_clean = description
            
            return {
                'title': self._clean_html(title),
                'link': link,
                'description': self._clean_html(description),
                'content_raw': description, # keep raw for later extraction
                'date_str': pub_date,
                'source': 'RSS Feed'
            }
        except Exception as e:
            logger.debug(f"Error parsing RSS item: {e}")
            return None
    
    def _parse_atom_entry(self, entry) -> Dict:
        """Parse Atom entry element"""
        try:
            title = entry.findtext('title', '')
            link_elem = entry.find('link')
            link = self._decode_google_news_url(link_elem.get('href') if link_elem is not None else '')
            
            # Try full content first
            content_elem = entry.find('{http://www.w3.org/2005/Atom}content')
            description = ''
            if content_elem is not None and content_elem.text:
                description = content_elem.text
            else:
                description = entry.findtext('{http://www.w3.org/2005/Atom}summary', '')
            
            pub_date = entry.findtext('{http://www.w3.org/2005/Atom}published', 
                                     entry.findtext('{http://www.w3.org/2005/Atom}updated', ''))
            
            return {
                'title': self._clean_html(title),
                'link': link,
                'description': self._clean_html(description),
                'content_raw': description,
                'date_str': pub_date,
                'source': 'RSS Feed'
            }
        except Exception as e:
            logger.debug(f"Error parsing Atom entry: {e}")
            return None
    
    def fetch_feed_with_feedparser(self, url: str) -> List[Dict]:
        """Alternative fetch using feedparser library which handles malformed feeds better"""
        try:
            import feedparser
            logger.info(f"📡 REAL-TIME: Fetching via FeedParser -> {url}")
            feed = feedparser.parse(url)
            
            if feed.bozo and hasattr(feed, 'bozo_exception'):
                logger.debug(f"Feedparser warning for {url}: {feed.bozo_exception}")
                # Sometimes it fails completely, sometimes it parses partial
            
            articles = []
            for entry in feed.entries:
                title = getattr(entry, 'title', '')
                link = self._decode_google_news_url(getattr(entry, 'link', ''))
                
                # Check multiple places for content
                description = ''
                if hasattr(entry, 'content') and len(entry.content) > 0:
                    description = entry.content[0].value
                elif hasattr(entry, 'summary'):
                    description = entry.summary
                elif hasattr(entry, 'description'):
                    description = entry.description
                    
                pub_date = getattr(entry, 'published', getattr(entry, 'updated', ''))
                
                if title:
                    articles.append({
                        'title': self._clean_html(title),
                        'link': link,
                        'description': self._clean_html(description),
                        'content_raw': description, 
                        'date_str': pub_date,
                        'source': 'RSS Feed'
                    })
                    
            logger.info(f"✅ Success: Parsed {len(articles)} via Feedparser from {url}")
            return articles
            
        except ImportError:
            logger.warning("feedparser not installed. Please run: pip install feedparser")
            return self.fetch_feed(url) # fallback
        except Exception as e:
            logger.error(f"❌ Feedparser error fetching {url}: {e}")
            return []

    def fetch_feed_smart(self, url: str) -> List[Dict]:
        """Attempts smart fetching using standard requests+xml, falls back to feedparser"""
        try:
            # First try our standard approach which is faster
            articles = self.fetch_feed(url)
            if not articles: # If 0, could be malformed, try feedparser
                articles = self.fetch_feed_with_feedparser(url)
            return articles
        except Exception:
            return self.fetch_feed_with_feedparser(url)

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags and entities from text"""
        if not text:
            return ''
        import html
        import re
        # Unescape HTML entities first (e.g., &lt; to <)
        text = html.unescape(text)
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', ' ', text)
        # Remove extra whitespace
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()
    
    def fetch_all_feeds(self, category: str = None) -> List[Dict]:
        """Fetch from all feeds or specific category"""
        all_articles = []
        
        feeds_to_fetch = self.RSS_FEEDS if category is None else {category: self.RSS_FEEDS.get(category, [])}
        
        for cat, feeds in feeds_to_fetch.items():
            for feed_url in feeds:
                # Use smart fetching instead of basic fetch_feed
                articles = self.fetch_feed_smart(feed_url)
                for article in articles:
                    article['category'] = cat
                all_articles.extend(articles)
        
        return all_articles
        
    def search_feeds(self, keyword: str) -> List[Dict]:
        """Search for keyword in all feeds"""
        all_articles = self.fetch_all_feeds()
        
        keyword_lower = keyword.lower()
        filtered = [
            a for a in all_articles 
            if keyword_lower in a.get('title', '').lower() or 
               keyword_lower in a.get('description', '').lower()
        ]
        
        return filtered


def test_rss():
    """Test RSS scraper"""
    scraper = RSSScraper()
    
    # Test fetching one feed
    articles = scraper.fetch_feed(scraper.RSS_FEEDS['General'][0])
    
    print(f"Found {len(articles)} articles")
    for article in articles[:3]:
        print(f"Title: {article.get('title', 'N/A')[:60]}")
        print("---")


if __name__ == "__main__":
    test_rss()

