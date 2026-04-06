import sqlite3
import re

def purge_low_relevance():
    conn = sqlite3.connect('data/events.db')
    cursor = conn.cursor()
    
    # 1. Delete events that don't mention a year in their name (for 2025-2027)
    # This ensures we don't have generic "About us" or "Contact" pages
    cursor.execute("""
        DELETE FROM events 
        WHERE event_name NOT LIKE '%202%' 
        AND confidence < 70
    """)
    deleted = cursor.rowcount
    
    # 2. Delete events with news/stock noise in title
    noise = ['stock', 'shares', 'pvt ltd', 'results', 'profit']
    for n in noise:
        cursor.execute("DELETE FROM events WHERE event_name LIKE ?", (f'%{n}%',))
        deleted += cursor.rowcount
        
    conn.commit()
    conn.close()
    print(f"Purged {deleted} low-relevance items from database.")

if __name__ == "__main__":
    purge_low_relevance()
