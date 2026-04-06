import sqlite3

def clean_news_events():
    conn = sqlite3.connect('data/events.db')
    cursor = conn.cursor()
    
    # Check current counts
    cursor.execute("SELECT count(*) FROM events WHERE source_title = 'news.google.com'")
    count = cursor.fetchone()[0]
    print(f"Found {count} events from Google News RSS.")
    
    # Delete them
    cursor.execute("DELETE FROM events WHERE source_title = 'news.google.com'")
    conn.commit()
    print(f"Deleted {count} events.")
    
    # Also delete anything that might be 'free_scrape'
    cursor.execute("DELETE FROM events WHERE source_url LIKE '%10times.com%' OR source_url LIKE '%nasscom.in%'")
    print(f"Deleted {conn.total_changes - count} other free source events.")
    conn.commit()
    
    conn.close()

if __name__ == "__main__":
    clean_news_events()
