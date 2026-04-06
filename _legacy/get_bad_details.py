import json

import os
filepath = os.path.join("data", "events.json")

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Targets to fix
targets = ["Event", "Of the Most", "Of the Silver", "BREAKING: Toxic: A fair"]

found = []
for item in data:
    if item.get('event_name') in targets or any(t in item.get('event_name', '') for t in ["Of the Most", "Of the Silver"]):
        found.append(item)

print(json.dumps(found, indent=2))
