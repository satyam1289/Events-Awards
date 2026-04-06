import sqlite3
import re
import os
import sys

# Add project dir to path
sys.path.append(r'c:\Users\DEll\OneDrive\Desktop\E&A\events 1')
import config

def clean_name(title):
    if not title: return ""
    t = str(title)
    # Remove pipes and dashes at the end
    for char in ['|', '-', '—', ':']:
        if char in t:
            t = t.split(char)[0].strip()
    return t

def sanitize_database():
    db_path = os.path.join(r'c:\Users\DEll\OneDrive\Desktop\E&A\events 1', 'data', 'events.db')
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Cleanup: Removing inaccurate results and cleaning names...")
    cursor.execute("SELECT id, event_name FROM events")
    rows = cursor.fetchall()
    
    deleted = 0
    updated = 0
    
    for rid, name in rows:
        n_str = str(name or "")
        n_lower = n_str.lower()
        
        # 1. DELETE if negative intent
        is_bad = any(neg in n_lower for neg in config.NEGATIVE_INTENT_SIGNALS)
        is_generic = n_lower in ["event", "conference", "summit", "awards"]
        is_too_short = len(n_str.split()) < 2
        
        if is_bad or is_generic or is_too_short:
            cursor.execute("DELETE FROM events WHERE id=?", (rid,))
            deleted += 1
            continue
            
        # 2. UPDATE name
        cleaned = clean_name(n_str)
        if cleaned != n_str:
            cursor.execute("UPDATE events SET event_name=? WHERE id=?", (cleaned, rid))
            updated += 1
            
    conn.commit()
    conn.close()
    print(f"Finished. Deleted: {deleted}, Cleaned: {updated}")

if __name__ == "__main__":
    sanitize_database()
