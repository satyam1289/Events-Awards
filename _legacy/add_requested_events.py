
import json
import os
from datetime import datetime

filepath = r"c:\Users\DEll\OneDrive\Desktop\events 1\data\events.json"

new_events = [
    {
        "event_name": "India Global Education Summit (IGES) 2026",
        "sector": "Education",
        "date": "January 28-29, 2026",
        "location": "Chennai",
        "source_title": "The Hindu BusinessLine",
        "source_url": "https://www.thehindubusinessline.com/news/tn-govt-to-host-india-global-education-summit-iges-in-chennaion-jan-28-29/article70551980.ece",
        "confidence": 95,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "event_name": "15th East Himalayan Trade Fair & 2nd East Himalayan Agri Expo",
        "sector": "Agriculture",
        "date": "January 22-28, 2026",
        "location": "Guwahati",
        "source_title": "NE India Broadcast",
        "source_url": "https://neindiabroadcast.com/2026/01/22/15th-east-himalayan-trade-fair-2nd-east-himalayan-agri-expo-to-be-held-in-guwahati-from-january-22-28/",
        "confidence": 95,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "event_name": "Guwahati Asian Film Festival (GAFF) 2026",
        "sector": "Entertainment",
        "date": "January 22-25, 2026",
        "location": "Jyoti Chitraban, Guwahati",
        "source_title": "The News Mill",
        "source_url": "https://thenewsmill.com/2026/01/4-day-guwahati-asian-film-festival-gaff-2026-opens-on-january-22-at-jyoti-chitraban/",
        "confidence": 95,
        "scraped_at": datetime.now().isoformat()
    }
]

if os.path.exists(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except:
            data = []
else:
    data = []

# Update existing if URL matches, or append
for new_event in new_events:
    found = False
    for i, item in enumerate(data):
        if item.get('source_url') == new_event['source_url']:
            data[i] = new_event
            found = True
            break
    if not found:
        data.append(new_event)

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Successfully added/updated {len(new_events)} events.")
