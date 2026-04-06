import sqlite3
import dateparser
from datetime import datetime
import json
import os

DB_FILE = 'data/events.db'
JSON_FILE = 'data/events.json'

def update_existing_dates():
    if not os.path.exists(DB_FILE):
        return
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, date FROM events")
    rows = cursor.fetchall()
    
    updated = 0
    for row_id, old_date in rows:
        if old_date and '/' not in old_date:
            parsed = dateparser.parse(old_date)
            if parsed:
                new_date = parsed.strftime("%d/%m/%Y")
                cursor.execute("UPDATE events SET date = ? WHERE id = ?", (new_date, row_id))
                updated += 1
                
    conn.commit()
    conn.close()
    print(f"Updated {updated} events in SQLite.")

    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as f:
            events = json.load(f)
            
        json_updated = 0
        for event in events:
            old_date = event.get('date')
            if old_date and '/' not in old_date:
                parsed = dateparser.parse(old_date)
                if parsed:
                    event['date'] = parsed.strftime("%d/%m/%Y")
                    json_updated += 1
        
        with open(JSON_FILE, 'w') as f:
            json.dump(events, f, indent=4)
        print(f"Updated {json_updated} events in JSON.")

if __name__ == "__main__":
    update_existing_dates()
