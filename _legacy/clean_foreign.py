
import json
import os
import config

events_file = 'data/events.json'
if os.path.exists(events_file):
    with open(events_file, 'r', encoding='utf-8') as f:
        events = json.load(f)
    
    original_count = len(events)
    
    cleaned_events = []
    for e in events:
        text_lower = ""
        # Create text block from multiple fields for extensive check check
        name = e.get('event_name', '').lower()
        location = e.get('location', '').lower()
        text_lower = f"{name} {location} india" # By default treat existing ones leniently unless obviously foreign

        # Still, if they explicitly mention a foreign indicator, test further
        has_india_city = any(city.lower() in location for city in config.CITIES) 
        has_foreign = any(fi in location for fi in config.FOREIGN_INDICATORS)
        
        # Geofence strict check for cleanup
        if has_foreign and not has_india_city and "india" not in location:
            print(f"Bouncing foreign event: {e.get('event_name')} - {e.get('location')}")
            continue
            
        cleaned_events.append(e)
    
    if original_count != len(cleaned_events):
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_events, f, indent=2)
        print(f"Cleaned {original_count - len(cleaned_events)} foreign entries from events.json")
    else:
        print("No foreign entries found to clean.")
else:
    print("Storage file not found.")
