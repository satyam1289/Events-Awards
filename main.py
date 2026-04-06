import logging
import config
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from query_engine import QueryEngine
from serper_search_client import SerperSearchClient
from result_processor import ResultProcessor
from deduplicator import Deduplicator
from storage import EventStorage
from telegram_alert import send_alert, should_alert

# Fix 5 — Import from free scraper
from free_sources_scraper import scrape_all_free_sources

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EventDiscoveryPipeline:
    def __init__(self):
        self.query_engine = QueryEngine()
        self.google_client = SerperSearchClient()
        self.processor = ResultProcessor()
        self.storage = EventStorage()
        self.deduplicator = Deduplicator(self.storage)
        
        logger.info("Initialized Elite Discovery Engine (v5.5 Elite)")

    def run_free_discovery(self):
        """Disabled: User requested only Serper API usage."""
        logger.info("ℹ️ Phase 1 (Free Discovery) is disabled as per configuration.")
        return 0

    def run(self, sector: str = None, on_progress: callable = None, force_no_cache: bool = False, **kwargs):
        """Main discovery run focused on high-signal Serper queries."""
        total_events = 0

        # Step 1: Run Serper queries based on budget (Fix 7)
        queries = self.query_engine.get_daily_budget_allocation()
        
        if sector:
            queries = [q for q in queries if q['sector'].lower() == sector.lower()]
            
        if not queries:
            logger.info("No Serper queries scheduled for today (or budget exhausted).")
            return total_events

        # Fix 3: Inform user of the 80-query hard cap per run
        logger.info(f"🚀 High-Signal Serper Discovery (Limit: 80 queries this run)...")

        # Process queries in parallel (but capped by self.google_client.calls_in_run)
        with ThreadPoolExecutor(max_workers=8) as executor:
            # Pass force_no_cache down to the client
            future_to_query = {executor.submit(self.google_client.search, q['query'], force_no_cache=force_no_cache): q for q in queries}
            
            for future in as_completed(future_to_query):
                q_obj = future_to_query[future]
                q_text = q_obj['query']
                q_sector = q_obj['sector']
                
                if on_progress:
                    on_progress(q_sector, q_text)
                    
                try:
                    raw_results = future.result()
                    if not raw_results:
                        continue
                        
                    found_in_query = 0
                    processed_events = self.processor.process_results(raw_results, q_sector)
                    
                    for event in processed_events:
                        if self.deduplicator.process_event(event):
                            if self.storage.add_event(event):
                                found_in_query += 1
                                logger.info(f"✨ Elite Discovery: {event.get('event_name')} | confidence: {event.get('confidence')}%")
                                if should_alert(event):
                                    send_alert(event)
                    total_events += found_in_query
                except Exception as e:
                    logger.error(f"Search worker failed: {e}")

        return total_events

if __name__ == "__main__":
    p = EventDiscoveryPipeline()
    p.run()
