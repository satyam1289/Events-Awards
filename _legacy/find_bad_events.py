import json
import os

filepath = os.path.join("data", "events.json")

if not os.path.exists(filepath):
    print(f"File not found: {filepath}")
    exit(1)

with open(filepath, 'r', encoding='utf-8') as f:
    try:
        data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        # Try to fix truncated JSON if possible
        f.seek(0)
        content = f.read()
        if not content.strip().endswith(']'):
            content += ']'
        try:
            data = json.loads(content)
        except:
             # Last resort: find last valid object
             print("JSON is too broken for direct loads. Trying regex...")
             import re
             objects = re.findall(r'\{[^{}]+\}', content)
             data = [json.loads(obj) for obj in objects if '"event_name"' in obj]

targets = ["Event", "Of the Most", "BREAKING: Toxic: A fair", "Of the Silver"]

for i, item in enumerate(data):
    name = item.get('event_name', '')
    if any(t in name for t in targets) or name == "Event":
        print(f"Index {i}: {item}")
