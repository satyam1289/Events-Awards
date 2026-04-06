import sqlite3
import re
from extractor import EventExtractor

def cleanup_db_names():
    extractor = EventExtractor()
    conn = sqlite3.connect('data/events.db')
    cursor = conn.cursor()
    
    # We need the source title/link context if possible, but extract_name only needs title
    cursor.execute("SELECT id, event_name, source_title FROM events")
    rows = cursor.fetchall()
    
    updated = 0
    for row_id, old_name, source_title in rows:
        # Use our new logic to clean it up
        new_name = extractor.extract_name(old_name)
        
        if new_name != old_name:
            cursor.execute("UPDATE events SET event_name = ? WHERE id = ?", (new_name, row_id))
            updated += 1
            
    conn.commit()
    conn.close()
    print(f"Cleaned up {updated} event names in Database.")

if __name__ == "__main__":
    cleanup_db_names()
