import argparse
import sys
import logging
import threading
import time
from datetime import datetime

import config
from main import EventDiscoveryPipeline
from storage import EventStorage
from app import run_dashboard
from google_search_client import GoogleSearchClient

logger = logging.getLogger(__name__)

def run_tier_loop(tier, schedule_times):
    pipeline = EventDiscoveryPipeline()
    client = GoogleSearchClient()
    
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        if current_time in schedule_times:
            quota = client.get_quota_info()
            if quota.get('quota_exhausted') or quota.get('daily_count', 0) >= config.MAX_DAILY_QUERIES:
                logger.warning(f"Quota limit reached, skipping Tier {tier} run")
            else:
                logger.info(f"--- Triggering scheduled Tier {tier} run at {current_time} ---")
                pipeline.run(tier=tier)
                
            time.sleep(61)
        else:
            time.sleep(30)

def main():
    parser = argparse.ArgumentParser(description='Event & Award Discovery Engine v4.0 CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    discover_parser = subparsers.add_parser('discover', help='Run all tiers once immediately')
    discover_parser.add_argument('--tier', type=int, choices=[1, 2, 3], help='Run only a specific Tier once')
    discover_parser.add_argument('--sector', type=str, help='Run only for a specific sector (e.g., Fintech, D2C, EV)')
    
    quota_parser = subparsers.add_parser('quota', help='Print today\'s quota usage')
    
    all_parser = subparsers.add_parser('all', help='Continuous scheduled mode')
    all_parser.add_argument('--live', action='store_true', help='Continuous scheduled mode')
    all_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    all_parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    
    dashboard_parser = subparsers.add_parser('dashboard', help='Run the web dashboard')
    dashboard_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    dashboard_parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    
    list_parser = subparsers.add_parser('list')
    scrape_parser = subparsers.add_parser('scrape')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return

    if args.command == 'discover':
        pipeline = EventDiscoveryPipeline()
        count = pipeline.run(tier=args.tier, sector=args.sector)
        logger.info(f"Discovery complete. Found {count} new events.")
        
    elif args.command == 'dashboard':
        logger.info(f"Starting dashboard on {args.host}:{args.port}")
        run_dashboard(host=args.host, port=args.port)
        
    elif args.command == 'quota':
        client = GoogleSearchClient()
        quota = client.get_quota_info()
        print(f"\n=== Quota Usage ===")
        print(f"Date (UTC): {quota.get('date')}")
        print(f"Queries Used: {quota.get('daily_count', 0)} / {config.MAX_DAILY_QUERIES}")
        print(f"Exhausted: {quota.get('quota_exhausted', False)}")
        
    elif args.command == 'all':
        if args.live:
            t1_times = [f"{str(h).zfill(2)}:00" for h in range(7, 23, 2)]
            t2_times = ["08:00", "14:00", "20:00"]
            t3_times = ["06:00"]
            
            t1_thread = threading.Thread(target=run_tier_loop, args=(1, t1_times), daemon=True)
            t2_thread = threading.Thread(target=run_tier_loop, args=(2, t2_times), daemon=True)
            t3_thread = threading.Thread(target=run_tier_loop, args=(3, t3_times), daemon=True)
            
            t1_thread.start()
            t2_thread.start()
            t3_thread.start()
            
            logger.info("3-Tier Scheduler started. Tiers will run at their scheduled times.")
            logger.info(f"Dashboard starting at http://{args.host}:{args.port}")
            run_dashboard(host=args.host, port=args.port)
        else:
            run_dashboard(host=args.host, port=args.port)

    elif args.command == 'list':
        storage = EventStorage()
        events = storage.get_all_events()
        print(f"\nTotal events: {len(events)}")

if __name__ == '__main__':
    main()
