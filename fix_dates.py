import json
import os
import re
import dateparser
from datetime import datetime

EVENTS_FILE = r'C:\Users\MAVERICKS\Desktop\events 1\data\events.json'

def fix_dates():
    if not os.path.exists(EVENTS_FILE):
        print("Events file not found.")
        return

    with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
        events = json.load(f)

    fixed_count = 0
    current_year = datetime.now().year

    for event in events:
        old_date = str(event.get('date', ''))
        event_name = str(event.get('event_name', ''))
        
        # Clean up weird spaces like "2 0 2 6"
        old_date = re.sub(r'(\d)\s+(\d)\s+(\d)\s+(\d)', r'\1\2\3\4', old_date)
        
        if old_date and old_date != 'TBD' and '/' not in old_date:
            # Try to combine with name if date looks incomplete (e.g., "27 2026")
            text_to_parse = old_date
            if len(old_date.split()) < 3 and any(m in event_name for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                text_to_parse = f"{old_date} {event_name}"
            
            parsed = dateparser.parse(text_to_parse, settings={'PREFER_DATES_FROM': 'future', 'REQUIRE_PARTS': ['month']})
            if parsed:
                new_date = parsed.strftime("%d/%m/%Y")
                event['date'] = new_date
                fixed_count += 1
            else:
                # Last ditch: if it's "DD YYYY", assume March (current discovery month)
                match = re.search(r'^(\d{1,2})\s+(\d{4})$', old_date)
                if match:
                    event['date'] = f"{match.group(1).zfill(2)}/03/{match.group(2)}"
                    fixed_count += 1

    if fixed_count > 0:
        with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=4)
        print(f"Fixed {fixed_count} event dates.")
    else:
        print("No dates needed fixing (or couldn't parse them).")

if __name__ == "__main__":
    fix_dates()
    
