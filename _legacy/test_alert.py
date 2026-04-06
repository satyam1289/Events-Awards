
import json
import os
from datetime import datetime, timedelta

filepath = r"c:\Users\DEll\OneDrive\Desktop\events 1\data\events.json"

new_event = {
    "event_name": "Antigravity AI Tech Summit 2026",
    "sector": "Artificial Intelligence",
    "type": "Event",
    "date": "December 10-12, 2026",
    "location": "Mumbai",
    "source_title": "Antigravity Official",
    "source_url": "https://antigravity.ai/events/summit-2026",
    "confidence": 100,
    "scraped_at": datetime.now().isoformat() # Now!
}

if os.path.exists(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except:
            data = []
else:
    data = []

data.append(new_event)

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Triggered alert for: {new_event['event_name']}")
