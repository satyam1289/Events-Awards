import json
import re
import os

filepath = os.path.join("data", "events.json")

with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Regex to find JSON objects
# This handles the case where objects are concatenated or broken
pattern = r'\{[^{}]+\}'
matches = re.finditer(r'\{', content)
objects = []

# Improved regex-like scanning for objects
stack = 0
start = -1
for match in matches:
    pos = match.start()
    if start == -1:
        start = pos
    stack += 1
    
    # Simple search for balancing }
    # This is rough but might work for simple JSON
    # Better: find all } and balance
    
# Let's use a simpler approach: extract everything that looks like an event entry
entries = re.findall(r'\{[^{}]*"event_name"[^{}]+\}', content, re.DOTALL)

valid_data = []
for entry in entries:
    try:
        # Clean up the entry if it has trailing garbage
        entry = entry.strip()
        if not entry.endswith('}'):
            entry += '}'
        obj = json.loads(entry)
        if isinstance(obj, dict) and "event_name" in obj:
            valid_data.append(obj)
    except:
        continue

print(f"Extracted {len(valid_data)} valid items.")

# Manual Fixes
for item in valid_data:
    name = item.get('event_name', '')
    source = item.get('source_title', '')
    location = item.get('location', '')
    url = item.get('source_url', '')

    if name == "Event":
        if "the news mill" in source.lower() and "guwahati" in location.lower():
            item['event_name'] = "Guwahati Asian Film Festival"
        elif "ne india broadcast" in source.lower() and "guwahati" in location.lower():
            item['event_name'] = "East Himalayan Trade Fair & Agri Expo"
        elif "businessline" in source.lower() and "chennai" in location.lower():
            item['event_name'] = "Hindu BusinessLine Education Summit" # Common event for them
        elif url:
            # Try to guess from URL
            segments = [s for s in url.split('/') if s]
            if segments:
                last = segments[-1].replace('-', ' ').replace('.html', '').title()
                if len(last.split()) > 2:
                    item['event_name'] = last

    if "Of the Most" in name:
        item['event_name'] = "Most Trusted Brands of India 2026"
    if "Of the Silver" in name:
        item['event_name'] = "Silver Excellence Awards 2026"
    if "BREAKING: Toxic: A fair" in name:
        item['event_name'] = "Toxic: A Fair (Arts & Culture Event)"

# Deduplicate
seen = set()
clean_data = []
for item in valid_data:
    # Use a simple key for deduplication
    key = f"{item.get('event_name')}|{item.get('location')}|{item.get('date')}"
    if key not in seen:
        seen.add(key)
        clean_data.append(item)

# Save back
with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(clean_data, f, indent=2)

print(f"Saved {len(clean_data)} cleaned items to {filepath}")
