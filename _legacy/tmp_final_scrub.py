
import json
import os

filepath = os.path.join("data", "events.json")

if os.path.exists(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Final aggressive purge: 
    # 1. No "example.com"
    # 2. No "No event found" style names
    # 3. No "N/A" URLs (already done but safe)
    # 4. Filter for high quality: title must look like a real name
    
    original_count = len(data)
    
    # Helper to check if title is a junk phrase
    bad_sentinel_phrases = ["no event", "no award", "no info", "not found", "example", "hosts up ai"]
    
    data = [e for e in data if not any(phrase in e.get('event_name', '').lower() for phrase in bad_sentinel_phrases)]
    data = [e for e in data if 'example.com' not in e.get('source_url', '')]
    data = [e for e in data if e.get('source_url', '') != 'N/A']
    
    removed_count = original_count - len(data)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"Final Data Scrub Complete. Removed {removed_count} items. {len(data)} high-quality items remain.")
else:
    print("File not found.")
