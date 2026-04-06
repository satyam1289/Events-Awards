from free_sources_scraper import scrape_all_free_sources, scrape_rss_feeds, scrape_google_news_rss
import logging

logging.basicConfig(level=logging.INFO)

print("--- Testing Free Sources ---")
results = scrape_all_free_sources()
print(f"Scraped {len(results)} raw results from free sources.")

print("\n--- Testing RSS Feeds ---")
rss_results = scrape_rss_feeds()
print(f"Scraped {len(rss_results)} results from RSS.")

print("\n--- Testing Google News RSS ---")
gn_results = scrape_google_news_rss()
print(f"Scraped {len(gn_results)} results from Google News.")
