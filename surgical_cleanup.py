import sqlite3
import os

def final_surgical_cleanup():
    db_path = os.path.join(r'c:\Users\DEll\OneDrive\Desktop\E&A\events 1', 'data', 'events.db')
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Precise deletion based on subagent findings and my verification
    targets = [
        "Frequently Asked Questions", "Entry Criteria", "Deadlines", 
        "About Summit", "Rules and Regulations", "Entry Submission",
        "Call for entries", "Music Biz 2026 Call For Presentations",
        "Speaker Requests", "Awards nominations", "Become a speaker at ad",
        "Calls & events planned for H1", "Bharatiya Business Awards 2026 Announced",
        "MSEDCL gets national recognition", "Indian Commercial Vehicle Industry",
        "Upcoming Marketing & Advertising Awards", "in the L&D industry",
        "Bfsi", "Awards", "India", "Technology", "Startup"
    ]
    
    deleted_count = 0
    
    # 1. Exact string matches
    for t in targets:
        cursor.execute("DELETE FROM events WHERE event_name = ?", (t,))
        deleted_count += cursor.rowcount
        
    # 2. Like matches for common news formats
    news_patterns = [
        "%gets national recognition%", "%hits new high%", "%Announced%", 
        "http%", "www.%", "%criteria%", "%regulations%", "%Speaker Requests%",
        "%Call for presentation%", "%Call for entries%", "%Call for nominations%"
    ]
    for p in news_patterns:
        cursor.execute("DELETE FROM events WHERE event_name LIKE ?", (p,))
        deleted_count += cursor.rowcount

    # 3. Final length check (remove single-word names)
    cursor.execute("SELECT id, event_name FROM events")
    rows = cursor.fetchall()
    for rid, name in rows:
        if name and len(str(name).split()) < 2:
            cursor.execute("DELETE FROM events WHERE id = ?", (rid,))
            deleted_count += 1

    conn.commit()
    conn.close()
    print(f"Surgical cleanup complete. Removed {deleted_count} inaccurate items.")

if __name__ == "__main__":
    final_surgical_cleanup()
