import sqlite3

def update_nominations_status():
    conn = sqlite3.connect('data/events.db')
    cursor = conn.cursor()
    
    # Update Awards that have 'nominat' or 'apply' in their name but don't have deadline Set
    cursor.execute("""
        UPDATE events 
        SET status = 'NOMINATIONS_OPEN', nomination_deadline = 'Open'
        WHERE event_type = 'Awards' 
        AND status = 'UPCOMING'
        AND (event_name LIKE '%nominat%' OR event_name LIKE '%apply%')
    """)
    
    conn.commit()
    conn.close()
    print("Nominations status update complete.")

if __name__ == "__main__":
    update_nominations_status()
