
import json
import os

events_file = 'data/events.json'
if os.path.exists(events_file):
    with open(events_file, 'r', encoding='utf-8') as f:
        events = json.load(f)
    
    bad_names = [
        'no event', 'not applicable', 'none', 'n/a', 'unknown', 
        'no specific', 'not specified', 'generic event', 'tbd', 
        'no core event', 'no information', 'null', 'no event found',
        'breaking news', 'exclusive report', 'latest update'
    ]
    
    original_count = len(events)
    # Filter out events where name is generic OR shorter than 4 chars
    cleaned_events = [
        e for e in events 
        if e.get('event_name') and not any(bn in e['event_name'].lower() for bn in bad_names) and len(e['event_name']) >= 4
    ]
    
    if original_count != len(cleaned_events):
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_events, f, indent=2)
        print(f"Cleaned {original_count - len(cleaned_events)} garbage entries from events.json")
    else:
        print("No garbage entries found to clean.")
else:
    print("Storage file not found.")
