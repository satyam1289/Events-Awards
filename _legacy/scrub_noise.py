
import json
import os

filepath = r"c:\Users\DEll\OneDrive\Desktop\events 1\data\events.json"

bad_phrases = [
    'unknown', 'not specified', 'no specific event', 'no event identified', 
    'no event found', 'no core event', 'generic event', 'none', 'n/a', 'tbd', 
    'to be announced', 'no specific', 'not applicable', 'no information'
]

if os.path.exists(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            events = json.load(f)
        except:
            events = []
    
    initial_count = len(events)
    # Filter out events with bad names
    cleaned_events = []
    for event in events:
        name = event.get('event_name', '').lower()
        if not any(bad in name for bad in bad_phrases) and len(name) >= 3:
            cleaned_events.append(event)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(cleaned_events, f, indent=2)
    
    removed = initial_count - len(cleaned_events)
    print(f"Scrubbing complete. Removed {removed} noisy/bad entries.")
    print(f"Total valid events remaining: {len(cleaned_events)}")
else:
    print("Events file not found.")
